from django.conf.urls import url
from let_me_app.views.autocomplete import (UserAutocomplete,
    EquipmentAutocomplete, StaffRoleAutocomplete)

urlpatterns = [
    url(
        'autocomplete/user/$',
        UserAutocomplete.as_view(),
        name='user-autocomplete',
    ),
    url(
        'autocomplete/equipment/$',
        EquipmentAutocomplete.as_view(),
        name='equipment-autocomplete',
    ),
    url(
        'autocomplete/staffrole/$',
        StaffRoleAutocomplete.as_view(),
        name='staffrole-autocomplete',
    ),
]
