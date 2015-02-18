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

class Peeper(models.Model):
    followable = models.ForeignKey(Followable)
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
    # there we need 2 fileds

