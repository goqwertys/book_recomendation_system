from django.urls import path

from users.apps import UsersConfig
from users.views import RegisterView, LoginView, LogoutView, ProfileView, ProfileUpdateView, my_profile_redirect

app_name = UsersConfig.name

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('<int:pk>/', ProfileView.as_view(), name='profile'),
    path('profile/', my_profile_redirect, name='my-profile'),
    path('edit/', ProfileUpdateView.as_view(), name='edit-profile'),
]
