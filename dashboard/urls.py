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
    path('manage-userslist/',views.ManageUserView.as_view(),name='ManageUserLists'),
    path('show-user-details/<int:id>/',views.ShowUserDetailsView.as_view(),name='ShowUserDetails'),
    path('add-userdata/',views.AddUserView.as_view(),name='AddUser'),
    path('show-ticketlist/',views.RaiseTicketListView.as_view(),name='RaiseTicketList'),
    path('ticket-details/<int:id>/',views.TicketDetailPageView.as_view(),name='TicketDetailPage'),
    path('ticket-particular-delete/<int:id>/',views.TicketParticularDeleteView.as_view(),name='TicketParticularDelete'),
    path('show-notificationlists/',views.NotificationListsView.as_view(),name='NotificationLists'),
    path('show-receive-notification/',views.NotificationreceiveView.as_view(),name='Notificationreceive'),
    
]
