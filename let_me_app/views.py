from xml.dom import minidom
from itertools import groupby

from collections import OrderedDict
from django import http
from django import forms as django_forms
from django.contrib.auth.models import Group
from django.contrib.gis.measure import D
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic.base import View as BaseView, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import BaseUpdateView
from django.views.generic.list import ListView

from extra_views import CreateWithInlinesView, InlineFormSet
from extra_views.generic import GenericInlineFormSet

from let_me_app import persistence, forms, models
from django.db import transaction
from let_me_app.models import VisitStatuses
from let_me_auth.models import User
import itertools



class OccasionInline(InlineFormSet):
    model = models.Occasion


class BookingPolicyInline(GenericInlineFormSet):
    model = models.BookingPolicy


class CreateCourtView(CreateWithInlinesView):
    model = models.Court
    inlines = [BookingPolicyInline, OccasionInline]


class ChatList(ListView):
    template_name = 'chat/list.html'
    model = models.ChatParticipant

    def get_queryset(self, **kwargs):
        query = super(ChatList, self).get_queryset(**kwargs)
        query = query.filter(user=self.request.user)
        query = query.select_related(
            'chat', 'chat__subject__event', 'user'
        )
        query = query.order_by('-chat__last_update')
        return query


class ChatDetails(DetailView):
    template_name = 'chat/details.html'
    model = models.InternalMessage

    def get_queryset(self, **kwargs):
        query = super(ChatDetails, self).get_queryset(**kwargs)
        query = query.prefetch_related('chatparticipant_set__user')
        return query

    def get_context_data(self, *args, **kwargs):
        result = super(ChatDetails, self).get_context_data(*args, **kwargs)

        for participant in result['object'].chatparticipant_set.all():
            if participant.user == self.request.user:
                participant.save()

        result['message_form'] = forms.ChatMessageForm()
        return result


class PostChatMessage(BaseUpdateView):
    model = models.InternalMessage
    form_class = forms.ChatMessageForm

    def get(self, *args, **kwargs):
        return http.HttpResponseRedirect(
            reverse('let_me_app:chat_details', kwargs={'pk': kwargs['pk']})
        )

    def get_form_kwargs(self):
        result = super(PostChatMessage, self).get_form_kwargs()
        result.pop('instance')
        return result

    def form_valid(self, form):
        doc = minidom.Document()
        message = doc.createElement('message')

        text_node = message.appendChild(doc.createElement('text'))
        text_node.appendChild(doc.createTextNode(form.cleaned_data['message']))
        author_node = message.appendChild(doc.createElement('author'))
        author_node.appendChild(doc.createTextNode(str(self.request.user.id)))
        date_node = message.appendChild(doc.createElement('date'))
        date_node.appendChild(doc.createTextNode(str(timezone.now())))

        self.object.text = message.toxml() + models.CF('text')
        self.object.save()

        return http.HttpResponseRedirect(
            reverse('let_me_app:chat_details', kwargs={'pk': self.object.id})
        )

    def form_invalid(self, form):
        return http.HttpResponseRedirect(
            reverse('let_me_app:chat_details', kwargs={'pk': kwargs['pk']})
        )


