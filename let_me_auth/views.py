from django.shortcuts import redirect, render
from django.conf import settings
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
# from django.template.context import RequestContext
from annoying.decorators import render_to
from django.template.context import RequestContext


def context(**extra):
    return dict(**extra)


def login(request):
    # context = RequestContext(request, {
    #     'request': request, 'user': request.user})
    # return render_to_response('login.html', context_instance=context)
    context = {'next_url': request.REQUEST.get('next', reverse('home'))}
    return render(
        request, 'login.html',
        context_instance = RequestContext(request, context)
    )


@login_required()
def home(request):
    return redirect(reverse(settings.DEFAULT_VIEW_NAME))


def logout(request):
    """Logs out user"""
    auth_logout(request)
    return redirect('/')


@login_required
@render_to('home.html')
def done(request):
    """Login complete view, displays user data"""
    return context()


@render_to('login.html')
def validation_sent(request):
    return context(
        validation_sent=True,
        email=request.session.get('email_validation_address')
    )


@render_to('login.html')
def require_email(request):
    backend = request.session['partial_pipeline']['backend']
    return context(email_required=True, backend=backend)


@render_to('login.html')
def signup(request):
    return context(signup=True)


