from datetime import datetime
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
from django.db.models import F
from django.views.generic.base import View as BaseView, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import BaseUpdateView
from django.views.generic.list import ListView

from extra_views import CreateWithInlinesView, InlineFormSet
from extra_views.generic import GenericInlineFormSet

from let_me_app import persistence, forms, models
from django.db import transaction
from let_me_app.models import VisitStatuses, ApplicationStatuses,\
    ProposalStatuses
from let_me_auth.models import User, FollowerGroup
import itertools
from django.db.models.aggregates import Count
from django.db.models.query import Prefetch
from let_me_app.tasks import send_notification
from let_me_app.persistence import filter_event_for_user


NUMBER_OF_KNOWN_VISITS = 10
NULL_DATE = datetime(1900, 1, 1).date()


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

        notification_context = {
            'reason': "new_chat_message",
            'initiator_id': self.request.user.id,
            'message_id': self.object.id
        }
        send_notification.delay(notification_context)

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

        queryset  = filter_event_for_user(queryset, self.request.user)

        queryset = queryset.select_related(
            'inventory_list', 'court', 'court__site', 'court__activity_type')
        queryset = queryset.prefetch_related('inventory_list__inventory_set__equipment')
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
        recommendation = recommendation.select_related('coach')[:1]
        if recommendation:
            return recommendation[0]

    def _get_visit_indexes(self, visit):
        indexes = models.VisitIndex.objects.filter(visit=visit)
        return indexes.values('parametr__name', 'parametr__units', 'value')

    def get_visitors_form(self, prefix, court_id, exclude_ids):
        form = forms.ExtendedEventVisitForm(prefix=prefix)
        checkbox_field = form.fields['known_users']
        queryset = User.objects.filter(visit__event__court_id=court_id)
        queryset = queryset.exclude(id__in=exclude_ids)
        queryset = queryset.annotate(visit_count=Count('id'))
        queryset = queryset.order_by('-visit_count')[:NUMBER_OF_KNOWN_VISITS]
        checkbox_field.choices = [
            (checkbox_field.prepare_value(i), i) for i in queryset]
        return form

    def get_context_data(self, **kwargs):
        result = super(EventView, self).get_context_data(**kwargs)
        event = result['object']
        admin_user_ids = event.court.admin_group.user_set.values_list('id', flat=True)
        result['is_admin'] = self.request.user.id in admin_user_ids
        result['admin_user_ids'] = admin_user_ids

        result['visit_role_form'] = forms.EventVisitRoleForm()
        result['inventory_form'] = forms.InventoryForm()
        result['active_applications'] = event.application_set.filter(
            status=models.ApplicationStatuses.ACTIVE
        ).select_related('user').order_by('id')

        default_role = event.court.activity_type.default_role_id

        active_visits = event.visit_set.select_related('user')
        active_visits = active_visits.prefetch_related('visitrole_set__role').order_by('id')

        result['active_visits'] = []
        result['staff_list'] = []
        for visit in active_visits:
            if any(j.role_id == default_role for j in visit.visitrole_set.all()):
                result['active_visits'].append(visit)
            else:
                result['staff_list'].append(visit)

        result['active_proposals'] = event.proposal_set.all().select_related('user').order_by('id')
        result['user_inventory'] = self._get_user_inventory(event, active_visits)

        result['following_groups'] = FollowerGroup.objects.filter(targets=event)

        result['is_event_staff'] = any(
            self.request.user.id == i.user_id for i in result['staff_list'])

        for prop in result['active_proposals']:
            if (prop.user == self.request.user
                    and prop.status==models.ProposalStatuses.ACTIVE):
                result['my_active_proposal'] = prop


        result['active_visits_id'] = [
            i.user_id for i in result['active_visits']
            if i.status in [models.VisitStatuses.PENDING, models.VisitStatuses.COMPLETED]
        ]

        result['proposal_form'] = self.get_visitors_form(
            'proposal',
            event.court_id,
            result['active_visits_id'] + [i.user_id for i in result['active_proposals']]
        )
        result['visit_form'] = self.get_visitors_form(
            'visit', event.court_id, result['active_visits_id'])

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

        result.update(self._get_gallery_info(event))

        chats = models.InternalMessage.objects.filter(
            subject=event, chatparticipant__user=self.request.user)[:1]
        if chats:
            result['chat'] = chats[0]

        return result

    def _get_gallery_info(self, event):
        images = (
            {'obj': i, 'type': 'image'}
            for i in models.GalleryImage.objects.filter(followable=event)
        )
        video = (
            {'obj': i, 'type': 'video'}
            for i in models.GalleryVideo.objects.filter(followable=event)
        )

        gallery_objects = [
            [j[1] for j in i[1]] for i in groupby(
                enumerate(itertools.chain(video, images)),
                key=lambda x: x[0] // 4)
        ]

        return {'gallery_objects': gallery_objects}


class UserGalleryListView(TemplateView):
    template_name = "gallery/user_gallery.html"

    def apply_gallery_filter(self, queryset, user_id):
        event_queryset = models.Event.objects.filter(
            visit__user_id=user_id,
            visit__status=VisitStatuses.COMPLETED).values_list('id', flat=True)
        queryset = queryset.filter(followable__in=event_queryset)
        queryset = queryset.select_related('followable__event__start_at')
        return queryset.order_by('followable__event__start_at')

    def get_context_data(self, **kwargs):
        user_id = kwargs['user']
        image_gallery = self.apply_gallery_filter(
            models.GalleryImage.objects.all(), user_id)
        video_gallery = self.apply_gallery_filter(
            models.GalleryVideo.objects.all(), user_id)

        image_gallery_groupped = itertools.groupby(
            image_gallery, key=lambda x: x.followable.event.start_at.date())
        video_gallery_groupped = itertools.groupby(
            video_gallery, key=lambda x: x.followable.event.start_at.date())


        initial_date = NULL_DATE
        image_date, images = next(image_gallery_groupped, (NULL_DATE, ()))
        video_date, videos = next(video_gallery_groupped, (NULL_DATE, ()))
        result = []
        while True:
            process_objects = []
            if image_date == video_date:
                if image_date > initial_date:
                    process_objects.extend(('image', 'video'))
                    initial_date = image_date
            elif image_date < video_date:
                if image_date > initial_date:
                    initial_date = image_date
                    process_objects.append('image')
                elif video_date > initial_date:
                    initial_date = video_date
                    process_objects.append('video')
            else:
                if video_date > initial_date:
                    initial_date = video_date
                    process_objects.append('video')
                elif image_date > initial_date:
                    initial_date = image_date
                    process_objects.append('image')

            if not process_objects:
                break

            images_gen = video_gen = ()
            if 'image' in process_objects:
                images_gen = [{'obj': i, 'type': 'image'} for i in images]
                image_date, images = next(image_gallery_groupped, (NULL_DATE, ()))
            if 'video' in process_objects:
                video_gen = [{'obj': i, 'type': 'video'} for i in videos]
                video_date, videos = next(video_gallery_groupped, (NULL_DATE, ()))

            gallery_objects = [
                [j[1] for j in i[1]] for i in groupby(
                    enumerate(itertools.chain(video_gen, images_gen)),
                    key=lambda x: x[0] // 4)
            ]
            result.append([initial_date, gallery_objects])

        return {'user_gallery_objects': result}

        result = super(UserEventListView, self).get_context_data(**kwargs)
        object_list = persistence.get_user_visit_applications_and_proposals(
            self.request.user)
        grouped_objects = groupby(object_list, lambda x: x.event.start_at.date())
        result['grouped_objects'] = [(i, [j for j in g]) for i, g in grouped_objects]
        return result


class UserEventListView(TemplateView):
    template_name = "events/user_events.html"

    def get_context_data(self, **kwargs):
        result = super(UserEventListView, self).get_context_data(**kwargs)
        object_list = persistence.get_user_visit_applications_and_proposals(
            self.request.user)
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


class UserManagedCourtsListView(ListView):
    model = models.Court
    template_name = "courts/user_managed_courts.html"

    def get_queryset(self, **kwargs):
        queryset = super(UserManagedCourtsListView, self).get_queryset(**kwargs)
        queryset = queryset.filter(
            admin_group__user=self.request.user).order_by('site__name')
        queryset = queryset.select_related('activity_type')
        queryset = queryset.prefetch_related('event_set')

        fetch_queryset = models.Event.objects.filter(
            status=models.EventStatuses.PENDING).order_by('start_at')
        fetch_queryset = fetch_queryset.prefetch_related('target_groups')
        fetch_queryset = fetch_queryset.prefetch_related(
            'visit_set',
            Prefetch(
                'visit_set',
                queryset=models.Visit.objects.filter(status=VisitStatuses.PENDING),
                to_attr='active_visit_set'
            )
        )
        fetch_queryset = fetch_queryset.prefetch_related(
            'proposal_set',
            Prefetch(
                'proposal_set',
                queryset=models.Proposal.objects.filter(status=ProposalStatuses.ACTIVE),
                to_attr='active_proposal_set'
            )
        )
        fetch_queryset = fetch_queryset.prefetch_related(
            'application_set',
            Prefetch(
                'application_set',
                queryset=models.Application.objects.filter(status=ApplicationStatuses.ACTIVE),
                to_attr='active_application_set'
            )
        )

        queryset = queryset.prefetch_related(
            'event_set',
            Prefetch(
                'event_set', queryset=fetch_queryset, to_attr='active_event_set'
            )
        )
        return queryset


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

        self.send_notification(objects)

        return http.HttpResponseRedirect(self.get_success_url(**kwargs))


class CancelApplicationView(EventActionMixin, BaseView):
    def get_queryset(self, request, *args, **kwargs):
        return models.Application.objects.filter(
            event_id=kwargs['event'],
            user=request.user,
            status=models.ApplicationStatuses.ACTIVE
        )

    def send_notification(self, objects):
        notification_context = {
            'reason': "cancel_application",
            'initiator_id': self.request.user.id,
            'object_ids': [i.id for i in objects]
        }
        send_notification.delay(notification_context)

    def process_object(self, application):
        application.status = models.ApplicationStatuses.CANCELED
        application.save()


class CreateApplicationView(BaseView):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if request.user.is_anonymous():
            return http.HttpResponseForbidden()

        events = models.Event.objects.filter(id=kwargs['event'])
        events = filter_event_for_user(events, self.request.user)

        if not events:
            return http.HttpResponseNotFound()

        comment = request.POST['comment']
        application = models.Application.objects.create(
            event=events[0],
            user=request.user,
            status=models.ApplicationStatuses.ACTIVE,
            comment=comment
        )

        notification_context = {
            'reason': "create_application",
            'initiator_id': self.request.user.id,
            'object_ids': [application.id]
        }
        send_notification.delay(notification_context)

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
        return forms.EventProposalForm(data=self.request.POST, prefix='proposal')

    def action_is_allowed(self, event):
        return event.court.admin_group.user_set.filter(
            id=self.request.user.id).exists()

    def save_on_success(self, event, form):
        comment = form.cleaned_data['comment']
        proposals = []
        user_set = set(form.cleaned_data['users']) | set(form.cleaned_data['known_users'])
        for user in user_set:
            proposal, _ = models.Proposal.objects.get_or_create(
                    event=event, user=user,
                    status=models.ApplicationStatuses.ACTIVE,
                    defaults={'comment':comment}
                )
            proposals.append(proposal)

        notification_context = {
            'reason': "create_proposal",
            'initiator_id': self.request.user.id,
            'object_ids': [i.id for i in proposals]
        }
        send_notification.delay(notification_context)


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
                name="inventory_list for %s" %visit.event.id)
            visit.inventory_list = inventory_list
            visit.save()
        inventory = form.save(commit=False)
        inventory.inventory_list = visit.inventory_list
        inventory.save()

    def get_success_url(self, obj):
        return reverse('let_me_app:view_event', kwargs={'pk': obj.event.id})


class CreateVisitView(DetailRelatedPostView):
    def get_form(self):
        return forms.ExtendedEventVisitForm(data=self.request.POST, prefix='visit')

    def action_is_allowed(self, event):
        return event.court.admin_group.user_set.filter(
            id=self.request.user.id).exists()

    def save_on_success(self, event, form):
        visits = []

        user_set = set(form.cleaned_data['users']) | set(form.cleaned_data['known_users'])
        for user in user_set:
            visits.append(persistence.create_event_visit(event, user, None))

        notification_context = {
            'reason': "create_visit",
            'initiator_id': self.request.user.id,
            'object_ids': [i.id for i in visits]
        }
        send_notification.delay(notification_context)


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

    def send_notification(self, objects):
        notification_context = {
            'reason': "decline_proposal",
            'initiator_id': self.request.user.id,
            'object_ids': [i.id for i in objects]
        }
        send_notification.delay(notification_context)


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

    def send_notification(self, objects):
        notification_context = {
            'reason': "accept_proposal",
            'initiator_id': self.request.user.id,
            'object_ids': [i.id for i in objects]
        }
        send_notification.delay(notification_context)


class DeclineApplicationEventView(EventActionMixin, BaseView):
    def check_permissions(self, request, *args, **kwargs):
        return Group.objects.filter(
            court__event=kwargs['event'], user=request.user).exists()

    def get_queryset(self, request, *args, **kwargs):
        return models.Application.objects.filter(
            event_id=kwargs['event'],
            id=kwargs['application'],
            status=models.ApplicationStatuses.ACTIVE
        )

    def process_object(self, application):
        application.status = models.ApplicationStatuses.DECLINED
        application.save()

    def send_notification(self, objects):
        notification_context = {
            'reason': "decline_application",
            'initiator_id': self.request.user.id,
            'object_ids': [i.id for i in objects]
        }
        send_notification.delay(notification_context)


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

    def send_notification(self, objects):
        notification_context = {
            'reason': "accept_application",
            'initiator_id': self.request.user.id,
            'object_ids': [i.id for i in objects]
        }
        send_notification.delay(notification_context)


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

    def send_notification(self, objects):
        notification_context = {
            'reason': "cancel_visit",
            'initiator_id': self.request.user.id,
            'object_ids': [i.id for i in objects]
        }
        send_notification.delay(notification_context)


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

    def send_notification(self, objects):
        notification_context = {
            'reason': "decline_visit",
            'initiator_id': self.request.user.id,
            'object_ids': [i.id for i in objects]
        }
        send_notification.delay(notification_context)


class RemoveVisitRoleEventView(EventActionMixin, BaseView):
    def check_permissions(self, request, *args, **kwargs):
        return Group.objects.filter(
            court__event=kwargs['event'], user=request.user).exists()

    def get_queryset(self, request, *args, **kwargs):
        return models.VisitRole.objects.filter(id=kwargs['role'])

    def process_object(self, obj):
        obj.delete()

    def send_notification(self, objects):
        pass


class UpdateVisitRoleEventView(EventActionMixin, BaseView):
    def check_permissions(self, request, *args, **kwargs):
        return Group.objects.filter(
            court__event=kwargs['event'], user=request.user).exists()

    def get_queryset(self, request, *args, **kwargs):
        return models.Visit.objects.filter(id=kwargs['visit'])

    def process_object(self, obj):
        form = forms.EventVisitRoleForm(
            data=self.request.POST, files=self.request.FILES
        )
        if form.is_valid():
            for role in form.cleaned_data['roles']:
                models.VisitRole.objects.get_or_create(visit=obj, role=role)

    def send_notification(self, objects):
        pass


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

    def send_notification(self, objects):
        notification_context = {
            'reason': "cancel_proposal",
            'initiator_id': self.request.user.id,
            'object_ids': [i.id for i in objects]
        }
        send_notification.delay(notification_context)


class CancelEventView(EventActionMixin, BaseView):
    def check_permissions(self, request, *args, **kwargs):
        return Group.objects.filter(
            court__event=kwargs['event'], user=request.user).exists()

    def get_queryset(self, request, *args, **kwargs):
        return models.Event.objects.filter(
            id=kwargs['event'], status=models.VisitStatuses.PENDING
        )

    def process_object(self, event):
        persistence.finish_event(event, models.EventStatuses.CANCELED)
        visits = event.visit_set.filter(status=models.VisitStatuses.PENDING)
        visits.update(status=models.VisitStatuses.DECLINED)

    def send_notification(self, objects):
        notification_context = {
            'reason': "cancel_event",
            'initiator_id': self.request.user.id,
            'object_ids': [i.id for i in objects]
        }
        send_notification.delay(notification_context)


class CourtDetailView(DetailView):
    template_name = 'courts/details.html'
    model = models.Court

    def get_context_data(self, **kwargs):
        result = super(CourtDetailView, self).get_context_data(**kwargs)
        court = result['object']
        is_admin = result['is_admin'] = court.admin_group.user_set.filter(
            email=self.request.user.email).exists() or self.request.user.is_staff

        result['is_admin'] = is_admin
        result['court_events'] = filter_event_for_user(
            court.event_set.order_by('-start_at'), self.request.user)
        result['group_admin_form'] = forms.GroupForm()
        result['court_groups'] = FollowerGroup.objects.filter(followable=court)
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

        queryset = filter_event_for_user(queryset, self.request.user)

        queryset = queryset.prefetch_related(
            'visit_set',
            Prefetch(
                'visit_set',
                queryset=models.Visit.objects.filter(
                    status=VisitStatuses.PENDING,
                    visitrole__role=F('event__court__activity_type__default_role')).only('id'),
                to_attr='people_count'
            )
        )

        form = forms.EventSearchForm(
            data=self.request.GET
        )
        if form.is_valid():
            if form.cleaned_data['geo_point'] and form.cleaned_data['radius']:
                site_queryset = models.Site.objects.filter(
                    geo_point__distance_lt=(form.cleaned_data['geo_point'],
                                            D(m=form.cleaned_data['radius']))
                )
                site_queryset = site_queryset | models.Site.objects.filter(
                    geo_line__distance_lt=(form.cleaned_data['geo_point'],
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


class CourtSearchView(ListView):
    template_name = 'courts/search.html'
    model = models.Court

    def get_queryset(self):
        queryset = super(CourtSearchView, self).get_queryset()
        queryset = queryset.order_by('site__name')

        form = forms.EventSearchForm(
            data=self.request.GET
        )
        if form.is_valid():
            if form.cleaned_data['geo_point'] and form.cleaned_data['radius']:
                site_queryset = models.Site.objects.filter(
                    geo_point__distance_lt=(form.cleaned_data['geo_point'],
                                            D(m=form.cleaned_data['radius']))
                )
                site_queryset = site_queryset | models.Site.objects.filter(
                    geo_line__distance_lt=(form.cleaned_data['geo_point'],
                                            D(m=form.cleaned_data['radius']))
                )
                queryset = queryset.filter(site__in=site_queryset)
            if form.cleaned_data['activity_type']:
                queryset = queryset.filter(
                    activity_type__in=form.cleaned_data['activity_type'])
        queryset = queryset.prefetch_related(
            Prefetch(
                'event_set',
                queryset=models.Event.objects.annotate(
                    apps_count=Count('application__id')).filter(
                    application__status=ApplicationStatuses.ACTIVE),
                to_attr='events_active_applications')
        )
        return queryset

    def get_context_data(self, **kwargs):
        result = super(CourtSearchView, self).get_context_data(**kwargs)
        result['search_form'] = forms.CourtSearchForm(data=self.request.GET)
        return result


class AddCourtGroupView(BaseView):
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

        FollowerGroup.objects.create(followable=courts[0])

        return http.HttpResponseRedirect(
            reverse('let_me_app:view_court', kwargs={'pk': kwargs['court']})
        )


class CreateEventView(TemplateView):
    template_name = 'events/create_new.html'

    def get_visitors_form(self, **kwargs):
        suffix = kwargs.get('suffix', '')
        kw = {
            'prefix': 'event' + suffix,
            'initial': {'users': kwargs.get('users', [])}
        }
        if 'data' in kwargs:
            kw['data'] = kwargs['data']
        return forms.EventVisitForm(**kw)

    def get_event_form(self, **kwargs):
        kw = {'prefix': 'event'}
        for key in ['data', 'files']:
            if key in kwargs:
                kw[key] = kwargs[key]
        return forms.EventForm(**kw)

    def get_forms(self, **kwargs):
        data_forms = OrderedDict()
        for entity, form_class in [('site', forms.SiteForm), ('court', forms.CourtForm)]:
            if not entity in kwargs:
                kw = {'prefix': entity}
                for key in ['data', 'files']:
                    if key in kwargs:
                        kw[key] = kwargs[key]
                data_forms[entity] = form_class(**kw)
        data_forms['event'] = self.get_event_form(**kwargs)
        data_forms['visitors'] = self.get_visitors_form(
            suffix="visitors", uesrs=[self.request.user], **kwargs)
        data_forms['proposals'] = self.get_visitors_form(
            suffix="proposals", **kwargs)
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
        view_forms = kwargs.get('forms') or self.get_forms(**kwargs)
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
        view_forms = self.get_forms(
            data=request.POST, files=request.FILES, **kwargs)
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

        visitors = self._get_visitors(view_forms)
        invitees = self._get_proposals(view_forms)

        persistence.save_event_and_related_things(
            instances['event'], request.user,
            visitors=visitors, invitees=invitees
        )

        for form in view_forms.values():
            if isinstance(form, django_forms.ModelForm):
                form.save_m2m()

        return http.HttpResponseRedirect(
            reverse(
                'let_me_app:view_event', kwargs={'pk': instances['event'].id}
            )
        )

    def _get_visitors(self, view_forms):
        return view_forms['visitors'].cleaned_data['users']

    def _get_proposals(self, view_forms):
        return view_forms['proposals'].cleaned_data['users']


class CreateSiteEventView(CreateEventView):
    template_name = 'events/create_for_site.html'

    def get_context_data(self, **kwargs):
        context = super(CreateSiteEventView, self).get_context_data(**kwargs)
        context['site_object'] = get_object_or_404(models.Site, pk=kwargs['site'])
        return context


class CreateCourtEventView(CreateEventView):
    template_name = 'events/create_for_court.html'

    def get_event_form(self, **kwargs):
        form = super(CreateCourtEventView, self).get_event_form(**kwargs)
        form.fields['target_groups'].queryset = FollowerGroup.objects.filter(
            followable=kwargs['court']) |  FollowerGroup.objects.filter(name="anyone")
        return form

    def get_visitors_form(self, **kwargs):
        suffix = kwargs.get('suffix', '')

        kw = {
            'prefix': 'event' + suffix,
            'initial': {'users': kwargs.get('users', [])}
        }
        if 'data' in kwargs:
            kw['data'] = kwargs['data']
        form = forms.ExtendedEventVisitForm(**kw)
        checkbox_field = form.fields['known_users']
        queryset = User.objects.filter(
            visit__event__court__id=self.kwargs['court'])
        queryset = queryset.annotate(visit_count=Count('id'))
        queryset = queryset.order_by('-visit_count')[:NUMBER_OF_KNOWN_VISITS]
        checkbox_field.choices = [
            (checkbox_field.prepare_value(i), i) for i in queryset]
        return form

    def check_permissions(self, request, court):
        return (court.admin_group.user_set.filter(id=request.user.id).exists()
            or self.request.user.is_staff)

    def get_context_data(self, **kwargs):
        context = super(CreateCourtEventView, self).get_context_data(**kwargs)
        context['court'] = get_object_or_404(models.Court, pk=kwargs['court'])
        return context

    def _get_visitors(self, view_forms):
        return (set(view_forms['visitors'].cleaned_data['users'])
                | set(view_forms['visitors'].cleaned_data['known_users']))

    def _get_proposals(self, view_forms):
        return (set(view_forms['proposals'].cleaned_data['users'])
                | set(view_forms['proposals'].cleaned_data['known_users']))


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
        queryset = queryset.select_related('visit__event', 'coach')
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

    def get_event_form(self, **kwargs):
        kw = {'prefix': 'event'}
        for key in ['data', 'files']:
            if key in kwargs:
                kw[key] = kwargs[key]
        form = forms.EventForm(**kw)
        queryset = FollowerGroup.objects.filter(
            followable__court__event=kwargs['event'])
        queryset = queryset |  FollowerGroup.objects.filter(name="anyone")
        form.fields['target_groups'].queryset = queryset
        return form

    def get_context_data(self, **kwargs):
        view_forms = kwargs.get('forms') or self.get_forms(**kwargs)
        result = {'forms': view_forms}
        result['event'] = (kwargs.get('source_event') or
            get_object_or_404(models.Event, pk=kwargs['event']))
        return result

    def check_permissions(self, request, court):
        return (court.admin_group.user_set.filter(id=request.user.id).exists()
            or self.request.user.is_staff)

    def get_visitors_form(self, **kwargs):
        suffix = kwargs.get('suffix', '')
        kw = {
            'prefix': 'event' + suffix,
            'initial': {'users': kwargs.get('users', [])}
        }
        if 'data' in kwargs:
            kw['data'] = kwargs['data']
        form = forms.ExtendedEventVisitForm(**kw)
        checkbox_field = form.fields['known_users']
        queryset = User.objects.filter(
            visit__event__court__event__id=self.kwargs['event'])
        queryset = queryset.annotate(visit_count=Count('id'))
        queryset = queryset.order_by('-visit_count')[:NUMBER_OF_KNOWN_VISITS]
        checkbox_field.choices = [
            (checkbox_field.prepare_value(i), i) for i in queryset]
        return form

    def get_forms(self, **kwargs):
        data_forms = OrderedDict()
        data_forms['event'] = self.get_event_form(**kwargs)
        data_forms['visitors'] = self.get_visitors_form(
            prefix='event', suffix="visitors", users=[self.request.user], **kwargs
        )
        visits = models.Visit.objects.filter(
            event=kwargs['event'],
            status__in=[VisitStatuses.COMPLETED, VisitStatuses.PENDING] )
        visits = visits.exclude(user=self.request.user).values('user_id')
        data_forms['proposals'] = self.get_visitors_form(
            prefix='event', suffix="proposals",
            users=User.objects.filter(id__in=visits), **kwargs
        )
        return data_forms

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        source_event = get_object_or_404(models.Event, pk=kwargs['event'])
        view_forms = self.get_forms(data=request.POST, files=request.FILES, **kwargs)
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

        visit_set = (set(view_forms['visitors'].cleaned_data['users'])
                     | set(view_forms['visitors'].cleaned_data['known_users']))
        proposal_set = (set(view_forms['proposals'].cleaned_data['users'])
                        | set(view_forms['proposals'].cleaned_data['known_users']))

        persistence.save_event_and_related_things(
            event, request.user, visitors=visit_set, invitees=proposal_set
        )

        view_forms['event'].save_m2m()

        notification_context = {
            'reason': "create_event",
            'initiator_id': self.request.user.id,
            'object_id': event
        }
        send_notification.delay(notification_context)

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
            instance=event, data=kwargs.get('data'),
            queryset=models.Visit.objects.filter(status=VisitStatuses.PENDING)
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
            persistence.finish_event(
                context['event'], models.EventStatuses.COMPLETED)
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


class UpdateGalleryView(TemplateView):
    template_name = 'gallery/update_form.html'

    def get_context_data(self, **kwargs):
        event = get_object_or_404(models.Event, pk=kwargs['event'])
        images_formset = forms.GalleryImagesFormset(
            instance=event, data=kwargs.get('data'), files=kwargs.get('files'))
        video_formset = forms.GalleryVideoFormset(
            instance=event, data=kwargs.get('data'), files=kwargs.get('files'))
        result = {
            'event': event,
            'images_formset': images_formset,
            'video_formset': video_formset
        }
        return result

    def check_permissions(self, request, court):
        return (court.admin_group.user_set.filter(id=request.user.id).exists()
            or self.request.user.is_staff)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        context = self.get_context_data(
            data=request.POST, files=request.FILES, **kwargs)
        formsets = [context[i] for i in ['video_formset', 'images_formset']]
        if all([f.is_valid() for f in formsets]):
            for formset in formsets:
                formset.save()
            return http.HttpResponseRedirect(
                reverse(
                    'let_me_app:view_event',
                    kwargs={'pk': context['event'].id}
                )
            )
        return self.render_to_response(context)
