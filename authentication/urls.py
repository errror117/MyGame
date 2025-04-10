from django.urls import path
from .views import register, login, admin_dashboard
from .views import ProtectedView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('admin-dashboard/', admin_dashboard, name='admin-dashboard'),
]

urlpatterns += [
    path('protected/', ProtectedView.as_view(), name='protected'),
]    