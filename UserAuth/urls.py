from django.conf.urls import url, include
from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from . import views
from django.contrib.auth import views as auth_views
from django.views.decorators.csrf import csrf_exempt


# Registration,Login,Forgot,Profile change

urlpatterns = [

    path('create_user/', views.CreateUser.as_view(), name='CreateUser'),
    path('jwt/', obtain_jwt_token),
    path('jwt/refresh/', refresh_jwt_token),
    path('get_user/', views.UserInformation.as_view(), name="UserInformation"),
    path('manage_user/', views.ManageUser.as_view(), name='ManageUser'),
    path('change_password/', views.UpdatePassword.as_view(), name='UpdatePassword'),
    # url(r'^$', views.home, name='home'),
    # url(r'^signup/$', views.signup, name='signup'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    # url('api/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),

    path('accounts/', include('django.contrib.auth.urls')),
    path("password-reset/",auth_views.PasswordResetView.as_view( template_name="UserAuth/templates/account/password_reset.html"), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view( template_name="UserAuth/templates/account/password_reset_done.html"), name="password_reset_done"),
    path("password-reset-confirm/<uidb64>/<token>", auth_views.PasswordResetConfirmView.as_view( template_name="UserAuth/templates/account/password_reset_from.html"), name="password_reset_confirm"),
    path("password-reset-complete/", auth_views.PasswordResetCompleteView.as_view( template_name="UserAuth/templates/account/password_reset_complete.html"), name="password_reset_complete")
  
        

]
