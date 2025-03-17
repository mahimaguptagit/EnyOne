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
    path('staff-dashboard/',views.StaffDashboardView.as_view(),name='StaffDashboard'),
    path('manage-userslist/',views.ManageUserView.as_view(),name='ManageUserLists'),
    path('show-user-details/<int:id>/',views.ShowUserDetailsView.as_view(),name='ShowUserDetails'),
    path('add-userdata/',views.AddUserView.as_view(),name='AddUser'),
    path('manage-stafflist/',views.ManageStaffView.as_view(),name='ManageStaff'),
    path('show-staff-detail/<int:id>/',views.ShowStaffDetailsView.as_view(),name='ShowStaffDetails'),
    path('add-staffuser/',views.AddStaffView.as_view(),name='AddStaff'),
    path('update-staff/<int:id>/',views.UpdateStaffDetailsView.as_view(),name='UpdateStaffDetails'),
    path('delete-staff/<int:id>/',views.DeleteStaffDetailsView.as_view(),name='DeleteStaffDetails'),
    path('show-ticketlist/',views.RaiseTicketListView.as_view(),name='RaiseTicketList'),
    path('show-issuelist/',views.RaiseIssueListView.as_view(),name='RaiseIssueList'),
    path('show-requestlist/',views.RaiseRequestListView.as_view(),name='RaiseRequestList'),
    path('ticket-details/<int:id>/',views.TicketDetailPageView.as_view(),name='TicketDetailPage'),
    path('ticket-update-detail/<int:id>/',views.TicketUpdateDetailsView.as_view(),name='TicketUpdateDetails'),
    path('ticket-particular-delete/<int:id>/',views.TicketParticularDeleteView.as_view(),name='TicketParticularDelete'),
    path('ticket-feedback-lists/',views.TicketFeedbackView.as_view(),name='TicketFeedback'),
    path('ticket-feedbackdetails/<int:id>/',views.TicketFeedbackDetailPageView.as_view(),name='TicketFeedbackDetailPage'),
    path('ticket-feedback-delete/<int:id>/',views.TicketFeedbackDeleteView.as_view(),name='TicketFeedbackDelete'),
    path('show-notificationlists/',views.NotificationListsView.as_view(),name='NotificationLists'),
    path('show-receive-notification/',views.NotificationreceiveView.as_view(),name='Notificationreceive'),
    path('add-notification/',views.AddNotificationView.as_view(),name='AddNotification'),
    path('delete-admin-notification/<int:id>/',views.DeleteAdminParticularNotificationView.as_view(),name='DeleteAdminNotification'),
    path('chat-send/<int:id>/',views.ChatSendReceiveView.as_view(),name='ChatSendReceive')
    
]
