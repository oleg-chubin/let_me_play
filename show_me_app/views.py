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


class CourtListView(ListView):
    model = models.Court
    template_name = 'reports/courts.html'

    def get_context_data(self, *args, **kwargs):
        result = super(CourtListView, self).get_context_data(*args, **kwargs)
        return result

    def get_queryset(self, **kwargs):
        result = super(CourtListView, self).get_queryset(**kwargs).select_related('site')
        result = result.annotate(events_count=Count('event__id'))
        result = result.annotate(first_event=Min('event__start_at'))
        result = result.annotate(last_event=Max('event__start_at'))
        return result


class CourtEventsView(ListView):
    model = models.Event
    template_name = 'reports/court_events.html'

    def get_context_data(self, *args, **kwargs):
        result = super(CourtEventsView, self).get_context_data(*args, **kwargs)
        return result

    def get_queryset(self, **kwargs):
        result = super(CourtEventsView, self).get_queryset(**kwargs)
        result = result.order_by('start_at')
        result = result.annotate(visitors_count=Count('visit__id'))


class CourtVisitorsView(ListView):
    model = models.Visit
    template_name = 'reports/court_visitors.html'

    def get_context_data(self, *args, **kwargs):
        result = super(CourtVisitorsView, self).get_context_data(*args, **kwargs)
        grouped_visits = itertools.groupby(
            result['object_list'], key=lambda x: x.user_id)
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
        return result

    def get_queryset(self):
        result = super(CourtVisitorsView, self).get_queryset()
        result = result.filter(event__court_id=self.kwargs['pk'])
        result = result.select_related('event', 'receipt')
        result = result.order_by('user_id', 'event__start_at')
        return result
