from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet
from extra_views.generic import GenericInlineFormSet

from . import models


class OccasionInline(InlineFormSet):
    model = models.Occasion


class BookingPolicyInline(GenericInlineFormSet):
    model = models.BookingPolicy


class CreateCourtView(CreateWithInlinesView):
    model = models.Court
    inlines = [BookingPolicyInline, OccasionInline]


