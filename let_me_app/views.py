from django.views.generic.detail import DetailView
from django.views.generic.base import View as BaseView
from django import http
from django.core.urlresolvers import reverse

from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet
from extra_views.generic import GenericInlineFormSet

from . import models
from let_me_app.persistence import get_event_actions_for_user


class OccasionInline(InlineFormSet):
    model = models.Occasion


class BookingPolicyInline(GenericInlineFormSet):
    model = models.BookingPolicy


class CreateCourtView(CreateWithInlinesView):
    model = models.Court
    inlines = [BookingPolicyInline, OccasionInline]


class EventView(DetailView):
    template_name = 'events/details.html'
    model = models.Event

    def get_context_data(self, **kwargs):
        result = super(EventView, self).get_context_data(**kwargs)
        result['event_actions'] = get_event_actions_for_user(self.request.user, result['object'])
        return result


class EventActionMixin(object):
    def get_queryset(self, request, *args, **kwargs):
        pass

    def process_object(self, obj):
        pass

    def post(self, request, *args, **kwargs):
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

class AcceptProposalView(DetailView):
    pass

