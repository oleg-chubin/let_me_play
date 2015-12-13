import time

from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
from osm_field.fields import LatitudeField, LongitudeField, OSMField
from django.contrib.gis.db import models as gismodels

UserModel = settings.AUTH_USER_MODEL


class CF(models.F):
    ADD = '||'


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


class VisitStatuses:
    PENDING = 1
    COMPLETED = 2
    CANCELED = 3
    DECLINED = 4
    MISSED = 5

    CHOICES = (
        (PENDING, _("Pending")),
        (COMPLETED, _("Completed")),
        (CANCELED, _("Canceled")),
        (DECLINED, _("Declined")),
        (MISSED, _("Missed")),
    )


class EventStatuses:
    PENDING = 1
    COMPLETED = 2
    CANCELED = 3

    CHOICES = (
        (PENDING, _("Pending")),
        (COMPLETED, _("Completed")),
        (CANCELED, _("Canceled")),
    )


ApplicationStatuses = ProposalStatuses


class Followable(models.Model):
    def __str__(self):
        return "followable object {}".format(self.id)


class GalleryImage(models.Model):
    followable = models.ForeignKey(Followable)
    image = models.ImageField(_('image'))
    thumbnail = models.ImageField(_('thumbnail'), null=True, blank=True)
    note = models.CharField(_('note'), max_length=128, default="just a picture")

    THUMBNAIL_HEIGHT = 100


class ChatParticipant(models.Model):
    user = models.ForeignKey(UserModel)
    chat = models.ForeignKey('InternalMessage')
    last_seen = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'chat')


class InternalMessage(models.Model):
    created_at = models.DateTimeField(_('date created'), default=timezone.now)
    last_update = models.DateTimeField(auto_now=True)
    subject = models.ForeignKey(Followable, null=True, blank=True)
    text = models.TextField(_("text"))


class Peeper(models.Model):
    followable = models.ForeignKey(Followable, related_name='followers')
    user = models.ForeignKey(UserModel)

    class Meta:
        unique_together = ('followable', 'user')

    def __str__(self):
        return "{} follows {}".format(self.user, self.followable.id)



class PrivateComment(models.Model):
    user = models.ForeignKey(UserModel, related_name='my_comments')
    followable = models.ForeignKey(Followable, related_name='users_comments')
    created_at = models.DateTimeField(_('date created'), default=timezone.now)
    text = models.TextField(_("text"))


class Changelog(models.Model):
    followable = models.ForeignKey(Followable, related_name='followable_set')
    created_at = models.DateTimeField(_('date created'), default=timezone.now)
    text = models.TextField(_("text"))

    def __str__(self):
        return "followable {} {}".format(self.followable_id, self.text)


class Site(Followable):
    geo_point = gismodels.PointField(verbose_name=_('Geo point'), null=True, blank=True)

    name = models.CharField(verbose_name=_('name'), max_length=128)
    description = models.TextField(verbose_name=_("Description"))
    address = models.TextField(verbose_name=_("Address"))

    objects = gismodels.GeoManager()

    def __str__(self):
        return self.name


class ActivityType(models.Model):
    image = models.ImageField(_('image'))
    title = models.CharField(_('title'), max_length=128)

    def __str__(self):
        return self.title


class Court(Followable):
    site = models.ForeignKey(Site)
    activity_type = models.ForeignKey(ActivityType)
    admin_group = models.ForeignKey(Group, blank=True, null=True)
    description = models.TextField(_("Description"))

    SHORT_DESCR_LEN = 20

    def __str__(self):
        description = self.description
        if len(description) > self.SHORT_DESCR_LEN:
            description = "{}...".format(description)
        return "{} ({})".format(self.site, description)


@receiver(pre_save, sender=Court)
def admin_group_creator(sender, **kwargs):
    if not kwargs['instance'].admin_group:
        admin_group = Group.objects.create(name="court_admin_group_%s" % time.time())
        kwargs['instance'].admin_group = admin_group


@receiver(post_save, sender=Court)
def admin_group_updater(sender, **kwargs):
    if kwargs['created']:
        kwargs['instance'].admin_group.name = "court_admin_group_%s" % kwargs['instance'].id
        kwargs['instance'].admin_group.save()



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

    def __str__(self):
        return "{} ({})".format(self.name, self.total_sum)


class InventoryList(models.Model):
    name = models.CharField(_('name'), max_length=256)

    def __str__(self):
        return self.name


class StaffProfile(Followable):
    user = models.OneToOneField(UserModel)
    description = models.TextField(_('description'))

    def __str__(self):
        return str(self.user)


class Event(Followable):
    start_at = models.DateTimeField(_('date started'), db_index=True)
    name = models.CharField(_("name"), max_length=128, default='')
    description = models.TextField(verbose_name=_("Description"), max_length=1024, default='')
    court = models.ForeignKey(Court)
    invoice = models.ForeignKey(Invoice, null=True, blank=True)
    inventory_list = models.ForeignKey(InventoryList, null=True, blank=True)
    staff = models.ManyToManyField(StaffProfile, blank=True)
    status = models.IntegerField(
        choices=EventStatuses.CHOICES, default=EventStatuses.PENDING
    )

    def __str__(self):
        return "{} ({})".format(self.name, self.start_at)


class StaffRole(models.Model):
    name = models.CharField(_("name"), max_length=128, default='')

    def __str__(self):
        return self.name


class EventStaff(models.Model):
    event = models.ForeignKey(Event, verbose_name=_("event"))
    staff = models.ForeignKey(StaffProfile, verbose_name=_("staff"))
    role = models.ForeignKey(StaffRole, verbose_name=_("role"))
    invoice = models.ForeignKey(
        Invoice, null=True, blank=True, verbose_name=_("invoice")
    )

    def __str__(self):
        return "{} ({})".format(self.staff, self.role)


class Equipment(models.Model):
    name = models.CharField(_("name"), max_length=256)

    def __str__(self):
        return self.name


class Inventory(models.Model):
    equipment = models.ForeignKey(Equipment)
    amount = models.IntegerField(_("amount"))
    inventory_list = models.ForeignKey(InventoryList)

    def __str__(self):
        return "{} ({})".format(self.equipment, self.amount)


class Proposal(models.Model):
    comment = models.TextField(_("comment"), max_length=256, default='')
    user = models.ForeignKey(UserModel)
    event = models.ForeignKey(Event)
    status = models.IntegerField(choices=ProposalStatuses.CHOICES,
                                 default=ProposalStatuses.ACTIVE)

    def __str__(self):
        return "{} proposal for user's ({}) for event {}".format(
            dict(ProposalStatuses.CHOICES)[self.status], self.user, self.event
        )


class Application(models.Model):
    comment = models.TextField(_("comment"), max_length=256, default='')
    event = models.ForeignKey(Event)
    inventory_list = models.ForeignKey(InventoryList, null=True, blank=True)
    user = models.ForeignKey(UserModel)
    status = models.IntegerField(choices=ApplicationStatuses.CHOICES,
                                 default=ApplicationStatuses.ACTIVE)

    def __str__(self):
        return "{} user's ({}) application for event {}".format(
            dict(ApplicationStatuses.CHOICES)[self.status],
            self.user, self.event
        )


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
    status = models.IntegerField(choices=VisitStatuses.CHOICES,
                                 default=VisitStatuses.PENDING)

    def __str__(self):
        return "{} user {} visit to {} ".format(
            dict(VisitStatuses.CHOICES)[self.status], self.user, self.event
        )

