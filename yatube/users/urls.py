# users/urls.py
import django.contrib.auth.views as auth
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'login/',
        auth.LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        'logout/',
        auth.LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path(
        'password_change/',
        auth.PasswordChangeView.as_view(
            template_name='users/password_change_form.html'
        ),
        name='password_change_form'
    ),
    path(
        'password_change/done/',
        auth.PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html'
        ),
        name='password_change_done'
    ),
    path(
        'password_reset/',
        auth.PasswordResetView.as_view(
            template_name='users/password_reset_form.html'
        ),
        name='password_reset_form'
    ),
    path(
        'password_reset/done/',
        auth.PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        auth.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'
        ),
        name='password_reset_complete'
    )
]
