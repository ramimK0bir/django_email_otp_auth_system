from django.urls import  path
# import views here
from home import views
urlpatterns = [
    path('', views.home, name='IndexHOME'),
    path('login/', views.login, name='LoginHOME'),
    path('signup/', views.signup, name='SignupHOME'),
    path('logout/', views.logout, name='LogoutHOME'),
    path('verify/', views.verify, name='VerifyHOME'),
    path('my_account/', views.myAccount, name='MyAccountHOME'),
    path('reset_password/', views.resetPassword, name='PasswordResetHOME'),
]
