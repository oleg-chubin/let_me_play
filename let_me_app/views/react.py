from django.views.generic.base import TemplateView


class ReactEventList(TemplateView):
    template_name = 'react/events_list.html'
