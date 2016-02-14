from django.test import TestCase
from django.contrib.auth.models import AnonymousUser
from let_me_auth.models import User
from let_me_app.persistence import get_my_chats,\
    get_user_visit_applications_and_proposals

from . import factories, models
from django.utils import timezone
from _datetime import timedelta

from django.test.utils import override_settings
from let_me_auth import models as auth_models
from unittest.mock import patch
from django.core.urlresolvers import reverse


class NotificationTasksTest(TestCase):
    domain = 'http://localhost'
    fake_body = 'zdfsdffsfsd'
    domain_mail = "some@ma.il"

    def setUp(self):
        self.event = factories.EventFactory()
        self.user = factories.UserFactory()
        self.admin_user = self.event.court.admin_group.user_set.all()[0]

    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       CELERY_ALWAYS_EAGER=True,
                       BROKER_BACKEND='memory',
                       SITE_DOMAIN=domain,
                       EMAIL_FROM = domain_mail)
    @patch('let_me_app.tasks.render_to_string')
    @patch('let_me_app.tasks.send_mail')
    def test_create_proposal_email(self, fake_send_mail, fake_render):
        fake_render.return_value = self.fake_body
        self.client.login(
            email=self.admin_user.email,
            password=self.admin_user.first_name
        )
        url = reverse('let_me_app:create_proposal', kwargs={'pk': self.event.id})
        auth_models.NotificationSettings.objects.create(
            sms_notifications=False,
            email_notifications=True,
            lang='ru',
            user=self.user
        )
        response = self.client.post(url, {'users': [self.user.id]})
        self.assertEqual(response.status_code, 302)
        fake_render.assert_called_with(
            'notifications/email/create_proposal.html',
            {
               'event': self.event,
               'event_url': '%s/let/me/view/event/%s/' % (self.domain, self.event.id)
            }
        )
        fake_send_mail.assert_called_with(
            'create_proposal',
            self.fake_body,
            self.domain_mail,
            [self.user.email],
            html_message=self.fake_body
        )

    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       CELERY_ALWAYS_EAGER=True,
                       BROKER_BACKEND='memory')
    @patch('let_me_app.tasks.render_to_string')
    @patch('let_me_app.tasks.send_sms')
    def test_create_proposal_sms(self, fake_send_sms, fake_render):
        fake_render.return_value = self.fake_body
        self.client.login(
            email=self.admin_user.email,
            password=self.admin_user.first_name
        )
        url = reverse('let_me_app:create_proposal', kwargs={'pk': self.event.id})
        auth_models.NotificationSettings.objects.create(
            sms_notifications=True,
            email_notifications=False,
            lang='ru',
            user=self.user
        )
        response = self.client.post(url, {'users': [self.user.id]})
        self.assertEqual(response.status_code, 302)
        fake_render.assert_called_with(
            'notifications/sms/create_proposal.html',
            {'event': self.event}
        )
        fake_send_sms.assert_called_with(
            self.user.cell_phone, self.fake_body,
        )

    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       CELERY_ALWAYS_EAGER=True,
                       BROKER_BACKEND='memory')
    @patch('let_me_app.tasks.send_sms')
    @patch('let_me_app.tasks.send_mail')
    def test_internal_chat(self, fake_send_mail, fake_send_sms):
        chat = models.InternalMessage.objects.create(subject=self.event)
        for u in [self.user, self.admin_user]:
            models.ChatParticipant.objects.create(user=u, chat=chat)

        self.client.login(
            email=self.admin_user.email,
            password=self.admin_user.first_name
        )
        url = reverse('let_me_app:post_chat_message', kwargs={'pk': chat.id})
        auth_models.NotificationSettings.objects.create(
            sms_notifications=True,
            email_notifications=True,
            lang='ru',
            user=self.user
        )
        response = self.client.post(url, {'message': "message"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            fake_send_mail.call_args[0][3], [self.user.email]
        )

    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       CELERY_ALWAYS_EAGER=True,
                       BROKER_BACKEND='memory')
    @patch('let_me_app.tasks.send_sms')
    @patch('let_me_app.tasks.send_mail')
    def test_event_created(self, fake_send_mail, fake_send_sms):
        self.client.login(
            email=self.admin_user.email,
            password=self.admin_user.first_name
        )
        url = reverse('let_me_app:clone_event', kwargs={'event': self.event.id})
        for user in [self.user, self.admin_user]:
            auth_models.NotificationSettings.objects.create(
                sms_notifications=True,
                email_notifications=True,
                lang='ru',
                user=user
            )
        post_data = {
            'eventvisitors-users': self.admin_user.id,
            'eventproposals-users': self.user.id,
            'event-description': 'test event',
            'event-preliminary_price': 23242,
            'event-start_at': '2016-02-16 17:51',
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 302)

        mail_notifications = {
            i[0][0]: i[0][-1] for i in fake_send_mail.call_args_list}
        expected_mail_notifications = {
            'create_visit': [self.admin_user.email],
            'create_proposal': [self.user.email]
        }
        self.assertEqual(mail_notifications, expected_mail_notifications)


    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       CELERY_ALWAYS_EAGER=True,
                       BROKER_BACKEND='memory',
                       SITE_DOMAIN=domain,
                       EMAIL_FROM = domain_mail)
    @patch('let_me_app.tasks.render_to_string')
    @patch('let_me_app.tasks.send_mail')
    def test_email_no_mail_for_me(self, fake_send_mail, fake_render):
        fake_render.return_value = self.fake_body
        self.client.login(
            email=self.admin_user.email,
            password=self.admin_user.first_name
        )

        user = factories.UserFactory(email='id123213.vk-oauth2@no.mail.for.me')
        url = reverse('let_me_app:create_proposal', kwargs={'pk': self.event.id})
        for u in [self.user, user]:
            auth_models.NotificationSettings.objects.create(
                sms_notifications=False,
                email_notifications=True,
                lang='ru',
                user=u
            )
        response = self.client.post(url, {'users': [user.id, self.user.id]})
        self.assertEqual(response.status_code, 302)
        fake_render.assert_called_with(
            'notifications/email/create_proposal.html',
            {
               'event': self.event,
               'event_url': '%s/let/me/view/event/%s/' % (self.domain, self.event.id)
            }
        )
        fake_send_mail.assert_called_with(
            'create_proposal',
            self.fake_body,
            self.domain_mail,
            [self.user.email],
            html_message=self.fake_body
        )


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

