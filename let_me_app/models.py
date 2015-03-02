from django.contrib.auth.models import Group
from django.utils.translation import ugettext as _
from django.db import models
from django.utils import timezone
from django.conf import settings


UserModel = settings.AUTH_USER_MODEL


class ReadStates:
    READ = 1
    UNREAD = 2

    CHOICES = (
        (READ, _("Read")),
        (UNREAD, _("Unread")),
    )


class PriceStatuses:
    NEW = 1
    PAID = 2
    NOT_PAID = 3

    CHOICES = (
        (NEW, _("New")),
        (PAID, _("Paid")),
        (NOT_PAID, _("Not paid")),
    )


class ProposalStatuses:
    ACTIVE = 1
    ACCEPTED = 2
    CANCELED = 3
    DECLINED = 4

    CHOICES = (
        (ACTIVE, _("Active")),
        (ACCEPTED, _("Accepted")),
        (CANCELED, _("Canceled")),
        (DECLINED, _("Declined")),
    )


ApplicationStatuses = ProposalStatuses


class Followable(models.Model):
    pass


class InternalMessage(models.Model):
    sender = models.ForeignKey(UserModel, related_name='outgoing_messages')
    recipient = models.ForeignKey(UserModel, related_name='incoming_messages')
    created_at = models.DateTimeField(_('date created'), default=timezone.now)
    text = models.TextField(_("text"))
    state = models.IntegerField(choices=ReadStates.CHOICES,
                                default=ReadStates.UNREAD)


class Peeper(models.Model):
    followable = models.ForeignKey(Followable, related_name='followers')
    user = models.ForeignKey(UserModel)


class PrivateComment(Followable):
    user = models.ForeignKey(UserModel, related_name='my_comments')
    followable = models.ForeignKey(Followable, related_name='users_comments')
    created_at = models.DateTimeField(_('date created'), default=timezone.now)
    text = models.TextField(_("text"))


class Changelog(Followable):
    followable = models.ForeignKey(Followable, related_name='followable_set')
    created_at = models.DateTimeField(_('date created'), default=timezone.now)
    text = models.TextField(_("text"))


class Site(Followable):
    name = models.CharField(_("name"), max_length=128)
    description = models.TextField(_("description"))
    address = models.TextField(_("address"))
    map_image = models.ImageField(
        _('map image'), upload_to="map_images", null=True, blank=True
    )


class Court(Followable):
    site = models.ForeignKey(Site)
    admin_group = models.ForeignKey(Group)
    description = models.TextField(_("text"))


class Occasion(models.Model):
    start_at = models.DateTimeField(_('date started'))
    duration = models.IntegerField(_("duration (minutes)"))
    period = models.IntegerField(_("period (hours)"))
    equipment = models.ForeignKey(Court)


class BookingPolicy(models.Model):
    court = models.ForeignKey(Court)
    group = models.ForeignKey(Group)
    early_registration = models.IntegerField(_("registration start within period"))
    price = models.IntegerField(_("estimated price"))


class Invoice(models.Model):
    name = models.CharField(max_length=128)
    total_sum = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.IntegerField(choices=PriceStatuses.CHOICES,
                                 default=PriceStatuses.NEW)


class InventoryList(models.Model):
    name = models.CharField(max_length=256)


class StaffProfile(Followable):
    user = models.OneToOneField(UserModel)
    description = models.TextField()


class Event(Followable):
    start_at = models.DateTimeField(_('date started'))
    name = models.CharField(max_length=128, default='')
    description = models.TextField(max_length=1024, default='')
    court = models.ForeignKey(Court)
    invoice = models.ForeignKey(Invoice, null=True, blank=True)
    inventory_list = models.ForeignKey(InventoryList, null=True, blank=True)
    staff = models.ManyToManyField(StaffProfile)


class Equipment(models.Model):
    name = models.CharField(max_length=256)


class Inventory(models.Model):
    equipment = models.ForeignKey(Equipment)
    amount = models.IntegerField()
    inventory_list = models.ForeignKey(InventoryList)


class Proposal(models.Model):
    comment = models.TextField(max_length=256, default='')
    user = models.ForeignKey(UserModel)
    event = models.ForeignKey(Event)
    status = models.IntegerField(choices=ProposalStatuses.CHOICES,
                                 default=ProposalStatuses.ACTIVE)


class Application(models.Model):
    comment = models.TextField(max_length=256, default='')
    event = models.ForeignKey(Event)
    inventory_list = models.ForeignKey(InventoryList, null=True, blank=True)
    user = models.ForeignKey(UserModel)
    status = models.IntegerField(choices=ApplicationStatuses.CHOICES,
                                 default=ApplicationStatuses.ACTIVE)


class Receipt(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.IntegerField(choices=PriceStatuses.CHOICES,
                                 default=PriceStatuses.NEW)


class Visit(models.Model):
    inventory_list = models.ForeignKey(InventoryList, null=True, blank=True)
    receipt = models.ForeignKey(Receipt, null=True, blank=True)
    user = models.ForeignKey(UserModel)
    event = models.ForeignKey(Event)


class GalleryImage(models.Model):
    followable = models.ForeignKey(Followable)
    image = models.ImageField(_('image'), upload_to="images")

