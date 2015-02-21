from django.contrib.auth.models import AbstractBaseUser, Group, PermissionsMixin
from django.utils.translation import ugettext as _
from django.db import models
from django.utils.http import urlquote
from django.core.mail import send_mail
from django.utils import timezone

from .managers import UserManager


PRICE_STATUS_CHOICES = (
    (1, _("New")),
    (2, _("Approved")),
    (3, _("Rejected")),
    (4, _("Paid")),
    (5, _("Not paid")),
)


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
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name


class InternalMessage(models.Model):
    sender = models.ForeignKey(User, related_name='sender')
    recipient = models.ForeignKey(User, related_name='recipient')


class Peeper(models.Model):
    followable = models.ForeignKey(Followable, related_name='followers')
    user = models.ForeignKey(User)


class PrivateComment(Followable):
    user = models.ForeignKey(User)


class Site(Followable):
    pass


class Court(Followable):
    site = models.ForeignKey(Site)
    group = models.ForeignKey(Group)


class Invoice(models.Model):
    name = models.CharField(max_length=128)


class Equipment(models.Model):
    name = models.CharField(max_length=256)


class InventoryList(models.Model):
    name = models.CharField(max_length=256)
    quantity = models.IntegerField()


class Inventory(models.Model):
    equipment = models.ForeignKey(Equipment)
    amount = models.IntegerField()
    inventory_list = models.ForeignKey(InventoryList)


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


class Visit(models.Model):
    inventory_list = models.ForeignKey(InventoryList)
    receipet = models.ForeignKey(Receipt)
    user = models.ForeignKey(User)
    event = models.ForeignKey(Event)


