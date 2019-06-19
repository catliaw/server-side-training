from django.contrib.auth import authenticate
from django.contrib.auth import login as log_in
from django.contrib.auth import logout as log_out
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from images.forms import SignUpForm
from images.forms import LoginForm
from mixpanel import Mixpanel
import datetime
import json
import urllib


mp = Mixpanel("71444cfc3c55b4714b0c83f0b4220a9b")


def index(request):
    """Return the logged in page, or the logged out page
    """
    print('Index view!')
    if request.user.is_authenticated():
        return render(request, 'images/index-logged-in.html', {
            'user': request.user
        })
    else:
        return render(request, 'images/index-logged-out.html')

def _get_distinct_id(request):
    """Gets distinct_id from client-side cookie.
    """
    raw_cookie = request.COOKIES['mp_71444cfc3c55b4714b0c83f0b4220a9b_mixpanel']
    json_cookie = json.loads(urllib.unquote(raw_cookie).decode('utf8'))
    d_id = json_cookie['distinct_id']
    return d_id

def signup(request):
    """Render the Signup form or a process a signup
    """
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        # import pdb; pdb.set_trace()

        if form.is_valid():
            form.save()
            distinct_id = _get_distinct_id(request)
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            
            user = authenticate(username=username, password=raw_password)
            
            mp.alias(username, distinct_id)
            
            log_in(request, user)

            mp.track(distinct_id, 'Signup', {
                'Username': username,
                'Signup Date': datetime.datetime.now()
                })
            mp.people_set(distinct_id, {
                'Username': username,
                'Signup Date': now_time,
                'Number of Logins': 1,
                'Number of Images': 1
                })

            return HttpResponseRedirect('/')

    else:
        form = SignUpForm()

    return render(request, 'images/signup.html', {'form': form})


def login(request):
    """Render the login form or log in the user
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            mp.track(username, 'Login', {
                'Username': username
                })
            mp.people_increment(username, {
                'Number of Logins': 1
                })
            log_in(request, user)
            return HttpResponseRedirect('/')
        else:
            return render(request, 'images/login.html', {
                'form': LoginForm,
                'error': 'Please try again'
            })

    else:
        return render(request, 'images/login.html', {'form': LoginForm})

# def save_profile(request):
#     profile = Profile.objects.get(email=request.user.email)
#     distinct_id = form.cleaned_data.get('distinct_id')
#     mp.alias(profile.email, distinct_id)


def logout(request):
    """Logout the user
    """

    log_out(request)

    return HttpResponseRedirect('/')
