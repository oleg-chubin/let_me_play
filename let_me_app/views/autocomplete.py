from dal import autocomplete
from slugify import slugify

from let_me_auth.models import User
from let_me_app.models import Equipment, StaffRole
from let_me_auth.social.pipeline import ABSENT_MAIL_HOST
import re


class UserAutocomplete(autocomplete.Select2QuerySetView):
    create_field = 'username'

    def create_object(self, text):
        cell_phone = re.findall(r'\+?(\d{9,12})', text)
        if cell_phone:
            cell_phone = cell_phone[0]
            text = re.sub(r'\+?(\d{9,12})', '', text).strip()
        parts = text.split(' ', 1)
        first_name = parts[0].strip()
        email_parts = [slugify(first_name)]
        defaults = {'first_name': first_name}
        if len(parts) > 1:
            last_name = parts[1].strip()
            defaults['last_name'] = last_name
            email_parts.append(slugify(last_name))
        email = '@'.join(['.'.join(email_parts), ABSENT_MAIL_HOST])
        if cell_phone:
            required = {'cell_phone': cell_phone}
            defaults.update({'email': email})
        else:
            required = {'email': email}
        user, _ = User.objects.get_or_create(defaults=defaults, **required)
        return user

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