class EventView(DetailView):
    template_name = 'events/details.html'
    model = models.Event

    def get_queryset(self):
        queryset = super(EventView, self).get_queryset()
        queryset = queryset.select_related(
            'inventory_list', 'court', 'court__site', 'court__activity_type')
        queryset = queryset.prefetch_related('inventory_list__inventory_set')
        return queryset

    def _get_user_inventory(self, event, visits):
        user_inventory = models.Inventory.objects.filter(
            inventory_list__visit__event=event,
            inventory_list__visit__status=models.VisitStatuses.PENDING)
        user_inventory = user_inventory.select_related('equipment')
        user_inventory = user_inventory.values('equipment__name', 'amount', 'inventory_list_id')
        inventory_lists = {i.inventory_list_id: i.user for i in visits}
        for inventory in user_inventory:
            inventory['user'] = inventory_lists[inventory['inventory_list_id']]
        return user_inventory

    def _get_coach_recommendation(self, visit):
        recommendation = models.CoachRecommendation.objects.filter(visit=visit)
        recommendation = recommendation.select_related('coach__user')[:1]
        if recommendation:
            return recommendation[0]

    def _get_visit_indexes(self, visit):
        indexes = models.VisitIndex.objects.filter(visit=visit)
        return indexes.values('parametr__name', 'parametr__units', 'value')

    def get_context_data(self, **kwargs):
        result = super(EventView, self).get_context_data(**kwargs)
        event = result['object']
        is_admin = event.court.admin_group.user_set.filter(
            email=self.request.user.email).exists()
        result['is_admin'] = is_admin
        result['proposal_form'] = forms.EventProposalForm()
        result['visit_form'] = forms.EventVisitForm()
        result['inventory_form'] = forms.InventoryForm()
        result['active_applications'] = event.application_set.filter(
            status=models.ApplicationStatuses.ACTIVE
        ).select_related('user').order_by('id')

        result['staff_list'] = event.eventstaff_set.all()
        result['is_event_staff'] = self.request.user.id in [i.staff_id for i in result['staff_list']]

        result['active_visits'] = event.visit_set.select_related('user').order_by('id')
        result['active_proposals'] = event.proposal_set.all().select_related('user').order_by('id')
        result['user_inventory'] = self._get_user_inventory(
            event, result['active_visits'])

        for prop in result['active_proposals']:
            if (prop.user == self.request.user
                    and prop.status==models.ProposalStatuses.ACTIVE):
                result['my_active_proposal'] = prop


        my_active_applications = [
            i for i in result['active_applications'] if i.user == self.request.user
        ]
        if my_active_applications:
            result['my_active_application'] = my_active_applications[0]

        my_active_visits = [
            i for i in result['active_visits']
            if i.user == self.request.user and i.status in [models.VisitStatuses.PENDING, models.VisitStatuses.COMPLETED]
        ]
        if my_active_visits:
            result['my_active_visit'] = my_active_visits[0]

            result['coach_recommendation'] = self._get_coach_recommendation(
                result['my_active_visit']
            )
            result['visit_indexes'] = self._get_visit_indexes(
                result['my_active_visit']
            )

        return result


class UserEventListView(ListView):
    model = models.Visit
    template_name = "events/user_events.html"

    def get_queryset(self, **kwargs):
        result = super(UserEventListView, self).get_queryset(**kwargs)
        return result.filter(
            user=self.request.user,
            event__start_at__gte=timezone.now()).order_by('-event__start_at')

    def get_context_data(self, **kwargs):
        result = super(UserEventListView, self).get_context_data(**kwargs)
        object_list = result['object_list']
        grouped_objects = groupby(object_list, lambda x: x.event.start_at.date())
        result['grouped_objects'] = [(i, [j for j in g]) for i, g in grouped_objects]
        return result


class UserProposalsListView(ListView):
    model = models.Proposal
    template_name = "events/user_proposals.html"

    def get_queryset(self, **kwargs):
        result = super(UserProposalsListView, self).get_queryset(**kwargs)
        return result.filter(
            user=self.request.user,
            event__start_at__gte=timezone.now()).order_by('-event__start_at')

    def get_context_data(self, **kwargs):
        result = super(UserProposalsListView, self).get_context_data(**kwargs)
        object_list = result['object_list']
        grouped_objects = groupby(object_list, lambda x: x.event.start_at.date())
        result['grouped_objects'] = [(i, [j for j in g]) for i, g in grouped_objects]
        return result


class UserManagedEventListView(ListView):
    model = models.Event
    template_name = "events/user_managed_events.html"

    def get_queryset(self, **kwargs):
        result = super(UserManagedEventListView, self).get_queryset(**kwargs)
        return result.filter(
            court__admin_group__user=self.request.user,
            start_at__gte=timezone.now()).order_by('-start_at')

