'''
Created on Jul 4, 2015

@author: oleg
'''
from django import template
from django.core.urlresolvers import reverse

register = template.Library()


@register.filter
def as_status(value, status_choices):
    return dict(status_choices)[value]


#@register.inclusion_tag('escort/follow_menu.html')
#def dropdown_follow_by_user(followable, user, redirect_to):
#    is_followed = False
#    for peeper in followable.peeper_set.all():
#        if peeper.user_id == user.id:
#            is_followed = True
#    return {
#        'followable': followable,
#        'is_followed': is_followed,
#        'redirect_to': redirect_to
#    }


@register.tag(name='followdropdown')
def dropdown_follow_by_user(parser, token):
    nodelist = parser.parse(('endfollowdropdown',))
    parser.delete_first_token()
    variables = token.split_contents()
    return FollowDropdownNode(nodelist, variables[1], variables[2])


class FollowDropdownNode(template.Node):
    def __init__(self, nodelist, followable_context_name, template_name):
        self.followable = template.Variable(followable_context_name)
        self.template_name = template.Variable(template_name)
        self.nodelist = nodelist

    def render(self, context):
        followable = self.followable.resolve(context)
        template_name  = self.template_name.resolve(context)

        request = context['request']
        is_followed = False
        for peeper in followable.followers.all():
            if peeper.user_id == request.user.id:
                is_followed = True

        inner_text = self.nodelist.render(context)

        if is_followed:
            action_url = reverse(
                'let_me_escort:stop_escort_followable', kwargs={'pk': followable.id}
            )
        else:
            action_url = reverse(
                'let_me_escort:escort_followable', kwargs={'pk': followable.id}
            )

        node_template = template.loader.get_template(template_name)
        data = {
            'csrf_token': context['csrf_token'],
            'request': context['request'],
            'inner_text': inner_text,
            'form_action_url': action_url,
            'is_followed': is_followed
        }
        template_context = template.Context(data)
        return node_template.render(template_context)
