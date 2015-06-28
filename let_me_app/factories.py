from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone


import factory
from . import models

UserModel = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    email = factory.Sequence(lambda n: 'email_{0}@gmail.com'.format(n))
    first_name = factory.Sequence(lambda n: 'first_name_{0}'.format(n))
    last_name = factory.Sequence(lambda n: 'last_name_{0}'.format(n))

    class Meta:
        model = UserModel


class SiteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Site

    name = factory.Sequence(lambda n: 'name_{0}'.format(n))
    description = factory.Sequence(lambda n: 'description_{0}'.format(n))
    address = factory.Sequence(lambda n: 'address_{0}'.format(n))


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group


class CourtFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Court

    site = factory.SubFactory(SiteFactory)
    description = factory.Sequence(lambda n: 'description_{0}'.format(n))
    admin_group = factory.SubFactory(GroupFactory)

class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Event

    start_at = factory.Sequence(lambda n: timezone.now() + timedelta(days=n))
    name = factory.Sequence(lambda n: 'event_{0}'.format(n))
    description = factory.Sequence(lambda n: 'description_{0}'.format(n))
    court = factory.SubFactory(CourtFactory)


class VisitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Visit

    user = factory.SubFactory(UserFactory)
    event = factory.SubFactory(EventFactory)


class ApplicationFactory(factory.django.DjangoModelFactory):
    comment = factory.Sequence(lambda n: 'comment_{0}'.format(n))
    user = factory.SubFactory(UserFactory)
    event = factory.SubFactory(EventFactory)
    status = models.ApplicationStatuses.ACTIVE

    class Meta:
        model = models.Application


class ProposalFactory(factory.django.DjangoModelFactory):
    comment = factory.Sequence(lambda n: 'comment_{0}'.format(n))
    user = factory.SubFactory(UserFactory)
    event = factory.SubFactory(EventFactory)
    status = models.ProposalStatuses.ACTIVE

    class Meta:
        model = models.Proposal
