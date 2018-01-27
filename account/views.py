from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import (
    get_user_model, login,
    authenticate, logout,
)
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone

from .forms import UserRegistrationForm, UserLoginForm
from .models import UserEmailVerification
from . import utils
# Create your views here.

User = get_user_model()


class HomePage(View):
    template_name = 'index.html'
    context = {
        'title': 'Home'
    }

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)


class UserRegistrationView(View):

    form_class = UserRegistrationForm
    template_name = 'form.html'
    context = {
        'title': 'User Registration',
    }

    def get(self, request, *args, **kwargs):
        #logged in user cannot access this view
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('index'))
        self.context['form'] = self.form_class()
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password'))
            user.save()
            #send email verification mail
            domain = get_current_site(request).domain   #gettings current domain to embed in verification mail
            key = UserEmailVerification.objects.create(user=user).key #creating key for email verification
            utils.send_email_verfication_mail(user.username, user.email, key, domain)

            messages.success(request, 'Your account has been created successfully.')
            messages.info(request, 
                "We have sent you an email, please verify your email to activate your account."
            )
            return self.get(request, *args, **kwargs)
        else:
            messages.error(request, "Invalid form submission.")
            self.context['form'] = form
            return render(request, self.template_name, self.context)


class UserEmailVerify(View):
    """
    This will be executed when the user will click on
    email verification link sent to his email.
    After opening the link sent to email address
    user must have to login in order to verify his email.
    """
    template_name = 'form.html'
    form_class = UserLoginForm
    context = {
        'title': 'Email Verification',
    }

    def get(self, request, *args, **kwargs):
        """
        returns login page
        """
        self.context['form'] = self.form_class
        messages.info(request, "Login to verfiy your email.")
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        """
        verify user passed valid login credentials
        and its the same user who has been sent the
        email varification link
        """
        key = kwargs['key']
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user.email_verification.key == key:
                if user.email_verification.is_valid_key:
                    if user.email_verified:
                        messages.info(request, "Your email is already verified.")
                        return HttpResponseRedirect(reverse('index'))
                    else:
                        user.email_verified = True
                        user.email_verification.is_valid_key = False
                        user.save()
                        login(request, user)
                        messages.success(request, "Your email has been successfully verified.")
                        return HttpResponseRedirect(reverse('index'))
                else:
                    messages.error(request, "Your email verification link is expired.")
            else:
                messages.error(request, "Invalid key.")
                return HttpResponseRedirect(reverse('index'))
            
        else:
            self.context['form'] = form
            return render(request, self.template_name, self.context)



class UserLoginView(View):

    form_class = UserLoginForm
    template_name = 'form.html'
    context = {
        'title': 'Login'
    }

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('index'))
        self.context['form'] = self.form_class
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        """
        Most of the validations are there in the UserLoginForm.
        """
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(username=username, password=password)

            
            if user.email_verified:
                login(request, user)
                messages.success(request, "You are successfully logged in.")

                return HttpResponseRedirect(reverse('index'))
            else:
                messages.info(request, "Please verify your email to access your account.")
                return render(request, self.template_name, self.context)
            
        else:
            self.context['form'] = form
            return render(request, self.template_name, self.context)


class UserLogoutView(View):

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')