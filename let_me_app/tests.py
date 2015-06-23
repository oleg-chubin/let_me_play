from django.test import TestCase
from django.contrib.auth.models import AnonymousUser
from let_me_app.persistence import get_event_actions_for_user

from . import factories, models

# Create your tests here.


class EventUserActionTestCase(TestCase):
    def test_no_proposals_no_applications_apply_for_event(self):
        event = factories.EventFactory()
        user = factories.UserFactory()
        result = get_event_actions_for_user(user, event)
        self.assertEqual(result, ['apply_for_event'])

    def test_inactive_proposals_inactive_applications_apply_for_event(self):
        event = factories.EventFactory()
        user = factories.UserFactory()
        for status, _ in models.ProposalStatuses.CHOICES:
            if status != models.ProposalStatuses.ACTIVE:
                factories.ProposalFactory(user=user, event=event, status=status)
        for status, _ in models.ApplicationStatuses.CHOICES:
            if status != models.ApplicationStatuses.ACTIVE:
                factories.ApplicationFactory(
                    user=user, event=event, status=status
                )
        result = get_event_actions_for_user(user, event)
        self.assertEqual(result, ['apply_for_event'])

    def test_proposal_no_applications_accept_decline_proposal(self):
        event = factories.EventFactory()
        user = factories.UserFactory()
        factories.ProposalFactory(user=user, event=event)
        result = get_event_actions_for_user(user, event)
        self.assertEqual(
            set(result), set(['accept_proposal', 'decline_proposal'])
        )

    def test_proposal_application_accept_decline_proposal_cancel_application(self):
        event = factories.EventFactory()
        user = factories.UserFactory()
        factories.ProposalFactory(user=user, event=event)
        factories.ApplicationFactory(user=user, event=event)
        result = get_event_actions_for_user(user, event)
        self.assertEqual(
            set(result),
            set(['accept_proposal', 'decline_proposal', 'cancel_application'])
        )

    def test_no_proposal_application_cancel_application(self):
        event = factories.EventFactory()
        user = factories.UserFactory()
        factories.ApplicationFactory(user=user, event=event)
        result = get_event_actions_for_user(user, event)
        self.assertEqual(set(result), set(['cancel_application']))

    def test_anonymous_user_no_actions(self):
        event = factories.EventFactory()
        user = AnonymousUser()
        result = get_event_actions_for_user(user, event)
        self.assertEqual(result, [])