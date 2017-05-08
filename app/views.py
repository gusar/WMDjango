import urllib2

from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from django.forms import ValidationError
from django.views.generic.edit import UpdateView

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import forms


@login_required
def logout_view(request):
    logout(request)
    return redirect(reverse('app:login'))


@login_required
def landing(request):
    return render(request, 'app/landing.html')


def login_view(request):
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    return redirect(reverse('app:landing'))
                else:
                    form.add_error(None, ValidationError("Your account is not active."))
            else:
                form.add_error(None, ValidationError("Invalid User Id of Password"))
    else:
        form = forms.LoginForm()

    return render(request, 'app/login.html', {'form': form})


def signup_view(request):
    if request.POST:
        form = forms.SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                user = get_user_model().objects.get(username=username)
                if user:
                    form.add_error(None, ValidationError("This user already exists."))
            except get_user_model().DoesNotExist:
                user = get_user_model().objects.create_user(username=username)

                user.set_password(password)
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.save()

                return redirect(reverse('app:login'))
    else:
        form = forms.SignupForm()

    return render(request, 'app/signup.html', {'form': form})


class UserProfile(UpdateView):
    form_class = forms.UserProfileForm
    template_name = "app/user_profile.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserProfile, self).dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        return get_user_model().objects.get(pk=self.request.user.pk)


    @api_view(["GET", ])
    @permission_classes((IsAuthenticated,))
    @csrf_exempt
    def get_station_data(request):
        stationFile = urllib2.urlopen(
            'https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey=f8ea8c86300204fae0f3231a3664c4c2e499bea5')
        stationData = stationFile.read()
        stationFile.close()
        for item in stationData:
            print(item)
        return Response(stationData, status=200)