class EventActionMixin(object):
    def get_success_url(self, **kwargs):
        if 'next' in self.request.GET:
            return self.request.GET.get('next')
        return reverse('let_me_app:view_event', kwargs={'pk': kwargs['event']})

    def get_queryset(self, request, *args, **kwargs):
        pass

    def process_object(self, obj):
        pass

    def check_permissions(self, request, *args, **kwargs):
        return True

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if not self.check_permissions(request, *args, **kwargs):
            return http.HttpResponseForbidden()

        query = self.get_queryset(request, *args, **kwargs)
        query = query.select_for_update()
        objects = query.all()
        if not objects:
            return http.HttpResponseNotFound()

        for obj in objects:
            self.process_object(obj)

        return http.HttpResponseRedirect(self.get_success_url(**kwargs))


class CancelApplicationView(EventActionMixin, BaseView):
    def get_queryset(self, request, *args, **kwargs):
        return models.Application.objects.filter(
            event_id=kwargs['event'],
            user=request.user,
            status=models.ApplicationStatuses.ACTIVE
        )

    def process_object(self, application):
        application.status = models.ApplicationStatuses.CANCELED
        application.save()


class CreateApplicationView(BaseView):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if request.user.is_anonymous():
            return http.HttpResponseForbidden()

        events = models.Event.objects.filter(id=kwargs['event'])
        if not events:
            return http.HttpResponseNotFound()

        comment = request.POST['comment']
        application = models.Application.objects.create(
            event=events[0],
            user=request.user,
            status=models.ApplicationStatuses.ACTIVE,
            comment=comment
        )

        return http.HttpResponseRedirect(
            reverse('let_me_app:view_event', kwargs={'pk': kwargs['event']})
        )


class DetailRelatedPostView(BaseView):
    model = models.Event

    def get_form(self):
        pass

    def action_is_allowed(self, event):
        pass

    def save_on_success(self, event, form):
        pass

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if request.user.is_anonymous():
            return http.HttpResponseForbidden()

        obj = get_object_or_404(self.model, id=kwargs['pk'])

        if not self.action_is_allowed(obj):
            return http.HttpResponseForbidden()

        form = self.get_form()

        if form.is_valid():
            self.save_on_success(obj, form)

        return http.HttpResponseRedirect(self.get_success_url(obj))

    def get_success_url(self, obj):
        return reverse('let_me_app:view_event', kwargs={'pk': obj.id})

class CreateProposalView(DetailRelatedPostView):
    def get_form(self):
        return forms.EventProposalForm(data=self.request.POST)

    def action_is_allowed(self, event):
        return event.court.admin_group.user_set.filter(
            id=self.request.user.id).exists()

    def save_on_success(self, event, form):
        comment = form.cleaned_data['comment']
        for user in form.cleaned_data['users']:
            models.Proposal.objects.get_or_create(
                event=event, user=user,
                status=models.ApplicationStatuses.ACTIVE,
                defaults={'comment':comment}
            )


class AddEventInventoryView(DetailRelatedPostView):
    def get_form(self):
        return forms.InventoryForm(data=self.request.POST)

    def action_is_allowed(self, event):
        return event.court.admin_group.user_set.filter(
            id=self.request.user.id).exists()

    def save_on_success(self, event, form):
        if not event.inventory_list:
            inventory_list = models.InventoryList.objects.create(name=event.name)
            event.inventory_list = inventory_list
            event.save()
        inventory = form.save(commit=False)
        inventory.inventory_list = event.inventory_list
        inventory.save()


class AddApplicationInventoryView(DetailRelatedPostView):
    model = models.Application

    def get_form(self):
        return forms.InventoryForm(data=self.request.POST)

    def action_is_allowed(self, application):
        return application.user_id == self.request.user.id

    def save_on_success(self, application, form):
        if not application.inventory_list:
            inventory_list = models.InventoryList.objects.create(
                name=application.event.name)
            application.inventory_list = inventory_list
            application.save()
        inventory = form.save(commit=False)
        inventory.inventory_list = application.inventory_list
        inventory.save()

    def get_success_url(self, obj):
        return reverse('let_me_app:view_event', kwargs={'pk': obj.event.id})


