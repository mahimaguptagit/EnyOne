from django.urls import path
from . import views

urlpatterns = [
    path('admin-login/',views.AdminLoginView.as_view(),name='AdminLogin'),
    path('admin-dashboard/',views.AdminDashboardView.as_view(),name='AdminDashboard')
    
]
