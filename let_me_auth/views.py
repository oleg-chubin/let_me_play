from django.shortcuts import redirect, render
from django.conf import settings
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
# from django.template.context import RequestContext
from annoying.decorators import render_to
from django.template.context import RequestContext
from django.contrib.auth.forms import SetPasswordForm
from django import forms
from let_me_auth.models import User
from django.views.generic.edit import UpdateView
from let_me_auth.forms import UserDetailsForm


def context(**extra):
    return dict(**extra)


def login(request):
    context = {'next_url': request.REQUEST.get('next', reverse('home'))}
    return render(
        request, 'registration/login.html',
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


@render_to('registration/login.html')
def validation_sent(request):
    return context(
        validation_sent=True,
        email=request.session.get('email_validation_address')
    )


class CustomSetPasswordForm(SetPasswordForm):
    verification_code = forms.CharField(widget=forms.HiddenInput)

    def save(self, commit=True):
        self.user.is_active = True
        return super(CustomSetPasswordForm, self).save(commit=commit)


@render_to('registration/login.html')
def set_password(request):
    post_reset_redirect = "/"
    code = request.REQUEST.get('verification_code')
    user = User.objects.filter(newcomer__code=code)[:1]
    if not user or user[0].is_active:
        return redirect('login')
    else:
        user = user[0]

    if request.method == 'POST':
        form = CustomSetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            return redirect(post_reset_redirect)
    else:
        form = CustomSetPasswordForm(user, initial={'verification_code': code})
    return {'form': form, 'initial_password': True}


@render_to('registration/login.html')
def require_email(request):
    backend = request.session['partial_pipeline']['backend']
    return context(email_required=True, backend=backend)


@render_to('registration/login.html')
def signup(request):
    return context(signup=True)


class EditUserView(UpdateView):
    form_class = UserDetailsForm
    template_name = 'user/details_form.html'

    def get_success_url(self):
        return reverse('let_me_auth:update_profile')

    def get_object(self):
        return self.request.user.user
