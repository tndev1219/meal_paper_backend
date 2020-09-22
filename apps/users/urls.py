from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'login/', views.Login.as_view(), name='login'),
    url(r'forgot-password/', views.ForgotPasswordAPIView.as_view(), name='forgot_password'),
    url(r'reset-password/(?P<reset_key>\w+)/$', views.ResetPasswordAPIView.as_view(), name='reset_password'),
    url(r'reset-email/', views.ResetEmail.as_view(), name='reset_email'),
    url(r'change-password/', views.ChangePassword.as_view(), name='change_password'),
    url(r'signup/', views.SignUpAPIView.as_view(), name='sign_up'),
]
