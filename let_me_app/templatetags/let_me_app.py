from django import template
import markdown
from let_me_app import models
from django.utils.translation import gettext
from django.utils import timezone


register = template.Library()


@register.filter
def markdownify(text):
    # safe_mode governs how the function handles raw HTML
    return markdown.markdown(text, safe_mode='escape')

@register.filter
def is_visit(obj):
    return isinstance(obj, models.Visit)

@register.filter
def is_application(obj):
    return isinstance(obj, models.Application)

@register.filter
def is_proposal(obj):
    return isinstance(obj, models.Proposal)

@register.filter
def model_name(obj):
    return gettext(obj.__class__.__name__)

@register.filter
def is_outdated(obj):
    if (obj.event.status != models.EventStatuses.PENDING
            or obj.event.start_at < timezone.now()):
        return True
    if isinstance(obj, models.Proposal):
        return obj.status != models.ProposalStatuses.ACTIVE
    if isinstance(obj, models.Application):
        return obj.status != models.ApplicationStatuses.ACTIVE
    if isinstance(obj, models.Visit):
        return obj.status != models.VisitStatuses.PENDING
    return True

