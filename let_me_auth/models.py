from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group
from django.utils.translation import ugettext as _
from django.db import models
from django.utils.http import urlquote
from django.core.mail import send_mail
from django.utils import timezone

from let_me_app.models import Followable
from .managers import UserManager
from django.db.models import signals
from django.dispatch.dispatcher import receiver


class Sex:
    MALE = 1
    FEMALE = 2
    NOT_SPECIFIED = 3

    CHOICES = (
        (MALE, _("Male")),
        (FEMALE, _("Female")),
        (NOT_SPECIFIED, _("Not specified")),
    )


class Newcomer(models.Model):
    user = models.ForeignKey('User')
    code = models.CharField(_('first name'), max_length=40, db_index=True)


class User(AbstractBaseUser, Followable, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    cell_phone = models.CharField(_('cell phone'), max_length=16, blank=True)
    cell_phone_is_valid = models.BooleanField(default=False)
    sex = models.IntegerField(choices=Sex.CHOICES, default=Sex.NOT_SPECIFIED)
    avatar = models.ImageField(_('image'), upload_to='avatars', blank=True)
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

    def __str__(self):
        return self.get_full_name()


@receiver(signals.pre_save, sender=User)
def change_handler(sender, **kwargs):
    instance = kwargs['instance']
    if (instance.id  and
            User.objects.get(pk=instance.id).cell_phone != instance.cell_phone):
        instance.cell_phone_is_valid = False


@receiver(signals.post_save, sender=User)
def create_notification_settings(sender, **kwargs):
    instance = kwargs['instance']
    if kwargs.get('created'):
        NotificationSettings.objects.get_or_create(
            user=instance,
            defaults=dict(
                sms_notifications=True, email_notifications=True, lang='ru')
        )


class NotificationSettings(models.Model):
    SMS_NOTIFICATION_CHOICES = [
        (True, _("Sms Notifications Enabled")),
        (False, _("Sms Notifications Disabled"))
    ]

    EMAIL_NOTIFICATION_CHOICES = [
        (True, _("Email Notifications Enabled")),
        (False, _("Email Notifications Disabled"))
    ]

    sms_notifications = models.BooleanField(
        _("Use sms for notifications"),
        choices=SMS_NOTIFICATION_CHOICES, default=False)
    email_notifications = models.BooleanField(
        _("Use email for notifications"),
        choices=EMAIL_NOTIFICATION_CHOICES, default=False)
    lang = models.CharField(_('language'), max_length=18)
    user = models.OneToOneField(User, primary_key=True)


class ConfirmationCodes(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    code = models.CharField(_('confirmation code'), max_length=8)
    created_at = models.DateTimeField(auto_now_add=True)


class FollowerGroup(Group):
    followable = models.ForeignKey(
        Followable, null=True, related_name='group_owners')
    verbose_name = models.CharField(_('verbose name'), max_length=80)
    targets = models.ManyToManyField(Followable, related_name='target_groups')

    def __str__(self):
        return "{} ({})".format(self.verbose_name, self.name)
