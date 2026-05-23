from django.contrib.auth import authenticate

from django.shortcuts import render, reverse, redirect
from django.http import Http404, HttpResponse
import random
from django.contrib.auth.models import User
from utility.models import Otp
from django.utils import timezone
from datetime import timedelta
from smtp_mail_sender import send_email, generate_otp
from utility.models import SiteSettings
from role import can_access_, routes_of_

import re

ALLOWED_DOMAINS = {'gmail.com'}


class EmailValidator:
    _pattern = re.compile(r'^([a-zA-Z0-9._%+\-]+)@([a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})$')

    def validate(self, email):
        match = self._pattern.match(email.strip().lower())
        if not match:
            return (-1, None)
        local, domain = match.group(1), match.group(2)
        normalized = f'{local}@{domain}'
        if domain not in ALLOWED_DOMAINS:
            return (0, normalized)
        return (1, normalized)


def load_site_settings():
    site_settings = SiteSettings.objects.all()

    if site_settings:
        site_settings = site_settings[0]

        site_name = site_settings.siteName
        site_fav_icon_link = site_settings.siteFavIconLink

    else:
        site_name = "BD-pay"
        site_fav_icon_link = "https://chatgpt.com/favicon.ico"
    return {
        "site_name": site_name,
        "site_fav_icon_link": site_fav_icon_link,
    }


class PrepareParams:

    def home(self, request, params={}):
        params = load_site_settings() | params
        params['active'] = "Home"
        user_role = request.session.get('user_role', 'viewer')
        allowed_routes = routes_of_(user_role)
        params['routes'] = list([(x, reverse(allowed_routes[x])) for x in allowed_routes])
        return params

    def login(self, request, params={}):
        params = load_site_settings() | params
        params['active'] = "Login"
        user_role = request.session.get('user_role', 'viewer')
        allowed_routes = routes_of_(user_role)
        params['routes'] = list([(x, reverse(allowed_routes[x])) for x in allowed_routes])
        return params

    def signup(self, request, params={}):
        params = load_site_settings() | params
        params['active'] = "Signup"
        user_role = request.session.get('user_role', 'viewer')
        allowed_routes = routes_of_(user_role)
        params['routes'] = list([(x, reverse(allowed_routes[x])) for x in allowed_routes])
        return params

    def password_reset(self, request, params={}):
        params = load_site_settings() | params
        params['active'] = "Password Reset"
        user_role = request.session.get('user_role', 'viewer')
        allowed_routes = routes_of_(user_role)
        params['routes'] = list([(x, reverse(allowed_routes[x])) for x in allowed_routes])
        return params

    def verify(self, request, params={}):
        params = load_site_settings() | params
        params['active'] = "Verify Account"
        user_role = request.session.get('user_role', 'viewer')
        allowed_routes = routes_of_(user_role)
        params['routes'] = list([(x, reverse(allowed_routes[x])) for x in allowed_routes])
        return params

    def myAccount(self, request, params={}):
        params = load_site_settings() | params
        params['active'] = "My Account"
        user_role = request.session.get('user_role', 'viewer')
        allowed_routes = routes_of_(user_role)
        params['routes'] = list([(x, reverse(allowed_routes[x])) for x in allowed_routes])
        return params


params_loader = PrepareParams()
email_validator = EmailValidator()


def home(request):
    if can_access_('IndexHOME', request.session.get('user_role', 'viewer')):
        raise Http404("404 Page not found...")
    if request.session.get('user_role', 'viewer') == 'unverified_user':
        return redirect(to='VerifyHOME')
    params = params_loader.home(request)
    return render(request, 'home/index.html', params)


