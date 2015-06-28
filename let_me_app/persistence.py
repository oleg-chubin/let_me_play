'''
Created on Jun 21, 2015

@author: oleg
'''
from . import models


def get_event_actions_for_user(user, event_object):
    if user.is_anonymous():
        return []
    result = []
    proposals = models.Proposal.objects.filter(
        user=user, event=event_object, status=models.ProposalStatuses.ACTIVE
    )
    applications = models.Application.objects.filter(
        user=user, event=event_object, status=models.ApplicationStatuses.ACTIVE
    )
    visits = models.Visit.objects.filter(
        user=user,
        event=event_object,
        status=models.VisitStatuses.PENDING
    )
    visit_exists = visits.exists()
    if proposals.count():
        result.extend(['decline_proposal', 'accept_proposal'])
    if applications.count():
        result.extend(["cancel_application"])
    if visit_exists:
        result.append('cancel_visit')
    return result or ['apply_for_event']


def get_my_chats(user):
    if user.is_anonymous():
        return models.InternalMessage.objects.none()
    return models.InternalMessage.objects.filter(
        chatparticipant__user=user).order_by('last_update')


def create_event_visit(event, user, inventory_list):
    visit = models.Visit.objects.create(
        event=event, user=user, inventory_list=inventory_list
    )
    return visit
