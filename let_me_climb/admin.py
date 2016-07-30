from django.contrib import admin
from let_me_climb.models import Participant


class ParticipantAdmin(admin.ModelAdmin):
    fields = ['last_name', 'first_name', 'middle_name',
              'sex', 'birth_date', 'sport_level',
              'country', 'city', 'phone', 'email',
              'avatar']
    list_display = ('last_name', 'first_name', 'middle_name',
                    'sex', 'birth_date', 'sport_level',
                    'country', 'city', 'phone')

admin.site.register(Participant, ParticipantAdmin)
