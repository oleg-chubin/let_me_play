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
    password = first_name
    cell_phone = first_name
    cell_phone_is_valid = True

    class Meta:
        model = UserModel


    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the default ``_create`` with our custom call."""
        manager = cls._get_manager(model_class)
        # The default would use ``manager.create(*args, **kwargs)``
        return manager.create_user(*args, **kwargs)


class SiteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Site

    name = factory.Sequence(lambda n: 'name_{0}'.format(n))
    description = factory.Sequence(lambda n: 'description_{0}'.format(n))
    address = factory.Sequence(lambda n: 'address_{0}'.format(n))


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        self.user_set.add(UserFactory())


class StaffRoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.StaffRole


class ActivityTypeFactory(factory.django.DjangoModelFactory):
    default_role = factory.SubFactory(StaffRoleFactory)
    class Meta:
        model = models.ActivityType


class CourtFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Court

    site = factory.SubFactory(SiteFactory)
    description = factory.Sequence(lambda n: 'description_{0}'.format(n))
    admin_group = factory.SubFactory(GroupFactory)
    activity_type = factory.SubFactory(ActivityTypeFactory)

class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Event

    preliminary_price = factory.Sequence(lambda n: n * 10)
    start_at = factory.Sequence(lambda n: timezone.now() + timedelta(days=n))
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
