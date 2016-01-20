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
        result = result.annotate(visitors_payment=Sum('visit__receipt__price'))
        return result
