from django.contrib.auth.models import User as DjangoUser
from django.utils.translation import ugettext as _
from django.db import models


PRICE_STATUS_CHOICES = (
    (1, _("New")),
    (2, _("Approved")),
    (3, _("Rejected")),
    (4, _("Paid")),
    (5, _("Not paid")),
)

class Followable(models.Model):
    pass

class User(Followable):
    user = models.OneToOneField(DjangoUser)
    group = models.ManyToManyField(Group)
    permission = models.ManyToManyField(Permission)

class InternalMessage(models.Model):
    sender = models.ForeignKey(User, related_name='sender')
    recipient = models.ForeignKey(User, related_name='recipient')

class Peeper(models.Model):
    followable = models.ForeignKey(Followable)
    user = models.ForeignKey(User)

class PrivateComment(Followable):
    user = models.ForeignKey(User)

class Site(Followable):
    pass

class Permission(models.Model):
    name = models.CharField(max_length=128)
    user = models.ManyToManyField(User)
    group = models.ManyToManyField(Group)

class Group(models.Model):
    name = models.CharField(max_length=128)
    user = models.ManyToManyField(User)
    permission = models.ManyToManyField(Permission)

class Court(Followable):
    site = models.ForeignKey(Site)
    group = models.ForeignKey(Group)

class Invoice(models.Model):
    name = models.CharField(max_length=128)

class Event(Followable):
    name = models.CharField(max_length=128)
    description = models.TextField(max_length=1024)
    court = models.ForeignKey(Court)
    invoice = models.ForeignKey(Invoice)
    inventory_list = models.ForeignKey(InventoryList)

class Proposal(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(max_length=1024)
    user = models.ForeignKey(User)
    event = models.ForeignKey(Event)

class Staff(User):
    name = models.CharField(max_length=128)
    event = models.ForeignKey(Event)

class Application(models.Model):
    name = models.CharField(max_length=128)
    event = models.ForeignKey(Event)
    inventory_list = models.ForeignKey(InventoryList)
    user = models.ForeignKey(User)

class Receipt(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.IntegerField(choices=PRICE_STATUS_CHOICES, default=1)

class Equipment(models.Model):
    name = models.CharField(max_length=256)

class InventoryList(models.Model):
    name = models.CharField(max_length=256)
    quantity = models.IntegerField()

class Inventory(models.Model):
    equipment = models.ForeignKey(Equipment)
    inventory_list = models.ForeignKey(InventoryList)

class Visit(models.Model):
    inventory_list = models.ForeignKey(InventoryList)
    user = models.ForeignKey(User)
    event = models.ForeignKey(Event)