def login(request):
    if can_access_('LoginHOME', request.session.get('user_role', 'viewer')):
        raise Http404("404 Page not found...")
    if request.session.get('user_role', 'viewer') == "unverified_user":
        return redirect(to='VerifyHOME')
    elif request.session.get('user_role', 'viewer') == "verified_user":
        return render(request, 'home/index.html',
                      params_loader.home(request, {'message': {'body': 'Already logged in.', 'type': 'warning'}}))

    if request.method == "POST":
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        if (not (email and password)) or (email_validator.validate(email)[0] != 1):
            params = params_loader.login(request,
                                         {'message': {'body': 'Fill the form correctly.', "type": "warning"}})
            return render(request, 'home/login.html', params)
        else:
            email = email_validator.validate(email)[1]
            user_temp = User.objects.filter(email=email)
            if not user_temp:
                params = params_loader.login(request, {'message': {'type': 'danger', 'body': 'Login failed.Try again.'},
                                                       'credential': {'email': email}})
                return render(request, 'home/login.html', params)
            username = user_temp[0].username
            user = authenticate(username=username, password=password)
            if user:
                request.session['username'] = username
                request.session['email'] = email
                request.session['user_role'] = 'unverified_user'
                params = params_loader.home(request, {'message': {'type': 'success', 'body': 'Login successful.'}})
                return redirect(to='VerifyHOME')
                # return render(request, 'home/index.html', params)
            else:
                params = params_loader.login(request, {'message': {'type': 'danger', 'body': 'Login failed.Try again.'},
                                                       'credential': {'email': email}})
            return render(request, 'home/login.html', params)
    return render(request, "home/login.html", params_loader.login(request))


def signup(request):
    if can_access_('SignupHOME', request.session.get('user_role', 'viewer')):
        raise Http404("404 Page not found...")
    elif request.session.get('user_role', 'viewer') == "unverified_user":
        return redirect(to='VerifyHOME')
    elif request.session.get('user_role', 'viewer') == "verified_user":
        return render(request, 'home/index.html',
                      params_loader.home(request, {'message': {'body': 'Already logged in.', 'type': 'warning'}}))

    if request.method == "POST":
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password', '')
        password2 = request.POST.get('confirm_password', '')
        if not all([first_name, last_name, email, password1, password2]):
            params = params_loader.signup(request, {'message': {'body': 'Please fill all fields', "type": "warning"}})
            return render(request, 'home/signup.html', params)
        elif len(first_name) < 2 or len(last_name) < 2 or len(password1) < 8:
            params = params_loader.signup(request, {'message': {'body': 'Fill the form correctly.', "type": "warning"}})
            return render(request, 'home/signup.html', params)
        validated = email_validator.validate(email)
        if validated[0] == -1:
            params = params_loader.signup(request,
                                          {'message': {'body': 'Enter a valid email address', "type": "danger"},
                                           'credential': {'firstName': first_name, 'lastName': last_name},
                                           })
            return render(request, 'home/signup.html', params)
        elif validated[0] == 0:
            params = params_loader.signup(request,
                                          {'message': {'body': 'Only gmail addresses are allowed', "type": "warning"},
                                           'credential': {'firstName': first_name, 'lastName': last_name},
                                           })
            return render(request, 'home/signup.html', params)
        elif validated[0] == 1:
            email = validated[1]
        if password1 != password2:
            params = params_loader.signup(request, {'message': {'body': 'Passwords do not match', "type": "danger"},
                                                    'credential': {'firstName': first_name, 'lastName': last_name,
                                                                   'email': email},
                                                    })
            return render(request, 'home/signup.html', params)
        user = User.objects.filter(email=email)
        if user:
            params = params_loader.signup(request, {
                'message': {'body': f"This email '{email}' already exist.Try with another email.", "type": "warning"},
                'credential': {'firstName': first_name, 'lastName': last_name}
            })
            return render(request, 'home/signup.html', params)
        else:
            x = [chr(y) for y in range(97, 123)]
            site_settings = SiteSettings.objects.all()[0]
            uid = site_settings.uUid
            site_settings.uUid = str(int(uid) + 1)
            site_settings.save()
            username = f'PayId{uid}{random.choice(x)}'
            user = User.objects.create_user(username=username, email=email, password=password1, first_name=first_name,
                                            last_name=last_name)
            request.session['username'] = username
            request.session['email'] = email
            request.session['user_role'] = 'unverified_user'

            return redirect(to="VerifyHOME")

    params = params_loader.signup(request)
    return render(request, 'home/signup.html', params)