class AddVisitInventoryView(DetailRelatedPostView):
    model = models.Visit

    def get_form(self):
        return forms.InventoryForm(data=self.request.POST)

    def action_is_allowed(self, visit):
        return visit.user_id == self.request.user.id

    def save_on_success(self, visit, form):
        if not visit.inventory_list:
            inventory_list = models.InventoryList.objects.create(
                name=visit.event.name)
            visit.inventory_list = inventory_list
            visit.save()
        inventory = form.save(commit=False)
        inventory.inventory_list = visit.inventory_list
        inventory.save()

    def get_success_url(self, obj):
        return reverse('let_me_app:view_event', kwargs={'pk': obj.event.id})


class CreateVisitView(DetailRelatedPostView):
    def get_form(self):
        return forms.EventVisitForm(data=self.request.POST)

    def action_is_allowed(self, event):
        return event.court.admin_group.user_set.filter(
            id=self.request.user.id).exists()

    def save_on_success(self, event, form):
        for user in form.cleaned_data['users']:
            persistence.create_event_visit(event, user, None)


class DeclineProposalEventView(EventActionMixin, BaseView):
    def get_queryset(self, request, *args, **kwargs):
        return models.Proposal.objects.filter(
            event_id=kwargs['event'],
            user=request.user,
            status=models.ProposalStatuses.ACTIVE
        )

    def process_object(self, proposal):
        proposal.status = models.ProposalStatuses.DECLINED
        proposal.save()


class AcceptProposalView(EventActionMixin, BaseView):
    def get_queryset(self, request, *args, **kwargs):
        return models.Proposal.objects.filter(
            event_id=kwargs['event'],
            user=request.user,
            status=models.ProposalStatuses.ACTIVE
        )

    def process_object(self, proposal):
        proposal.status = models.ProposalStatuses.ACCEPTED
        proposal.save()
        persistence.create_event_visit(proposal.event, proposal.user, None)


class DeclineApplicationEventView(EventActionMixin, BaseView):
    def check_permissions(self, request, *args, **kwargs):
        return Group.objects.filter(
            court__event=kwargs['event'], user=request.user).exists()

    def get_queryset(self, request, *args, **kwargs):
        return models.Application.objects.filter(
            event_id=kwargs['event'],
            user=request.user,
            status=models.ApplicationStatuses.ACTIVE
        )

    def process_object(self, application):
        application.status = models.ApplicationStatuses.DECLINED
        application.save()


class AcceptApplicationView(EventActionMixin, BaseView):
    def check_permissions(self, request, *args, **kwargs):
        return Group.objects.filter(
            court__event=kwargs['event'], user=request.user).exists()

    def get_queryset(self, request, *args, **kwargs):
        return models.Application.objects.filter(
            event_id=kwargs['event'],
            user_id=kwargs['user'],
            status=models.ApplicationStatuses.ACTIVE
        )

    def process_object(self, application):
        application.status = models.ApplicationStatuses.ACCEPTED
        application.save()
        inventory_list = persistence.clone_inventory_list(
            application.inventory_list
        )
        persistence.create_event_visit(
            application.event, application.user, inventory_list
        )


class CancelVisitView(EventActionMixin, BaseView):
    def get_queryset(self, request, *args, **kwargs):
        return models.Visit.objects.filter(
            event_id=kwargs['event'],
            user_id=self.request.user,
            status=models.VisitStatuses.PENDING
        )

    def process_object(self, application):
        application.status = models.VisitStatuses.CANCELED
        application.save()


class DismissVisitorEventView(EventActionMixin, BaseView):
    def get_queryset(self, request, *args, **kwargs):
        return models.Visit.objects.filter(
            event_id=kwargs['event'],
            user=kwargs['user'],
            status=models.VisitStatuses.PENDING
        )

    def process_object(self, visit):
        visit.status = models.VisitStatuses.DECLINED
        visit.save()


