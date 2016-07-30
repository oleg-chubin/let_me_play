from django.contrib import admin
from let_me_climb.models import Participant, Route, ResultTable


class ParticipantAdmin(admin.ModelAdmin):
    fields = ['last_name', 'first_name', 'middle_name',
              'sex', 'birth_date', 'sport_level',
              'country', 'city', 'phone', 'email',
              'avatar']
    list_display = ('last_name', 'first_name', 'middle_name',
                    'sex', 'birth_date', 'sport_level',
                    'country', 'city', 'phone')


class RouteAdmin(admin.ModelAdmin):
    fields = ['route_number', 'route_color',
              'route_score', 'route_onsite_percent']
    list_display = ('route_number', 'route_color',
                    'route_score', 'route_onsite_percent',)


class ResultTableAdmin(admin.ModelAdmin):
    list_display = ('participant', 'score',)


admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Route, RouteAdmin)
admin.site.register(ResultTable, ResultTableAdmin)

