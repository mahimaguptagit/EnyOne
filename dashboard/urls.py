from django.urls import path
from . import views

urlpatterns = [
    path('admin-login/',views.AdminLoginView.as_view(),name='AdminLogin'),
    path('admin-update-profile/<int:id>/',views.AdminUpdateProfileView.as_view(),name='AdminUpdateProfile'),
    path('admin-dashboard/',views.AdminDashboardView.as_view(),name='AdminDashboard'),
    path('analytical-dashboard/',views.AnalyticDashboardView.as_view(),name='AnalyticDashboard'),
    path('show-ticketlist/',views.RaiseTicketListView.as_view(),name='RaiseTicketList')
    
]
