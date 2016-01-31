from django import template
from django.conf import settings

register = template.Library()

@register.filter
def avatar_url(user):
    if user.avatar:
        return user.avatar.url
    else:
        return '/'.join(
            [settings.STATIC_URL.rstrip('/'), "images/default.png"])
