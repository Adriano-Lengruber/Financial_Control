from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    LogoutView,
    ProfileView,
    ChangePasswordView,
    user_stats,
    delete_account
)

urlpatterns = [
    # Autenticação
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Perfil
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('stats/', user_stats, name='user_stats'),
    path('delete-account/', delete_account, name='delete_account'),
]
