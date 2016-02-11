from celery import task
from django.core.mail import send_mail
from django.conf import settings

import logging
from django.template.loader import render_to_string
from let_me_app import models
from django.core.mail.message import EmailMultiAlternatives
logger = logging.getLogger(__name__)


@task
def mytask(a, b):
    return a + b


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

        template_name = "notifications/email/{}.html".format(reason)

        try:
            preprocessor = getattr(self, reason)
        except AttributeError:
            logger.error(
                "MailNotificator does not have preprocessor for %s", reason
            )

        mail_info = preprocessor(notification_context)

        for mail_list, context in mail_info:
            if not mail_list:
                continue
            context['SITE_DOMAIN'] = settings.SITE_DOMAIN
            mail_body = render_to_string(template_name, context)

            msg = EmailMultiAlternatives(
                reason, mail_body, settings.EMAIL_FROM, mail_list)
            msg.attach_alternative(mail_body, "text/html")
            msg.send()

    def new_chat_message(self,  notification_context):
        participants = models.ChatParticipant.objects.filter(
            chat_id=notification_context['message_id']
        ).select_related('user')

        context = {'chat_id': notification_context['message_id']}

        initiator = notification_context['initiator_id']
        mail_list = [i.user.email for i in participants if i.user_id!=initiator]
        return [mail_list, context]

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
            mail_list = [i.email for i in event.court.admin_group.user_set.all()]
            context = {'event': event, 'users': [a.user for a in app_list]}
            mail_info.append([mail_list, context])
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
            mail_list = [i.email for i in event.court.admin_group.user_set.all()]
            context = {'event': event, 'users': [a.user for a in app_list]}
            mail_info.append([mail_list, context])
        return mail_info

    def create_proposal(self,  notification_context):
        proposal_ids = notification_context['object_ids']
        proposals = models.Proposal.objects.filter(
            id__in=proposal_ids).select_related('user', 'event')

        mail_info = []
        for proposal in proposals:
            context = {'event': proposal.event}
            mail_info.append([[proposal.user.email], context])
        return mail_info

    def create_visit(self,  notification_context):
        visit_ids = notification_context['object_ids']
        visits = models.Visit.objects.filter(
            id__in=visit_ids).select_related('user', 'event')

        mail_info = []
        for visit in visits:
            context = {'event': visit.event}
            mail_info.append([[visit.user.email], context])
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
            mail_list = [i.email for i in event.court.admin_group.user_set.all()]
            context = {
                'event': event,
                'users': [a.user for a in proposal_list]
            }
            mail_info.append([mail_list, context])
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
            mail_list = [i.email for i in event.court.admin_group.user_set.all()]
            context = {
                'event': event,
                'users': [a.user for a in proposal_list]
            }
            mail_info.append([mail_list, context])
        return mail_info

    def decline_application(self,  notification_context):
        application_ids = notification_context['object_ids']
        applications = models.Application.objects.filter(
            id__in=application_ids).select_related('user', 'event')

        mail_info = []
        for application in applications:
            context = {'event': application.event}
            mail_info.append([[application.user.email], context])
        return mail_info

    def accept_application(self,  notification_context):
        application_ids = notification_context['object_ids']
        applications = models.Visit.objects.filter(
            id__in=application_ids).select_related('user', 'event')

        mail_info = []
        for application in applications:
            context = {'event': application.event}
            mail_info.append([[application.user.email], context])
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
            mail_list = [i.email for i in event.court.admin_group.user_set.all()]
            context = {
                'event': event,
                'users': [a.user for a in visit_list]
            }
            mail_info.append([mail_list, context])
        return mail_info

    def decline_visit(self,  notification_context):
        visit_ids = notification_context['object_ids']
        visits = models.Visit.objects.filter(
            id__in=visit_ids).select_related('user', 'event')

        mail_info = []
        for visit in visits:
            context = {'event': visit.event}
            mail_info.append([[visit.user.email], context])
        return mail_info

    def cancel_proposal(self,  notification_context):
        proposal_ids = notification_context['object_ids']
        proposals = models.Proposal.objects.filter(
            id__in=proposal_ids).select_related('user', 'event')

        mail_info = []
        for proposal in proposals:
            context = {'event': proposal.event}
            mail_info.append([[proposal.user.email], context])
        return mail_info

    def cancel_event(self,  notification_context):
        return []

    def create_event(self,  notification_context):
        return []


mail_notifier = MailNotificator()

@task
def send_notification(notification_context):
    logger.debug("process data %s initiated", notification_context)
    mail_notifier.process_notification(notification_context)
