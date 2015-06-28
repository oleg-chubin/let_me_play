from django.test import TestCase
from django.contrib.auth.models import AnonymousUser
from let_me_auth.models import User
from let_me_app.persistence import get_event_actions_for_user, get_my_chats

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

    def test_visit_exists_cancel_visit(self):
        event = factories.EventFactory()
        user = factories.UserFactory()
        visit = factories.VisitFactory(event=event, user=user)
        result = get_event_actions_for_user(user, event)
        self.assertIn('cancel_visit', result)

    def test_visit_exists_no_create_application(self):
        event = factories.EventFactory()
        user = factories.UserFactory()
        visit = factories.VisitFactory(event=event, user=user)
        result = get_event_actions_for_user(user, event)
        self.assertNotIn('apply_for_event', result)


class TestChatList(TestCase):
    def test_get_for_anonymous(self):
        anonym = AnonymousUser()
        result = get_my_chats(anonym)
        self.assertEqual(list(result), [])

    def test_empty_chat_list(self):
        user = User.objects.create(email='some@ema.il')
        result = get_my_chats(user)
        self.assertEqual(list(result), [])

    def test_only_users_chats_returned(self):
        user = User.objects.create(email='some@ema.il')
        other_user = User.objects.create(email='other@ema.il')
        chat = models.InternalMessage.objects.create()
        models.ChatParticipant.objects.create(user=other_user, chat=chat)
        result = get_my_chats(user)
        self.assertEqual(list(result), [])

    def test_returned_chat_order(self):
        user = User.objects.create(email='some@ema.il')
        other_users = []
        for email in ['other1@ma.il', 'other2@ma.il', 'other3@ma.il']:
            other_users.append(
                User.objects.create(email=email)
            )

        chats = []
        for other_user in other_users:
            chat = models.InternalMessage.objects.create()
            chats.append(chat)
            models.ChatParticipant.objects.create(user=other_user, chat=chat)
            models.ChatParticipant.objects.create(user=user, chat=chat)

        for chat in reversed(chats):
            chat.save()

        result = get_my_chats(user)
        result = [
            [x.user.email for x in i.chatparticipant_set.all()] for i in result
        ]
        expected_result = [
            ['other3@ma.il', 'some@ema.il'],
            ['other2@ma.il', 'some@ema.il'],
            ['other1@ma.il', 'some@ema.il']
        ]
        self.assertEqual([sorted(i) for i in result], expected_result)

