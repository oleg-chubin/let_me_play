'''
Created on Jul 3, 2015

@author: oleg
'''
from let_me_app import models
from django.db.models import F
from django.utils import timezone
from functools import wraps
from django.conf import settings


def oject_statuses(request):
    return {
        'APPLICATION_STATUSES': models.ApplicationStatuses,
        'PROPOSAL_STATUSES': models.ProposalStatuses,
        'EVENT_STATUSES': models.EventStatuses,
        'VISIT_STATUSES': models.VisitStatuses
    }

def for_authentificated_users(func):
    @wraps(func)
    def wrapped(request):
        if request.user.is_anonymous():
            return {}
        else:
            return func(request)
    return wrapped

@for_authentificated_users
def user_events(request):
    proposals = models.Proposal.objects.filter(
        user=request.user,
        event__start_at__gte=timezone.now(),
        status=models.ProposalStatuses.ACTIVE)
    visits = models.Visit.objects.filter(
        user=request.user,
        event__start_at__gte=timezone.now(),
        status=models.VisitStatuses.PENDING)
    unread_chats = models.ChatParticipant.objects.filter(
        user=request.user, chat__last_update__gt=F('last_seen'))
    applications = models.Application.objects.filter(
        event__court__admin_group__user=request.user,
        event__start_at__gte=timezone.now(),
        status=models.ApplicationStatuses.ACTIVE
    )

    return {
        'user_active_applications': applications,
        'user_messages': unread_chats,
        'user_active_proposals': proposals,
        'user_active_visits': visits
    }


def site_host(request):
    return {'SITE_DOMAIN': settings.SITE_DOMAIN}
