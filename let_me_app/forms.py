import floppyforms.__future__ as forms

from . import models


class OccasionForm(forms.ModelForm):
    class Meta:
        model = models.Occasion
        widgets = {
            'start_at': forms.Select,
            'duration': forms.NumberInput,
            'period': forms.NumberInput,
            'equipment': forms.Select
        }


class BookingPolicyForm(forms.ModelForm):
    class Meta:
        model = models.BookingPolicy
        widgets = {
            'court': forms.Select,
            'group': forms.Select,
            'early_registration': forms.NumberInput,
            'price': forms.NumberInput
        }


class CourtForm(forms.ModelForm):
    class Meta:
        model = models.Court
        widgets = {
            'site': forms.Select,
            'admin_group': forms.Select,
            'description': forms.Textarea
        }


class SiteForm(forms.ModelForm):
    class Meta:
        model = models.Site
        widgets = {
            'name': forms.TextInput,
            'map_image': forms.FileInput,
            'description': forms.Textarea,
            'address': forms.Textarea
        }