class CancelInventoryEventView(EventActionMixin, BaseView):
    def get_queryset(self, request, *args, **kwargs):
        return models.Inventory.objects.filter(
            id=kwargs['inventory'],
        )

    def process_object(self, inventory):
        inventory.delete()


class CancelProposalEventView(EventActionMixin, BaseView):
    def check_permissions(self, request, *args, **kwargs):
        return Group.objects.filter(
            court__event=kwargs['event'], user=request.user).exists()

    def get_queryset(self, request, *args, **kwargs):
        return models.Proposal.objects.filter(
            event_id=kwargs['event'],
            user=kwargs['user'],
            status=models.ProposalStatuses.ACTIVE
        )

    def process_object(self, proposal):
        proposal.status = models.ProposalStatuses.CANCELED
        proposal.save()


class CancelEventView(EventActionMixin, BaseView):
    def check_permissions(self, request, *args, **kwargs):
        return Group.objects.filter(
            court__event=kwargs['event'], user=request.user).exists()

    def get_queryset(self, request, *args, **kwargs):
        return models.Event.objects.filter(
            id=kwargs['event'], status=models.VisitStatuses.PENDING
        )

    def process_object(self, event):
        event.status = models.EventStatuses.CANCELED
        event.save()


class CourtDetailView(DetailView):
    template_name = 'courts/details.html'
    model = models.Court

    def get_context_data(self, **kwargs):
        result = super(CourtDetailView, self).get_context_data(**kwargs)
        court = result['object']
        is_admin = result['is_admin'] = court.admin_group.user_set.filter(
            email=self.request.user.email).exists() or self.request.user.is_staff

        result['is_admin'] = is_admin
        result['group_admin_form'] = forms.GroupAdminForm()
        return result


class SiteDetailView(DetailView):
    template_name = 'sites/details.html'
    model = models.Site

    def get_context_data(self, **kwargs):
        result = super(SiteDetailView, self).get_context_data(**kwargs)
        is_admin = self.request.user.is_staff

        result['site_actions'] = []#persistence.get_court_actions_for_user(
#            self.request.user, court, is_admin=is_admin)
        result['is_admin'] = is_admin
        return result


class EventSearchView(ListView):
    template_name = 'events/search.html'
    model = models.Event

    def get_queryset(self):
        queryset = super(EventSearchView, self).get_queryset()
        queryset = queryset.filter(start_at__gte=timezone.now())
        queryset = queryset.order_by('start_at')

        queryset = queryset.select_related(
            'inventory_list', 'court', 'court__site', 'court__activity_type')

        form = forms.EventSearchForm(
            data=self.request.GET
        )
        if form.is_valid():
            if form.cleaned_data['geo_point'] and form.cleaned_data['radius']:
                site_queryset = models.Site.objects.filter(
                    geo_point__distance_lt=(form.cleaned_data['geo_point'],
                                            D(m=form.cleaned_data['radius']))
                )
                queryset = queryset.filter(court__site__in=site_queryset)
            if form.cleaned_data['activity_type']:
                queryset = queryset.filter(
                    court__activity_type__in=form.cleaned_data['activity_type'])
            if form.cleaned_data['start_date']:
                queryset = queryset.filter(
                    start_at__gt=form.cleaned_data['start_date'])
            if form.cleaned_data['end_date']:
                queryset = queryset.filter(
                    start_at__lt=form.cleaned_data['end_date'])
        return queryset

    def get_context_data(self, **kwargs):
        result = super(EventSearchView, self).get_context_data(**kwargs)
        result['search_form'] = forms.EventSearchForm(data=self.request.GET)
        return result


class CourtActionMixin(EventActionMixin):
    def get_success_url(self, **kwargs):
        return reverse('let_me_app:view_court', kwargs={'pk': self.kwargs['court']})

    def get_queryset(self, request, *args, **kwargs):
        return models.Court.objects.filter(pk=kwargs['court'])

    def process_object(self, obj):
        pass

    def check_permissions(self, request, *args, **kwargs):
        return Group.objects.filter(
            court=self.kwargs['court'], user=request.user).exists() or self.request.user.is_staff


