from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet
from extra_views.generic import GenericInlineFormSet

from . import models


class OccasionInline(InlineFormSet):
    model = models.Occasion


class BookingPolicyInline(InlineFormSet):
    model = models.BookingPolicy


class CreateCourtView(CreateWithInlinesView):
    model = models.Court
    inlines = [BookingPolicyInline, OccasionInline]

    def get_context_data(self, *args, **kwargs):
        res = super().get_context_data(*args, **kwargs)
        return res