def logout(request):
    if can_access_('LogoutHOME', request.session.get('user_role', 'viewer')):
        raise Http404("404 Page not found...")
    if not request.session.get('username', ''):
        return render(request, 'home/login.html',
                      params_loader.home(request, {'message': {'body': 'Not logged in.', 'type': 'warning'}}))
    request.session.flush()
    return render(request, 'home/login.html',
                  params_loader.home(request, {'message': {'body': 'Logout successful.', 'type': 'success'}}))


def verify(request):
    if can_access_('VerifyHOME', request.session.get('user_role', 'viewer')):
        raise Http404("404 Page not found...")
    email = request.session.get('email', '')
    resend = request.GET.get('resend', False)
    Otp.objects.filter(created_at__lt=timezone.now() - timedelta(minutes=5)).delete()

    otps = Otp.objects.filter(email=email,purpose='login')
    if not otps:
        generated_otp = generate_otp()
        send_email(email, "OTP", f'{generated_otp} is your login verification OTP.',    SiteSettings.objects.first().siteLink )
        Otp.objects.create(email=email, otp_code=generated_otp, purpose='login')
        if resend:
            return render(request, 'home/verify.html', params_loader.verify(request,
                                                                            {'email': request.session.get('email', ''),
                                                                             'message': {
                                                                                 'body': 'New OTP has been sent.',
                                                                                 'type': 'success'}}))
    if resend:
        return render(request, 'home/verify.html', params_loader.verify(request,
                                                                        {'email': request.session.get('email', ''),
                                                                         'message': {
                                                                             'body': "Already sent withing 5 min.Try again after 5 min.",
                                                                             'type': 'warning'}}))

    if request.method == 'POST':
        otp_code = request.POST.get('otp', "")
        if otp_code:

            if otp_code.isnumeric():
                if len(otp_code) == 6:
                    otp = Otp.objects.filter(email=email, otp_code=otp_code, purpose= 'login')
                    if otp:
                        request.session['user_role'] = 'verified_user'
                        otp[0].delete()
                        return redirect(to="IndexHOME")
                    return render(request, 'home/verify.html', params_loader.verify(request, {
                        'email': request.session.get('email', ''),
                        'message': {'body': 'Wrong OTP.Try again', 'type': 'danger'}}))

        return render(request, 'home/verify.html', params_loader.verify(request,
                                                                        {'email': request.session.get('email', ''),
                                                                         'message': {'body': 'Fill from properly.',
                                                                                     'type': 'warning'}}))

    return render(request, 'home/verify.html',
                  params_loader.verify(request, {'email': request.session.get('email', '')}))


def myAccount(request):
    if can_access_('MyAccountHOME', request.session.get('user_role', 'viewer')):
        raise Http404("404 Page not found...")
    user = User.objects.filter(email=request.session.get('email', ''))[0]
    email = user.email

    params = {
        'credential': {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'email': user.email,
            'status': 'active',
        }
    }

    return render(request, 'home/my_account.html', params_loader.myAccount(request, params))



