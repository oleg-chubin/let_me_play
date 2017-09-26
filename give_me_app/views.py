from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import authentication, permissions
from let_me_app import models, persistence
from give_me_app import serializers
from rest_framework.generics import get_object_or_404


class EventList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        queryset = models.Event.objects.all()
        queryset = queryset.select_related(
            'court__site', 'court__activity_type', 'inventory_list')
        result = persistence.filter_event_for_user(queryset, request.user)
        serialized = serializers.EventSerializer(result, many=True)
        return Response(serialized.data)
