'''
Created on Jun 21, 2015

@author: oleg
'''
from . import models


def save_event_and_related_things(event, user, visitors=tuple()):
    event.save()
    models.InternalMessage.objects.create(subject=event)

    for visitor in visitors:
        create_event_visit(event, visitor, None)
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

