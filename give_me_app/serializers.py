from rest_framework import serializers
from django.contrib.gis.geos import LineString, Point
from rest_framework.generics import get_object_or_404
from let_me_app import models


class GeoSerializer(serializers.Field):
    """
    Color objects are serialized into 'rgb(#, #, #)' notation.
    """
    def to_representation(self, obj):
        return obj.coords

    def to_internal_value(self, data):
        return Point(data)


class SiteSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='followable_ptr_id', read_only=True)
    geo_point = GeoSerializer()
    address = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()


class ActivityTypeSerializer(serializers.Serializer):
    image = serializers.SerializerMethodField(method_name='image_url')
    id = serializers.IntegerField()
    title = serializers.CharField()

    def image_url(self, obj):
        return obj.image.url if obj.image else ''


class CourtSerializer(serializers.Serializer):
    image = serializers.SerializerMethodField(method_name='image_url')
    id = serializers.IntegerField(source='followable_ptr_id', read_only=True)
    name = serializers.CharField()
    site = SiteSerializer()
    activity_type = ActivityTypeSerializer()
    description = serializers.CharField()

    def image_url(self, obj):
        return obj.image.url if obj.image else ''


class InventoryListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class EventSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='followable_ptr_id', read_only=True)
    start_at = serializers.DateTimeField()
    description = serializers.CharField()
    court = CourtSerializer()
    inventory_list = InventoryListSerializer()
    preliminary_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.ChoiceField(choices=models.EventStatuses.CHOICES)
