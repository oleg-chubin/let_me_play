from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet
from extra_views.generic import GenericInlineFormSet
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.core.urlresolvers import reverse
from . import models, forms


class SiteCreateView(CreateView):
    model = models.Site
    form_class = forms.SiteForm

    def get_success_url(self):
        return reverse('let_me_app:site-details', kwargs={'pk': self.object.id})


class SiteUpdateView(UpdateView):
    model = models.Site
    form_class = forms.SiteForm

    def get_success_url(self):
        return reverse('let_me_app:site-details', kwargs={'pk': self.object.id})


class SiteDetailView(DetailView):
    model = models.Site


class SiteListView(ListView):
    model = models.Site


class OccasionInline(InlineFormSet):
    model = models.Occasion
    form_class = forms.OccasionForm


class BookingPolicyInline(InlineFormSet):
    model = models.BookingPolicy
    form_class = forms.BookingPolicyForm


class CreateCourtView(CreateWithInlinesView):
    model = models.Court
    form_class = forms.CourtForm
    inlines = [BookingPolicyInline, OccasionInline]

    def get_context_data(self, *args, **kwargs):
        res = super().get_context_data(*args, **kwargs)
        return res
