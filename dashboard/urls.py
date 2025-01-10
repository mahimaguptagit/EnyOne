from django.urls import path
from . import views

urlpatterns = [
    path('admin-login/',views.AdminLoginView.as_view(),name='AdminLogin'),
    path('admin-logout/',views.admin_logout,name='AdminLogOut'),
    path('admin-update-profile/<int:id>/',views.AdminUpdateProfileView.as_view(),name='AdminUpdateProfile'),
    path('admin-change-password/',views.AdminChangePasswordView.as_view(),name='AdminChangePassword'),
    path('verify-otp/',views.VerifyOtpView.as_view(),name='VerifyOtp'),
    path('email-verification/',views.EmailVerificationView.as_view(),name='EmailVerification'),
    path('admin-forget-password/',views.AdminForgetPasswordView.as_view(),name='AdminForgetPassword'),
    path('admin-dashboard/',views.AdminDashboardView.as_view(),name='AdminDashboard'),
    path('analytical-dashboard/',views.AnalyticDashboardView.as_view(),name='AnalyticDashboard'),
    path('show-ticketlist/',views.RaiseTicketListView.as_view(),name='RaiseTicketList')
    
]
