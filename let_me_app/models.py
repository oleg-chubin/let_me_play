from django.contrib.auth.models import Group
from django.utils.translation import ugettext as _
from django.db import models
from django.utils import timezone
from django.conf import settings


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
    pass


class ChatParticipant(models.Model):
    user = models.ForeignKey(UserModel)
    chat = models.ForeignKey('InternalMessage')
    last_seen = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'chat')


class InternalMessage(models.Model):
    created_at = models.DateTimeField(_('date created'), default=timezone.now)
    last_update = models.DateTimeField(auto_now=True)
    text = models.TextField(_("text"))


class Peeper(models.Model):
    followable = models.ForeignKey(Followable, related_name='followers')
    user = models.ForeignKey(UserModel)


class PrivateComment(models.Model):
    user = models.ForeignKey(UserModel, related_name='my_comments')
    followable = models.ForeignKey(Followable, related_name='users_comments')
    created_at = models.DateTimeField(_('date created'), default=timezone.now)
    text = models.TextField(_("text"))


class Changelog(models.Model):
    followable = models.ForeignKey(Followable, related_name='followable_set')
    created_at = models.DateTimeField(_('date created'), default=timezone.now)
    text = models.TextField(_("text"))


class Site(Followable):
    name = models.CharField(max_length=128)
    description = models.TextField(_("Description"))
    address = models.TextField(_("Address"))
    map_image = models.ImageField(_('map image'), null=True, blank=True)

    def __str__(self):
        return self.name


class Court(Followable):
    site = models.ForeignKey(Site)
    admin_group = models.ForeignKey(Group)
    description = models.TextField(_("Description"))

    SHORT_DESCR_LEN = 20

    def __str__(self):
        description = self.description
        if len(description) > self.SHORT_DESCR_LEN:
            description = "{}...".format(description)
        return "{} ({})".format(self.site, description)


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
    staff = models.ManyToManyField(StaffProfile, blank=True)
    status = models.IntegerField(
        choices=EventStatuses.CHOICES, default=EventStatuses.PENDING
    )

    def __str__(self):
        return "{} ({})".format(self.name, self.start_at)


class Equipment(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Inventory(models.Model):
    equipment = models.ForeignKey(Equipment)
    amount = models.IntegerField()
    inventory_list = models.ForeignKey(InventoryList)

    def __str__(self):
        return "{} ({})".format(self.equipment, self.amount)


class Proposal(models.Model):
    comment = models.TextField(max_length=256, default='')
    user = models.ForeignKey(UserModel)
    event = models.ForeignKey(Event)
    status = models.IntegerField(choices=ProposalStatuses.CHOICES,
                                 default=ProposalStatuses.ACTIVE)

    def __str__(self):
        return "{} proposal for user's ({}) for event {}".format(
            dict(ProposalStatuses.CHOICES)[self.status], self.user, self.event
        )


class Application(models.Model):
    comment = models.TextField(max_length=256, default='')
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

