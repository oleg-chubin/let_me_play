from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Sex:
    MALE = 1
    FEMALE = 2
    NOT_SPECIFIED = 3

    CHOICES = (
        (MALE, _("Male")),
        (FEMALE, _("Female")),
        (NOT_SPECIFIED, _("Not specified")),
    )

class SportRankLevel:
    AMATEUR = 1
    SPORT_LEVEL3 = 2
    SPORT_LEVEL2 = 3
    SPORT_LEVEL1 = 4
    SPORT_LEVEL_KMS = 5
    SPORT_LEVEL_MS = 6
    SPORT_LEVEL_MSMK = 7
    NOT_SPECIFIED = 8

    CHOICES = (
        (AMATEUR, _("Amateur")),
        (SPORT_LEVEL3, _("Sport rank #3")),
        (SPORT_LEVEL2, _("Sport rank #2")),
        (SPORT_LEVEL1, _("Sport rank #1")),
        (SPORT_LEVEL_KMS, _("Sport rank KMS")),
        (SPORT_LEVEL_MS, _("Sport rank MS")),
        (SPORT_LEVEL_MSMK, _("Sport rank MSMK")),
        (NOT_SPECIFIED, _("Not specified")),
    )


class Participant(models.Model):
    first_name = models.CharField(_('first name'), max_length=30, default='')
    middle_name = models.CharField(_('middle name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, default='')
    email = models.EmailField(_('email address'), unique=True, blank=True)
    phone = models.CharField(_('cell phone'), max_length=16, blank=True)
    sex = models.IntegerField(choices=Sex.CHOICES, default=Sex.NOT_SPECIFIED)
    sport_level = models.IntegerField(choices=SportRankLevel.CHOICES,
                                      default=SportRankLevel.NOT_SPECIFIED)
    avatar = models.ImageField(_('image'), upload_to='avatars', blank=True)
    birth_date = models.DateField(_('birth date'), default=datetime(1950, 1, 1))
    country = models.CharField(_('country'), max_length=30, default='Russia')
    city = models.CharField(_('city'), max_length=30, default='Sevastopol')

    def __str__(self):
        return "{0} {1}".format(self.first_name, self.last_name)