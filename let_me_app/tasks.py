from celery import task
from django.core.mail import send_mail
from django.conf import settings

import logging
from django.template.loader import render_to_string
from let_me_app import models
from let_me_auth import models as auth_models
from django.core.mail.message import EmailMultiAlternatives
from let_me_app.integration.rocketsms import RocketLauncher
from django.template.base import TemplateDoesNotExist
from django.core.urlresolvers import reverse
from contextlib import contextmanager
from django.utils import translation
from functools import wraps
from let_me_auth.pipeline import ABSENT_MAIL_HOST
logger = logging.getLogger(__name__)


sms_sender = RocketLauncher(**settings.ROCKET_SMS_CONFIG)

def send_sms(phone_number, text):
    sms_sender.send_sms(phone_number, text.strip())


@contextmanager
def render_language(lang):
    cur_language = translation.get_language()
    try:
        translation.activate(lang)
        yield lang
    finally:
        translation.activate(cur_language)


def skip_absent_templates(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TemplateDoesNotExist as e:
            logger.info(
                "template does not exist and skipped %s", e
            )
    return wrapped


class MailNotificator:
    def _send_mail(self, mail_list, subject, body):
        send_mail(
            subject, body, settings.EMAIL_FROM, mail_list, fail_silently=False
        )

    def process_notification(self, notification_context):
        try:
            reason = notification_context['reason']
        except KeyError:
            logger.error(
                "notification context %s doesn't have a reason",
                notification_context
            )
            return

        try:
            preprocessor = getattr(self, reason)
        except AttributeError:
            logger.error(
                "MailNotificator does not have preprocessor for %s", reason
            )

        mail_info = preprocessor(notification_context)

        for user_list, context in mail_info:
            self._notify_user_list(user_list, context, reason)

    def _split_sms_and_mail_notifications(self, user_list):
        mail_list = []
        phone_list = []
        notify_settings = auth_models.NotificationSettings.objects.filter(
            user_id__in=[i.id for i in user_list]
        )
        notify_settings = {i.user_id: i for i in notify_settings}
        for user in user_list:
            if user.id not in notify_settings:
                continue
            if notify_settings[user.id].email_notifications:
                mail_list.append(user.email)
            if (notify_settings[user.id].sms_notifications
                    and user.cell_phone_is_valid):
                phone_list.append(user.cell_phone)
        return mail_list, phone_list

    @skip_absent_templates
    def _render_and_send_sms(self, phone_list, context, reason):
        if not phone_list:
            return

        sms_template = "notifications/sms/{}.html".format(reason)
        sms_text = render_to_string(sms_template, context)
        for phone_number in phone_list:
            send_sms(phone_number, sms_text)

    @skip_absent_templates
    def _render_and_send_mail(self, mail_list, context, reason):
        mail_list = [
            i for i in mail_list if i.split('@')[-1] != ABSENT_MAIL_HOST
        ]
        if not mail_list:
            return

        mail_template = "notifications/email/{}.html".format(reason)

        if 'event' in context:
            context['event_url'] = "".join([
                settings.SITE_DOMAIN,
                reverse(
                    "let_me_app:view_event",
                    kwargs={'pk': context['event'].id})
            ])
        mail_body = render_to_string(mail_template, context)
        send_mail(
            reason, mail_body, settings.EMAIL_FROM, mail_list,
            html_message=mail_body
        )

    def _notify_user_list(self, user_list, context, reason):
        if not user_list:
            return

        mail_list, phone_list = self._split_sms_and_mail_notifications(user_list)

        # TODO: rework me to render notifications according to their NotificationSettings
        language = 'ru'
        with render_language(language):
            self._render_and_send_sms(phone_list, context, reason)
            self._render_and_send_mail(mail_list, context, reason)


    def new_chat_message(self,  notification_context):
        participants = models.ChatParticipant.objects.filter(
            chat_id=notification_context['message_id']
        ).select_related('user')

        context = {
            'chat_id': notification_context['message_id'],
            'chat_url': "".join([
                settings.SITE_DOMAIN,
                reverse(
                    "let_me_app:chat_details",
                    kwargs={'pk': notification_context['message_id']})
            ])

        }

        initiator = notification_context['initiator_id']
        user_list = [i.user for i in participants if i.user_id!=initiator]
        return [[user_list, context], ]

    def cancel_application(self,  notification_context):
        application_ids = notification_context['object_ids']
        applications = models.Application.objects.filter(
            id__in=application_ids).select_related('user', 'event')
        apps_by_events = {}
        events = {}
        for app in applications:
            events[app.event.id] = app.event
            app_list = apps_by_events.setdefault(app.event.id, [])
            app_list.append(app)

        mail_info = []
        for event_id, app_list in apps_by_events.items():
            event = events[event_id]
            user_list = event.court.admin_group.user_set.all()
            context = {'event': event, 'users': [a.user for a in app_list]}
            mail_info.append([user_list, context])
        return mail_info

    def create_application(self,  notification_context):
        application_ids = notification_context['object_ids']
        applications = models.Application.objects.filter(
            id__in=application_ids).select_related('user', 'event')
        apps_by_events = {}
        events = {}
        for app in applications:
            events[app.event.id] = app.event
            app_list = apps_by_events.setdefault(app.event.id, [])
            app_list.append(app)

        mail_info = []
        for event_id, app_list in apps_by_events.items():
            event = events[event_id]
            user_list = event.court.admin_group.user_set.all()
            context = {'event': event, 'users': [a.user for a in app_list]}
            mail_info.append([user_list, context])
        return mail_info

    def create_proposal(self,  notification_context):
        proposal_ids = notification_context['object_ids']
        proposals = models.Proposal.objects.filter(
            id__in=proposal_ids).select_related('user', 'event')

        mail_info = []
        for proposal in proposals:
            context = {'event': proposal.event}
            mail_info.append([[proposal.user], context])
        return mail_info

    def create_visit(self,  notification_context):
        visit_ids = notification_context['object_ids']
        visits = models.Visit.objects.filter(
            id__in=visit_ids).select_related('user', 'event')

        mail_info = []
        for visit in visits:
            context = {'event': visit.event}
            mail_info.append([[visit.user], context])
        return mail_info

    def decline_proposal(self,  notification_context):
        proposal_ids = notification_context['object_ids']
        proposals = models.Proposal.objects.filter(
            id__in=proposal_ids).select_related('user', 'event')
        proposals_by_events = {}
        events = {}
        for proposal in proposals:
            events[proposal.event.id] = proposal.event
            app_list = proposals_by_events.setdefault(proposal.event.id, [])
            app_list.append(proposal)

        mail_info = []
        for event_id, proposal_list in proposals_by_events.items():
            event = events[event_id]
            user_list = event.court.admin_group.user_set.all()
            context = {
                'event': event,
                'users': [a.user for a in proposal_list]
            }
            mail_info.append([user_list, context])
        return mail_info

    def accept_proposal(self,  notification_context):
        proposal_ids = notification_context['object_ids']
        proposals = models.Proposal.objects.filter(
            id__in=proposal_ids).select_related('user', 'event')
        proposals_by_events = {}
        events = {}
        for proposal in proposals:
            events[proposal.event.id] = proposal.event
            app_list = proposals_by_events.setdefault(proposal.event.id, [])
            app_list.append(proposal)

        mail_info = []
        for event_id, proposal_list in proposals_by_events.items():
            event = events[event_id]
            user_list = event.court.admin_group.user_set.all()
            context = {
                'event': event,
                'users': [a.user for a in proposal_list]
            }
            mail_info.append([user_list, context])
        return mail_info

    def decline_application(self,  notification_context):
        application_ids = notification_context['object_ids']
        applications = models.Application.objects.filter(
            id__in=application_ids).select_related('user', 'event')

        mail_info = []
        for application in applications:
            context = {'event': application.event}
            mail_info.append([[application.user], context])
        return mail_info

    def accept_application(self,  notification_context):
        application_ids = notification_context['object_ids']
        applications = models.Application.objects.filter(
            id__in=application_ids).select_related('user', 'event')

        mail_info = []
        for application in applications:
            context = {'event': application.event, 'user': application.user}
            mail_info.append([[application.user], context])
        return mail_info

    def cancel_visit(self,  notification_context):
        visit_ids = notification_context['object_ids']
        visits = models.Visit.objects.filter(
            id__in=visit_ids).select_related('user', 'event')
        visits_by_events = {}
        events = {}
        for visit in visits:
            events[visit.event.id] = visit.event
            app_list = visits_by_events.setdefault(visit.event.id, [])
            app_list.append(visit)

        mail_info = []
        for event_id, visit_list in visits_by_events.items():
            event = events[event_id]
            user_list = event.court.admin_group.user_set.all()
            context = {
                'event': event,
                'user': visit_list and visit_list[0].user
            }
            mail_info.append([user_list, context])
        return mail_info

    def decline_visit(self,  notification_context):
        visit_ids = notification_context['object_ids']
        visits = models.Visit.objects.filter(
            id__in=visit_ids).select_related('user', 'event')

        mail_info = []
        for visit in visits:
            context = {'event': visit.event}
            mail_info.append([[visit.user], context])
        return mail_info

    def cancel_proposal(self,  notification_context):
        proposal_ids = notification_context['object_ids']
        proposals = models.Proposal.objects.filter(
            id__in=proposal_ids).select_related('user', 'event')

        mail_info = []
        for proposal in proposals:
            context = {'event': proposal.event}
            mail_info.append([[proposal.user], context])
        return mail_info

    def cancel_event(self,  notification_context):
        event_ids = notification_context['object_ids']
        events = models.Event.objects.filter(id__in=event_ids)

        mail_info = []
        for event in events:
            context = {'event': event}
            visits = event.visit_set.filter(
                status=models.VisitStatuses.DECLINED)
            visits = visits.select_related('user')
            mail_info.append([[i.user for i in visits], context])
        return mail_info

    def create_event(self,  notification_context):
        return []


mail_notifier = MailNotificator()

@task
def send_notification(notification_context):
    logger.debug("process data %s initiated", notification_context)
    mail_notifier.process_notification(notification_context)
