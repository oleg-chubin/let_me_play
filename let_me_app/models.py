from django.contrib.auth.models import AbstractBaseUser, Group, PermissionsMixin
from django.utils.translation import ugettext as _
from django.db import models
from django.utils.http import urlquote
from django.core.mail import send_mail
from django.utils import timezone

from .managers import UserManager


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


class User(AbstractBaseUser, Followable, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.email)

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip() or self.email

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name or self.email


class InternalMessage(models.Model):
    sender = models.ForeignKey(User, related_name='outgoing_messages')
    recipient = models.ForeignKey(User, related_name='incoming_messages')
    created_at = models.DateTimeField(_('date created'), default=timezone.now)
    text = models.TextField(_("text"))


class Peeper(models.Model):
    followable = models.ForeignKey(Followable, related_name='followers')
    user = models.ForeignKey(User)


class PrivateComment(Followable):
    user = models.ForeignKey(User, related_name='my_comments')
    followable = models.ForeignKey(Followable, related_name='users_comments')
    created_at = models.DateTimeField(_('date created'), default=timezone.now)
    text = models.TextField(_("text"))


class Changelog(Followable):
    followable = models.ForeignKey(Followable, related_name='followable_set')
    created_at = models.DateTimeField(_('date created'), default=timezone.now)
    text = models.TextField(_("text"))


class Site(Followable):
    name = models.CharField(max_length=128)
    description = models.TextField(_("text"))
    address = models.TextField(_("text"))
    map_image = models.ImageField(_('map image'), null=True, blank=True)


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


class Staff(User):
    description = models.TextField()


class Event(Followable):
    start_at = models.DateTimeField(_('date started'))
    name = models.CharField(max_length=128, default='')
    description = models.TextField(max_length=1024, default='')
    court = models.ForeignKey(Court)
    invoice = models.ForeignKey(Invoice, null=True, blank=True)
    inventory_list = models.ForeignKey(InventoryList, null=True, blank=True)
    staff = models.ManyToManyField(Staff)


class Equipment(models.Model):
    name = models.CharField(max_length=256)


class Inventory(models.Model):
    equipment = models.ForeignKey(Equipment)
    amount = models.IntegerField()
    inventory_list = models.ForeignKey(InventoryList)


class Proposal(models.Model):
    comment = models.TextField(max_length=256, default='')
    user = models.ForeignKey(User)
    event = models.ForeignKey(Event)
    status = models.IntegerField(choices=ProposalStatuses.CHOICES,
                                 default=ProposalStatuses.ACTIVE)


class Application(models.Model):
    comment = models.TextField(max_length=256, default='')
    event = models.ForeignKey(Event)
    inventory_list = models.ForeignKey(InventoryList, null=True, blank=True)
    user = models.ForeignKey(User)
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
    user = models.ForeignKey(User)
    event = models.ForeignKey(Event)


