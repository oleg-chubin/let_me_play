'''
Created on Jun 21, 2015

@author: oleg
'''
from . import models
from django.utils import timezone
from let_me_app.tasks import send_notification


def filter_event_for_user(queryset, user):
    user_groups = user.groups.values_list('id', flat=True)
    return (
        queryset.filter(target_groups__in=user_groups)
        | queryset.filter(target_groups__name='anyone'))


def save_event_and_related_things(event, user, visitors=(), invitees=()):
    event.save()
    models.InternalMessage.objects.create(subject=event)

    visits = []
    for visitor in visitors:
        visits.append(create_event_visit(event, visitor, None))

    proposals = []
    for visitor in invitees:
        proposal, _ = models.Proposal.objects.get_or_create(
            event=event, user=visitor,
            status=models.ProposalStatuses.ACTIVE,
        )
        proposals.append(proposal)

    notification_context = {
        'reason': "create_event",
        'initiator_id': user.id,
        'object_id': event
    }
    send_notification.delay(notification_context)

    if proposals:
        notification_context = {
            'reason': "create_proposal",
            'initiator_id': user.id,
            'object_ids': [i.id for i in proposals]
        }
        send_notification.delay(notification_context)

    if visits:
        notification_context = {
            'reason': "create_visit",
            'initiator_id': user.id,
            'object_ids': [i.id for i in visits]
        }
        send_notification.delay(notification_context)

    return event


def get_my_chats(user):
    if user.is_anonymous():
        return models.InternalMessage.objects.none()
    return models.InternalMessage.objects.filter(
        chatparticipant__user=user).order_by('last_update')


def create_event_visit(event, user, inventory_list):
    visit, created = models.Visit.objects.get_or_create(
        event=event, user=user,
        status=models.VisitStatuses.PENDING,
        defaults={'inventory_list': inventory_list}
    )
    if created:
        chat = list(models.InternalMessage.objects.filter(subject=event))
        if chat:
            models.ChatParticipant.objects.get_or_create(
                user=user, chat=chat[0]
            )
        role, created = models.VisitRole.objects.get_or_create(
            visit=visit, role=event.court.activity_type.default_role
        )
    return visit


def clone_inventory_list(inventory_list):
    if inventory_list is None:
        return
    cloned_list = models.InventoryList.objects.create(name=inventory_list.name)

    inventory_collection = []
    for inventory in inventory_list.inventory_set.all():
        inventory_collection.append(
            models.Inventory(
                amount=inventory.amount,
                inventory_list=cloned_list,
                equipment=inventory.equipment
            )
        )

    models.Inventory.objects.bulk_create(inventory_collection)

    return cloned_list


def get_user_visit_applications_and_proposals(user):
    applications = models.Application.objects.filter(
        user=user, status=models.ApplicationStatuses.ACTIVE)
    applications = applications.order_by('-event__start_at')
    applications.select_related('event__court')

    proposals = models.Proposal.objects.filter(
        user=user, status=models.ProposalStatuses.ACTIVE)
    proposals = proposals.order_by('-event__start_at')
    proposals.select_related('event__court')

    visits = models.Visit.objects.filter(
        user=user,
        status__in=[models.VisitStatuses.PENDING,models.VisitStatuses.COMPLETED]
    ).select_related('event__court')
    visits = visits.order_by('-event__start_at')
    visits.select_related('event__court')
    now = timezone.now()
    return sorted(
        list(applications) + list(proposals) + list(visits),
        key=lambda x: (now - x.event.start_at, x.__class__.__name__),
    )


def finish_event(event, status):
    event.status = status
    event.save()
    applications = event.application_set.filter(
        status=models.ApplicationStatuses.ACTIVE)
    applications.update(status=models.ApplicationStatuses.DECLINED)
    proposals = event.proposal_set.filter(
        status=models.ApplicationStatuses.ACTIVE)
    proposals.update(status=models.ProposalStatuses.CANCELED)
