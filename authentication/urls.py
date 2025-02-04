from django.urls import path
from .views import register, login
from .views import ProtectedView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # JWT login endpoint
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Refresh token endpoint
]

urlpatterns += [
    path('protected/', ProtectedView.as_view(), name='protected'),
]    