class RemoveFromAdminGroup(CourtActionMixin, BaseView):
    def get_queryset(self, request, *args, **kwargs):
        return models.Court.objects.filter(pk=kwargs['court'])

    def process_object(self, obj):
        obj.admin_group.user_set.remove(self.kwargs['user'])


class AddUserToAdminGroupView(BaseView):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if request.user.is_anonymous():
            return http.HttpResponseForbidden()

        courts = models.Court.objects.filter(id=kwargs['court'])
        if not courts:
            return http.HttpResponseNotFound()

        if not (courts[0].admin_group.user_set.filter(id=request.user.id).exists()
                or self.request.user.is_staff):
            return http.HttpResponseForbidden()

        form = forms.GroupAdminForm(data=request.POST)

        if form.is_valid():
            if form.cleaned_data['users']:
                courts[0].admin_group.user_set.add(*form.cleaned_data['users'])

        return http.HttpResponseRedirect(
            reverse('let_me_app:view_court', kwargs={'pk': kwargs['court']})
        )


class CreateEventView(TemplateView):
    template_name = 'events/create_new.html'

    def get_visitors_form(self, data, files, **kwargs):
        return forms.EventVisitForm(
            data=data, prefix='event', initial={'users': [self.request.user]}
        )

    def get_forms(self, data, files, **kwargs):
        data_forms = OrderedDict()
        for entity, form_class in [('site', forms.SiteForm), ('court', forms.CourtForm)]:
            if not entity in kwargs:
                kw = {'prefix': entity}
                if data:
                    kw['data'] = data
                    kw['files'] = files
                data_forms[entity] = form_class(**kw)
        data_forms['event'] = forms.EventForm(
            data=data, files=files, prefix='event')
        data_forms['visitors'] = self.get_visitors_form(data, files, **kwargs)
        return data_forms

    def get_instances(self, view_forms, **kwargs):
        instances = {'event': view_forms['event'].instance}
        for entity, model in (('site', models.Site), ('court', models.Court)):
            pk = kwargs.get(entity)
            if not pk:
                instances[entity] = view_forms[entity].instance
            else:
                instances[entity] = get_object_or_404(model, pk=pk)
        return instances

    def get_context_data(self, **kwargs):
        view_forms = kwargs.get('forms') or self.get_forms(None, None, **kwargs)
        return {'forms': view_forms}

    def check_permissions(self, request, court):
        return True

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if not self.check_permissions(request, context.get('court')):
            return http.HttpResponseForbidden()

        return self.render_to_response(context)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        view_forms = self.get_forms(request.POST, request.FILES, **kwargs)
        validation_result = True
        for form in view_forms.values():
            validation_result = validation_result and form.is_valid()
            if validation_result and isinstance(form, django_forms.ModelForm):
                form.save(commit=False)

        if not validation_result:
            return self.render_to_response(
                self.get_context_data(forms=view_forms, **kwargs))

        instances = self.get_instances(view_forms, **kwargs)

        if not self.check_permissions(request, instances['court']):
            return http.HttpResponseForbidden()

        instances['site'].save()
        instances['court'].site = instances['site']
        instances['court'].save()
        instances['court'].admin_group.user_set.add(request.user)
        instances['event'].court = instances['court']

        persistence.save_event_and_related_things(
            instances['event'], request.user, visitors=view_forms['visitors'].cleaned_data['users']
        )

        for form in view_forms.values():
            if isinstance(form, django_forms.ModelForm):
                form.save_m2m()

        return http.HttpResponseRedirect(
            reverse(
                'let_me_app:view_event', kwargs={'pk': instances['event'].id}
            )
        )


class CreateSiteEventView(CreateEventView):
    template_name = 'events/create_for_site.html'

    def get_context_data(self, **kwargs):
        context = super(CreateSiteEventView, self).get_context_data(**kwargs)
        context['site_object'] = get_object_or_404(models.Site, pk=kwargs['site'])
        return context


