from django.test import TestCase
from django.contrib.auth.models import AnonymousUser
from let_me_auth.models import User
from let_me_app.persistence import get_my_chats,\
    get_user_visit_applications_and_proposals

from . import factories, models
from django.utils import timezone
from _datetime import timedelta

# Create your tests here.


class EventUserActionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='some@ema.il')
        self.events = []
        self.outdated_events = []

        for i in range(1, 5):
            self.events.append(
                factories.EventFactory(
                    start_at=timezone.now() + timedelta(days=i)
                )
            )

        for i in range(1, 5):
            self.outdated_events.append(
                factories.EventFactory(
                    start_at=timezone.now() - timedelta(days=i)
                )
            )

    def test_empty_call(self):
        res = get_user_visit_applications_and_proposals(self.user)
        self.assertEqual(list(res), [])

    def test_applications_only(self):
        applications = []
        for event in self.events:
            for status, _ in models.ApplicationStatuses.CHOICES:
                app = models.Application.objects.create(
                    user=self.user, status=status, event=event
                )
                if status == models.ApplicationStatuses.ACTIVE:
                    applications.append(app)
        res = get_user_visit_applications_and_proposals(self.user)
        self.assertEqual(list(res), list(reversed(applications)))

    def test_proposals_only(self):
        proposals = []
        for event in self.events:
            for status, _ in models.ProposalStatuses.CHOICES:
                proposal = models.Proposal.objects.create(
                    user=self.user, status=status, event=event
                )
                if status == models.ProposalStatuses.ACTIVE:
                    proposals.append(proposal)

        res = get_user_visit_applications_and_proposals(self.user)
        self.assertEqual(list(res), list(reversed(proposals)))

    def test_incomplete_visits_only(self):
        visits = []
        for event in self.events:
            for status, _ in models.VisitStatuses.CHOICES:
                if status == models.VisitStatuses.COMPLETED:
                    continue
                visit = models.Visit.objects.create(
                    user=self.user, status=status, event=event
                )
                if status == models.VisitStatuses.PENDING:
                    visits.append(visit)

        res = get_user_visit_applications_and_proposals(self.user)
        self.assertEqual(list(res), list(reversed(visits)))

    def test_completed_visits_only(self):
        visits = []
        for event in self.outdated_events:
            visit = models.Visit.objects.create(
                user=self.user, status=models.VisitStatuses.COMPLETED, event=event
            )
            visits.append(visit)

        res = get_user_visit_applications_and_proposals(self.user)
        self.assertEqual(list(res), visits)

    def test_inactive_visits(self):
        visits = []
        for event in self.outdated_events:
            for status, _ in models.VisitStatuses.CHOICES:
                visit = models.Visit.objects.create(
                    user=self.user, status=status, event=event
                )
                if status in [models.VisitStatuses.PENDING, models.VisitStatuses.COMPLETED]:
                    visits.append(visit)

        res = get_user_visit_applications_and_proposals(self.user)
        self.assertEqual(list(res), visits)

    def test_objects_order(self):
        objects = []
        for event in self.events:
                visit = models.Visit.objects.create(
                    user=self.user, event=event,
                    status=models.VisitStatuses.PENDING
                )
                objects.append(visit)
                proposal = models.Proposal.objects.create(
                    user=self.user, event=event,
                    status=models.ProposalStatuses.ACTIVE
                )
                objects.append(proposal)
                app = models.Application.objects.create(
                    user=self.user, event=event,
                    status=models.ApplicationStatuses.ACTIVE
                )
                objects.append(app)

        objects = list(reversed(objects))
        for event in self.outdated_events:
            visit = models.Visit.objects.create(
                user=self.user, status=models.VisitStatuses.COMPLETED, event=event
            )
            objects.append(visit)
        res = get_user_visit_applications_and_proposals(self.user)
        self.assertEqual(list(res), objects)


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

