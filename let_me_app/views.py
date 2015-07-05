from xml.dom import minidom
from itertools import groupby

from django import http
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.views.generic.base import View as BaseView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, BaseUpdateView
from django.views.generic.list import ListView

from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet
from extra_views.generic import GenericInlineFormSet

from let_me_app import persistence, forms, models



class OccasionInline(InlineFormSet):
    model = models.Occasion


class BookingPolicyInline(GenericInlineFormSet):
    model = models.BookingPolicy


class CreateCourtView(CreateWithInlinesView):
    model = models.Court
    inlines = [BookingPolicyInline, OccasionInline]


class ChatList(ListView):
    template_name = 'chat/list.html'
    model = models.InternalMessage

    def get_queryset(self, **kwargs):
        result = super(ChatList, self).get_queryset(**kwargs)
        return result.filter(chatparticipant__user=self.request.user)


class ChatDetails(DetailView):
    template_name = 'chat/details.html'
    model = models.InternalMessage

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

    def get_context_data(self, **kwargs):
        result = super(EventView, self).get_context_data(**kwargs)
        event = result['object']
        result['event_actions'] = persistence.get_event_actions_for_user(
            self.request.user, event)
        result['is_admin'] = event.court.admin_group.user_set.filter(
            email=self.request.user.email).exists()
        result['active_applications'] =event.application_set.filter(
            status=models.ApplicationStatuses.ACTIVE
        )
        return result


class UserEventListView(ListView):
    model = models.Visit
    template_name = "events/user_events.html"

    def get_queryset(self, **kwargs):
        result = super(UserEventListView, self).get_queryset(**kwargs)
        return result.filter(user=self.request.user).order_by('-event__start_at')

    def get_context_data(self, **kwargs):
        result = super(UserEventListView, self).get_context_data(**kwargs)
        object_list = result['object_list']
        grouped_objects = groupby(object_list, lambda x: x.event.start_at.date())
        result['grouped_objects'] = [(i, [j for j in g]) for i, g in grouped_objects]
        return result


class EventActionMixin(object):
    def get_queryset(self, request, *args, **kwargs):
        pass

    def process_object(self, obj):
        pass

    def check_permissions(self, request, *args, **kwargs):
        return True

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

        return http.HttpResponseRedirect(
            reverse('let_me_app:view_event', kwargs={'pk': kwargs['event']})
        )


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
    def get_queryset(self, request, *args, **kwargs):
        return models.Application.objects.filter(
            event_id=kwargs['event'],
            user_id=kwargs['user'],
            status=models.ApplicationStatuses.ACTIVE
        )

    def process_object(self, application):
        application.status = models.ApplicationStatuses.ACCEPTED
        application.save()
        persistence.create_event_visit(
            application.event, application.user, None
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


class CompleteEventView(EventActionMixin, BaseView):
    def check_permissions(self, request, *args, **kwargs):
        return Group.objects.filter(
            court__event=kwargs['event'], user=request.user).exists()

    def get_queryset(self, request, *args, **kwargs):
        return models.Event.objects.filter(
            id=kwargs['event'], status=models.VisitStatuses.PENDING
        )

    def process_object(self, event):
        event.status = models.EventStatuses.COMPLETED
        event.save()


class CourtDetailView(DetailView):
    template_name = 'courts/details.html'
    model = models.Court

    def get_context_data(self, **kwargs):
        result = super(CourtDetailView, self).get_context_data(**kwargs)
        court = result['object']
        result['is_admin'] = court.admin_group.user_set.filter(
            email=self.request.user.email).exists()
#        result['event_actions'] = persistence.get_event_actions_for_user(self.request.user, event)
        return result
