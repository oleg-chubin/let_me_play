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


class RecommendationStatuses:
    ACTIVE = 1
    OUTDATED = 2
    CANCELED = 3

    CHOICES = (
        (ACTIVE, _("Active")),
        (OUTDATED, _("Outdated")),
        (CANCELED, _("Canceled")),
    )


class Coolness:
    WEAKER = 1
    BIT_WEAKER = 2
    SAME = 3
    BIT_STRONGER = 4
    STRONGER = 5

    CHOICES = (
        (WEAKER, _('weaker')),
        (BIT_WEAKER, _('bit_weaker')),
        (SAME, _('same')),
        (BIT_STRONGER, _('bit_stronger')),
        (STRONGER, _('stronger'))
    )

    IMAGES = {
        WEAKER: 'images/weaker_coolness.png',
        BIT_WEAKER: 'images/bit_weaker_coolness.png',
        SAME: 'images/same_coolness.png',
        BIT_STRONGER: 'images/bit_stronger_coolness.png',
        STRONGER: 'images/stronger_coolness.png'
    }


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


class CoolnessRate(models.Model):
    topic = models.ForeignKey(Followable, related_name='expertise')
    rater = models.ForeignKey(UserModel)
    value = models.IntegerField(choices=Coolness.CHOICES,
                                default=Coolness.SAME)

    class Meta:
        unique_together = ('topic', 'rater')

    def __str__(self):
        return "{} thinks that {} is {}".format(
            self.rater_id,
            self.topic_id,
            dict(Coolness.CHOICES)[self.value])


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
    geo_line = gismodels.LineStringField(
        verbose_name=_('Geo line'), null=True, blank=True)
    address = models.TextField(verbose_name=_("Address"))
    name = models.CharField(verbose_name=_('name'), max_length=128)
    description = models.TextField(verbose_name=_("Description"))

    objects = gismodels.GeoManager()

    def __str__(self):
        return self.name


class StaffRole(models.Model):
    name = models.CharField(_("name"), max_length=128, default='')

    def __str__(self):
        return self.name


class ActivityType(models.Model):
    image = models.ImageField(_('image'))
    title = models.CharField(_('title'), max_length=128)
    default_role = models.ForeignKey(StaffRole)

    def __str__(self):
        return self.title


class Court(Followable):
    site = models.ForeignKey(Site, related_name='court_set')
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


class Event(Followable):
    start_at = models.DateTimeField(_('date started'), db_index=True)
    description = models.TextField(verbose_name=_("Description"), max_length=1024, default='')
    court = models.ForeignKey(Court)
    invoice = models.ForeignKey(Invoice, null=True, blank=True)
    inventory_list = models.ForeignKey(InventoryList, null=True, blank=True)
    preliminary_price = models.IntegerField(_("Preliminary price"))
    status = models.IntegerField(
        choices=EventStatuses.CHOICES, default=EventStatuses.PENDING
    )

    def __str__(self):
        description = self.description
        if len(description) > 20:
            description = description[:16] + '...'
        return "{} ({})".format(description, self.start_at)

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

    def __str__(self):
        return "{} ({})".format(self.price, dict(PriceStatuses.CHOICES)[self.status])


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


class VisitRole(models.Model):
    visit = models.ForeignKey(Visit, verbose_name=_("Visit"))
    role = models.ForeignKey(StaffRole, verbose_name=_("role"))
    invoice = models.ForeignKey(
        Invoice, null=True, blank=True, verbose_name=_("invoice")
    )

    def __str__(self):
        return str(self.role)


class IndexParametr(models.Model):
    name = models.CharField(_("name"), max_length=256)
    units = models.CharField(_("units"), max_length=16)

    def __str__(self):
        return "{} ({})".format(self.name, self.units)


class CoachRecommendation(models.Model):
    recommendation = models.TextField(
        verbose_name=_("Description"), max_length=1024, default='')
    coach = models.ForeignKey(UserModel)
    visit = models.ForeignKey(Visit)
    status = models.IntegerField(choices=RecommendationStatuses.CHOICES,
                                 default=RecommendationStatuses.ACTIVE)


class VisitIndex(models.Model):
    visit = models.ForeignKey(Visit)
    parametr = models.ForeignKey(IndexParametr)
    value = models.FloatField(verbose_name=_("Value"))