class CreateCourtEventView(CreateEventView):
    template_name = 'events/create_for_court.html'

    def check_permissions(self, request, court):
        return (court.admin_group.user_set.filter(id=request.user.id).exists()
            or self.request.user.is_staff)

    def get_context_data(self, **kwargs):
        context = super(CreateCourtEventView, self).get_context_data(**kwargs)
        context['court'] = get_object_or_404(models.Court, pk=kwargs['court'])
        return context


class CreateStaffView(TemplateView):
    template_name = 'events/create_staff.html'

    def get_context_data(self, **kwargs):
        event = get_object_or_404(models.Event, pk=kwargs['pk'])
        formset = forms.EventStaffFormSet(
                instance=event, data=kwargs.get('data'))
        result = {
            'event': event,
            'staff_formset': formset}

        return result

    def check_permissions(self, request, court):
        return (court.admin_group.user_set.filter(id=request.user.id).exists()
            or self.request.user.is_staff)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        context = self.get_context_data(data=request.POST, **kwargs)
        formset = context['staff_formset']
        if formset.is_valid():
            formset.save()
            return http.HttpResponseRedirect(
                reverse(
                    'let_me_app:view_event',
                    kwargs={'pk': context['event'].id}
                )
            )
        return self.render_to_response(context)


class IndexCharts(ListView):
    template_name = 'charts/visit_indexes.html'
    model = models.VisitIndex

    def get_queryset(self):
        user_id = int(self.kwargs['user_id'])
        queryset = super(IndexCharts, self).get_queryset()
        queryset = queryset.filter(visit__user_id=user_id)
        if self.request.user.id != user_id:
            queryset = queryset.filter(
                visit__event__eventstaff__staff__user=self.request.user)
        queryset = queryset.order_by('parametr', 'visit__event__start_at')
        queryset = queryset.values('parametr_id', 'parametr__name', 'value', 'visit__event__start_at')
        return queryset

    def get_context_data(self, **kwargs):
        context_data = super(IndexCharts, self).get_context_data(**kwargs)
        param_groups = itertools.groupby(
            context_data['object_list'], lambda x: (x['parametr_id'], x['parametr__name']))
        context_data['param_groups'] = [(i, list(j)) for i, j in param_groups]
        return context_data


class IndexRecommendations(ListView):
    template_name = 'charts/recommendations.html'
    model = models.CoachRecommendation

    def get_queryset(self):
        user_id = int(self.kwargs['user_id'])
        queryset = super(IndexRecommendations, self).get_queryset()
        queryset = queryset.filter(visit__user_id=user_id)
        if self.request.user.id != user_id:
            queryset = queryset.filter(
                visit__event__eventstaff__staff__user=self.request.user)
        queryset = queryset.order_by('status', '-visit__event__start_at')
        queryset = queryset.select_related('visit__event', 'coach__user')
        return queryset


