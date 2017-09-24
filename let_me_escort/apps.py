'''
Created on Jul 5, 2015

@author: oleg
'''
import json
from django.apps import AppConfig
from django.apps import apps
from django.db.models import signals
from django.db.models.fields.related import RelatedField
from django.dispatch import receiver
from let_me_escort import persistence


SIGNALS = []

class EscortAppConfig(AppConfig):
    name = 'let_me_escort'
    verbose_name = "Escort Application"

    def ready(self, *args, **kwargs):
        from let_me_app.models import Followable, Changelog
        followable_linked_models = []
        for model in apps.get_app_config('let_me_app').get_models():
            for field in model._meta.fields:
                if not isinstance(field, RelatedField):
                    continue
                for related_field in field.foreign_related_fields:
                    if (issubclass(related_field.model, Followable)
                            and not issubclass(model, Changelog)):
                        followable_linked_models.append((field.model, field.name))

        SIGNALS[:] = []
        for model, field_name in followable_linked_models:
            @receiver(signals.post_save, sender=model)
            def my_handler(sender, field_name=field_name, **kwargs):
                followable = getattr(kwargs['instance'], field_name)

                data = {
                    'text': 'created' if kwargs['created'] else 'updated',
                    'model': ".".join([sender._meta.app_label, sender.__name__]),
                    'id': kwargs['instance'].pk,
                    'followable_model': followable.__class__.__name__
                }
                Changelog.objects.create(
                    followable=followable, text=json.dumps(data)
                )

            SIGNALS.append(my_handler)

