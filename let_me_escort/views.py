'''
Created on Jul 5, 2015

@author: oleg
'''
import json
from let_me_app import models
from django.db.models import get_model
from django.views.generic.list import ListView

class DashboardView(ListView):
    model = models.Changelog
    template_name = 'dashboard/list.html'

    def get_context_data(self, *args, **kwargs):
        result = super(DashboardView, self).get_context_data(*args, **kwargs)
        decoded_list = []
        for i in result['object_list']:
            data = json.loads(i.text)
            data['date'] = i.created_at
            data['followable'] = i.followable_id
            decoded_list.append(data)
        object_by_models = {}
        for data in decoded_list:
            object_by_models.setdefault(data['model'], set()).add(data['id'])

        objects = {}
        for model_name, pks in object_by_models.items():
            model = get_model(model_name)
            objects[model_name] = {i.pk: i for i in model.objects.filter(pk__in=pks)}
        for data in decoded_list:
            data['object'] = objects[data['model']][data['id']]
        result['decoded_list'] = decoded_list
        return result

    def get_queryset(self, **kwargs):
        result = super(DashboardView, self).get_queryset(**kwargs)
        return result.filter(followable__followers__user=self.request.user).order_by('-created_at')