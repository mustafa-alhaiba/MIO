from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from apps.accounts.api import views
urlpatterns = [
    #authentication endpoints
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # User profile endpoint
    path('me/', views.UserProfileView.as_view(), name='user_profile'),
]