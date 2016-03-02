from dal import autocomplete
from slugify import slugify

from let_me_auth.models import User
from let_me_app.models import Equipment, StaffRole


class UserAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return User.objects.none()

        qs = User.objects.all()

        if self.q:
            qs = User.objects.filter(first_name__istartswith=self.q)
            qs = qs | User.objects.filter(last_name__istartswith=self.q)
            qs = qs | User.objects.filter(email__istartswith=self.q)

        return qs


class EquipmentAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Equipment.objects.none()

        qs = Equipment.objects.all()

        if self.q:
            qs = Equipment.objects.filter(name__istartswith=self.q)

        return qs


class StaffRoleAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return StaffRole.objects.none()

        qs = StaffRole.objects.all()

        if self.q:
            qs = StaffRole.objects.filter(name__istartswith=self.q)

        return qs
