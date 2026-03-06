from django.urls import path
from .views import (
    UserRegisterView, DoctorRegisterView, HospitalRegisterView,
    LoginView, LogoutView, MeView, ChangePasswordView,
)

urlpatterns = [
    path('register/user/',     UserRegisterView.as_view(),     name='register-user'),
    path('register/doctor/',   DoctorRegisterView.as_view(),   name='register-doctor'),
    path('register/hospital/', HospitalRegisterView.as_view(), name='register-hospital'),
    path('login/',             LoginView.as_view(),             name='login'),
    path('logout/',            LogoutView.as_view(),            name='logout'),
    path('me/',                MeView.as_view(),                name='me'),
    path('change-password/',   ChangePasswordView.as_view(),   name='change-password'),
]