class AnnotateVisitView(TemplateView):
    template_name = 'visits/annotate_visit.html'

    def get(self, request, *args, **kwargs):
        visit = get_object_or_404(models.Visit, pk=kwargs['visit_id'])
        kwargs['object'] = visit
        if not self.check_permissions(request, visit):
            return http.HttpResponseForbidden()
        return super(AnnotateVisitView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        result = super(AnnotateVisitView, self).get_context_data(**kwargs)
        result['visit'] = kwargs['object']

        if 'formsets' in kwargs:
            result['formsets'] = kwargs['formsets']
        else:
            result['formsets'] = self.get_formsets(result['visit'], None, None)
        return result

    def check_permissions(self, request, visit):
        query = models.EventStaff.objects.filter(
            event_id=visit.event_id, staff_id=request.user.id)
        return query.exists()

    def get_formsets(self, visit, data, files, **kwargs):
        data_forms = OrderedDict()
        data_forms['visit_indexes'] = forms.VisitIndexFormSet(
            instance=visit, data=data, files=files)
        data_forms['recommendation'] = forms.CoachRecommendationFormSet(
            instance=visit, data=data, files=files)
        return data_forms

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        visit = get_object_or_404(models.Visit, pk=kwargs['visit_id'])

        if not self.check_permissions(request, visit):
            return http.HttpResponseForbidden()

        view_formsets = self.get_formsets(
            visit, request.POST, request.FILES, **kwargs)

        validation_result = True
        for formset in view_formsets.values():
            validation_result = validation_result and formset.is_valid()

        if not validation_result:
            return self.render_to_response(
                self.get_context_data(
                    formsets=view_formsets, object=visit, **kwargs)
            )

        for key, formset in view_formsets.items():
            formset.save(commit=(key != 'recommendation'))

        for form in view_formsets['recommendation'].forms:
            form.instance.coach = request.user.staffprofile
            form.instance.save()

        return http.HttpResponseRedirect(
            reverse('let_me_app:view_event', kwargs={'pk': visit.event_id})
        )


class CloneEventView(TemplateView):
    template_name = 'events/clone_event.html'

    def get_context_data(self, **kwargs):
        view_forms = kwargs.get('forms') or self.get_forms(None, None, **kwargs)
        result = {'forms': view_forms}
        result['event'] = (kwargs.get('source_event') or
            get_object_or_404(models.Event, pk=kwargs['event']))
        return result

    def check_permissions(self, request, court):
        return (court.admin_group.user_set.filter(id=request.user.id).exists()
            or self.request.user.is_staff)

    def get_forms(self, data, files, **kwargs):
        data_forms = OrderedDict()
        data_forms['event'] = forms.EventForm(
            data=self.request.POST, files=self.request.FILES, prefix='event')
        data_forms['visitors'] = forms.EventVisitForm(
            data=data, prefix='event',
            initial={'users': User.objects.filter(visit__event=kwargs['event'])}
        )
        return data_forms

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        source_event = get_object_or_404(models.Event, pk=kwargs['event'])
        view_forms = self.get_forms(request.POST, request.FILES, **kwargs)
        validation_result = True
        for form in view_forms.values():
            validation_result = validation_result and form.is_valid()

        if not validation_result:
            return self.render_to_response(
                self.get_context_data(
                    forms=view_forms, source_event=source_event, **kwargs)
            )

        event = view_forms['event'].save(commit=False)

        event.court_id = source_event.court_id

        event.inventory_list = persistence.clone_inventory_list(
            source_event.inventory_list
        )

        persistence.save_event_and_related_things(
            event,
            request.user,
            visitors=view_forms['visitors'].cleaned_data['users']
        )

        view_forms['event'].save_m2m()

        return http.HttpResponseRedirect(
            reverse('let_me_app:view_event', kwargs={'pk': event.id})
        )


class CompleteEventView(TemplateView):
    template_name = 'events/complete_event.html'

    def get_context_data(self, **kwargs):
        event = get_object_or_404(
            models.Event,
            pk=kwargs['event'],
            status=models.EventStatuses.PENDING
        )
        formset = forms.CompleteEventVisitFormSet(
            instance=event, data=kwargs.get('data')
        )
        for visit_form in formset.forms:
            visit_form.initial.setdefault('income', event.preliminary_price)
        result = {
            'event': event,
            'visit_formset': formset}

        return result

    def check_permissions(self, request, court):
        return (court.admin_group.user_set.filter(id=request.user.id).exists()
            or self.request.user.is_staff)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        context = self.get_context_data(data=request.POST, **kwargs)
        formset = context['visit_formset']
        if formset.is_valid():
            formset.save(commit=False)
            context['event'].status = models.EventStatuses.COMPLETED
            context['event'].save()
            for form in formset.forms:
                instance = form.instance
                receipt = instance.receipt or models.Receipt()
                if (instance.status == VisitStatuses.COMPLETED
                        and form.cleaned_data['income'] is not None):
                    receipt.price = form.cleaned_data['income']
                    receipt.status = models.PriceStatuses.PAID
                    receipt.save()
                    instance.receipt = receipt
                form.instance.save()
            return http.HttpResponseRedirect(
                reverse(
                    'let_me_app:view_event',
                    kwargs={'pk': context['event'].id}
                )
            )
        return self.render_to_response(context)