def resetPassword(request):
    step = 1
    if request.session.get('password_reset_email','')  :
        step = 2
    if request.session.get('otp_matched', False) :
        step = 3

    if step == 1 :
        if request.method == 'POST':
            email = request.POST.get('email', '').strip()
            validated = email_validator.validate(email)
            if validated[0] != 1:
                return render(request, 'home/password_reset.html', params_loader.password_reset(request, {'step': 1,
                                                                                                          'message': {
                                                                                                              'body': 'Enter a valid gmail address.',
                                                                                                              'type': 'danger'}}))
            email = validated[1]
            user = User.objects.filter(email=email)
            if user:
                request.session['password_reset_email'] = email
                Otp.objects.filter(created_at__lt=timezone.now() - timedelta(minutes=5)).delete()
                otps = Otp.objects.filter(email=email, purpose='password_reset')
                if not otps:
                    generated_otp = generate_otp()
                    send_email(email, "OTP", f'{generated_otp} is your password reset OTP.',
                               SiteSettings.objects.first().siteLink)
                    Otp.objects.create(email=email, otp_code=generated_otp, purpose='password_reset')



                return render(request, 'home/password_reset.html', params_loader.password_reset(request, {'step': 2,
                                                                                                          'message': {
                                                                                                              'body': "Email submitted successfully.",
                                                                                                              'type': 'success'}}))
            else:
                return render(request, 'home/password_reset.html', params_loader.password_reset(request, {'step': 1,
                                                                                                          'message': {
                                                                                                              'body': f"There's no user with this '{email}' email.",
                                                                                                              'type': 'warning'}}))
    if step == 2 :
        if request.method == 'POST':
            if not request.session.get('password_reset_email', ''):
                return render(request, 'home/password_reset.html',
                              params_loader.password_reset(request, {'step': 1}))
            email = request.session.get('password_reset_email')
            Otp.objects.filter(created_at__lt=timezone.now() - timedelta(minutes=5)).delete()
            otp_code= request.POST.get('otp', "")
            code_matched= Otp.objects.filter(email=email , otp_code=otp_code, purpose= 'password_reset'  )
            if code_matched :
                request.session['otp_matched'] = True
                code_matched.first().delete()
                return render(request, 'home/password_reset.html',
                              params_loader.password_reset(request, {'step': 3,
                                                                     'message': {'body': 'OTP matched.',
                                                                                 'type': 'success'}}))
            else:
                return render(request, 'home/password_reset.html',
                              params_loader.password_reset(request, {'step': 2,
                                                                     'message': {'body': 'OTP not matched.Try again',
                                                                                 'type': 'danger'}, 'credential':{'email':email }     }))
        email = request.session.get('password_reset_email')

        resend = request.GET.get('resend', False)
        otps = Otp.objects.filter(email=email, purpose='password_reset')
        if not otps:
            generated_otp = generate_otp()
            send_email(email, "OTP", f'{generated_otp} is your password reset OTP.',
                       SiteSettings.objects.first().siteLink)
            Otp.objects.create(email=email, otp_code=generated_otp, purpose='password_reset')
            if resend:
                return render(request, 'home/password_reset.html',
                              params_loader.password_reset(request, {'step': 2,
                                                                     'message': {'body': 'Otp sent successfully.',
                                                                                 'type': 'success'}, 'credential':{'email':email } }))

        if resend:
                return render(request, 'home/password_reset.html',
                              params_loader.password_reset(request, {'step': 2, 'message': {
                                  'body': "Already sent withing 5 min.Try again after 5 min.", 'type': 'warning'}, 'credential':{'email':email } }))

        return render(request, 'home/password_reset.html',
                      params_loader.password_reset(request, {'step': 2, 'credential':{'email':email } }))

    if step == 3:
        if request.method == 'POST':
            password1 = request.POST.get('password', "")
            password2 = request.POST.get('confirm_password', "")
            if len(password1) < 8 or len(password2) < 8:
                return render(request, 'home/password_reset.html', params_loader.password_reset(request, {'step': step,
                                                                                                          'message': {
                                                                                                              'body': "Fill the form correctly.",
                                                                                                              "type": "danger"}}))

            elif password1 != password2:
                return  render(request, 'home/password_reset.html', params_loader.password_reset(request, {'step': step, 'message':{'body':"Passwords do not match.","type":"warning"}        }))
            email = request.session.get('password_reset_email', '').strip().lower()
            user = User.objects.filter(email=email)
            if user:
                if user[0] :
                    user[0].set_password(password1)
                    user[0].save()
                    request.session.flush()
                    return render(request, 'home/password_reset.html', params_loader.password_reset(request, {'step': 4}))


    return render(request, 'home/password_reset.html', params_loader.password_reset(request, {'step': step}))




