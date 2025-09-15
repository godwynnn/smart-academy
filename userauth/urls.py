from django.urls import path,re_path
from .views import *
from django.conf.urls.static import static
from django.conf import settings
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('register/',SignupView.as_view(),name='register'),
    path('activate/account/',VerifyOTPView.as_view(),name='activate_account'),
    path('login/',LoginView.as_view(),name='login'),
     path('logout/',LogoutView.as_view(),name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    re_path('verify/'+ r'social/(?P<backend>[^/]+)/$',VerifySocialLogin,name='verify_social'),
    path('password/change/',RequestVerifyPasswordChangeView.as_view(),name='password_change'),
   
]