from social.strategies.django_strategy import DjangoStrategy
from django.template import TemplateDoesNotExist, RequestContext, loader
from django.conf import settings


class FixedDjangoStrategy(DjangoStrategy):
    def render_html(self, tpl=None, html=None, context=None):
        if not tpl and not html:
            raise ValueError('Missing template or html parameters')
        context = context or {}
        try:
            template = loader.get_template(tpl)
        except TemplateDoesNotExist:
            template = loader.get_template_from_string(html)
        return template.render(
            RequestContext(
                self.request,
                context,
                processors=settings.TEMPLATES[0]['OPTIONS']['context_processors']),
                request=self.request)


class CustomDjangoStrategy(FixedDjangoStrategy):
    def get_pipeline(self):
        return self.setting('INNER_PIPELINE')



