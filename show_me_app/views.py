'''
Created on Jul 5, 2015

@author: oleg
'''
import json
from django import http
from let_me_app import models
from django.db.models import get_model
from django.views.generic.base import View as BaseView
from django.views.generic.list import ListView
from django.db import transaction
from django.db.models.aggregates import Count, Max, Min, Sum
from let_me_auth.models import User
import itertools
from let_me_app.models import Visit


class CourtListView(ListView):
    model = models.Court
    template_name = 'reports/courts.html'

    def get_context_data(self, *args, **kwargs):
        result = super(CourtListView, self).get_context_data(*args, **kwargs)
        courts = result['object_list']
        visitors = Visit.objects.filter(
            event__court_id__in=courts.values_list('followable_ptr_id', flat=True))
        visitors = visitors.values('event__court_id')
        visitors = visitors.annotate(user_count=Count('user_id', distinct=True))
        visitors = {v['event__court_id']: v['user_count'] for v in visitors}
        visitors_count = []
        for court in courts:
            visitors_count.append(visitors.get(court.id, 0))
        result['visitors_count'] = visitors_count
        return result

    def get_queryset(self, **kwargs):
        result = super(CourtListView, self).get_queryset(**kwargs)
        result = result.filter(admin_group__user=self.request.user)
        result = result.annotate(events_count=Count('event__id'))
        result = result.annotate(first_event=Min('event__start_at'))
        result = result.annotate(last_event=Max('event__start_at'))
        return result.order_by('-events_count')


class CourtEventsView(ListView):
    model = models.Event
    template_name = 'reports/court_events.html'

    def check_permissions(self, *args, **kwargs):
        if not models.Court.objects.filter(
                admin_group__user=self.request.user).exists():
            raise http.HttpResponseForbidden()

    def get_context_data(self, *args, **kwargs):
        result = super(CourtEventsView, self).get_context_data(*args, **kwargs)
        self.check_permissions(*args, **kwargs)
        visitors_payments = models.Visit.objects.filter(
            event_id__in=result['object_list'].values_list('id', flat=True),
            status=models.VisitStatuses.COMPLETED)
        visitors_payments = visitors_payments.values('event_id').annotate(
            price=Sum('receipt__price'))
        visitors_payment = {i['event_id']: i['price'] for i in visitors_payments}
        result['payment'] = [
            (visitors_payment.get(e.id) or 0) for e in result['object_list']
        ]
        visitors = models.Visit.objects.filter(
            event_id__in=result['object_list'].values_list('id', flat=True),
            status=models.VisitStatuses.COMPLETED)
        visitors = visitors.values('event_id').annotate(count=Count('id'))
        visitors = {i['event_id']: i['count'] for i in visitors}
        result['visitors'] = [
            (visitors.get(e.id) or 0) for e in result['object_list']
        ]

        return result

    def get_queryset(self, **kwargs):
        result = super(CourtEventsView, self).get_queryset(**kwargs)
        result = result.filter(court_id=self.kwargs['pk']).order_by('start_at')
        return result.annotate(
            attendees_count=Count('visit__user_id', distinct=True))


class CourtVisitorsView(ListView):
    model = models.Visit
    template_name = 'reports/court_visitors.html'

    def check_permissions(self, *args, **kwargs):
        if not models.Court.objects.filter(
                admin_group__user=self.request.user).exists():
            raise http.HttpResponseForbidden()

    def get_context_data(self, *args, **kwargs):
        result = super(CourtVisitorsView, self).get_context_data(*args, **kwargs)
        table_visits = result['object_list'].select_related('event', 'receipt')
        table_visits = table_visits.order_by('user_id', 'event__start_at')
        grouped_visits = itertools.groupby( table_visits, key=lambda x: x.user_id)

        self.check_permissions(*args, **kwargs)

        court_users = User.objects.filter(
            visit__event__court_id=self.kwargs['pk']).distinct().order_by('id')
        iter_court_users = iter(court_users)
        court_events = models.Event.objects.filter(
            court_id=self.kwargs['pk']).order_by('start_at')
        user = next(iter_court_users, None)
        result_table = []
        for user_id, visit_list in grouped_visits:
            result_row = []
            result_table.append(result_row)
            while user and user_id > user.id:
                user = next(iter_court_users, None)

            visit = next(visit_list, None)
            for event in court_events:
                visit_to_store = None
                if user and user.id == user_id:
                    while visit and visit.event.start_at < event.start_at:
                        visit = next(visit_list, None)
                    if visit and visit.event.start_at == event.start_at:
                        visit_to_store = visit
                result_row.append(visit_to_store)
        result['visit_table'] = result_table
        result['events'] = court_events
        result['users'] = court_users

        payments = result['object_list'].filter(status=models.VisitStatuses.COMPLETED)
        payments = payments.exclude(receipt__price=None)
        payments = payments.values('user_id')
        payments = payments.annotate(paid=Sum('receipt__price'), debt=Sum('event__preliminary_price'))
        total_payment = {v['user_id']: v for v in payments}
        payment_data = []
        for user in court_users:
            payment_info = total_payment.get(user.id, {'paid': 0, 'debt': 0})
            payment_data.append(payment_info['paid'] - payment_info ['debt'])
        result['total_payment'] = payment_data
        return result

    def get_queryset(self):
        result = super(CourtVisitorsView, self).get_queryset()
        result = result.filter(event__court_id=self.kwargs['pk'])
        return result



class UserVisitsView(ListView):
    model = models.Visit
    template_name = 'reports/user_visits.html'

    def get_context_data(self, *args, **kwargs):
        result = super(UserVisitsView, self).get_context_data(*args, **kwargs)
        table_visits = result['object_list'].select_related('event', 'receipt')
        table_visits = table_visits.order_by('event__court_id', 'event__start_at')
        grouped_visits = itertools.groupby(
            table_visits, key=lambda x: x.event.court_id)

        courts = models.Court.objects.filter(
            event__visit__user=self.request.user).distinct().order_by('followable_ptr_id')
        iter_courts = iter(courts)
        user_events = models.Event.objects.filter(
            visit__user=self.request.user).order_by('start_at')
        import ipdb; ipdb.set_trace()
        court = next(iter_courts, None)
        result_table = []
        for court_id, visit_list in grouped_visits:
            result_row = []
            result_table.append(result_row)
            while court and court_id > court.followable_ptr_id:
                court = next(iter_courts, None)

            visit = next(visit_list, None)
            for event in user_events:
                visit_to_store = None
                if court and court.followable_ptr_id == court_id:
                    while visit and visit.event.start_at < event.start_at:
                        visit = next(visit_list, None)
                    if visit and visit.event.start_at == event.start_at:
                        visit_to_store = visit
                result_row.append(visit_to_store)
        result['visit_table'] = result_table
        result['events'] = user_events
        result['courts'] = courts

        payments = result['object_list'].filter(status=models.VisitStatuses.COMPLETED)
        payments = payments.exclude(receipt__price=None)
        payments = payments.values('event__court_id')
        payments = payments.annotate(paid=Sum('receipt__price'), debt=Sum('event__preliminary_price'))
        total_payment = {v['event__court_id']: v for v in payments}
        payment_data = []
        for user in courts:
            payment_info = total_payment.get(user.followable_ptr_id, {'paid': 0, 'debt': 0})
            payment_data.append(payment_info['paid'] - payment_info ['debt'])
        result['total_payment'] = payment_data
        return result

    def get_queryset(self):
        result = super(UserVisitsView, self).get_queryset()
        return result.filter(user_id=self.request.user.id)
