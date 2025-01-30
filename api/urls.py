from django.urls import path
from . import views

urlpatterns = [
    path('user-login/',views.UserLoginView.as_view(),name='UserLogin'),
    path('user-profile-detail/',views.UserProfileView.as_view(),name='UserProfile'),
    path('user-email-verification/',views.UserEmailVerificationView.as_view(),name='UserEmailVerification'),
    path('verify-send-otp-user/',views.UserVerifyOtpView.as_view(),name='UserVerifyOtp'),
    path('reset-user-password/',views.ResetUserPasswordView.as_view(),name='ResetUserPassword'),
    path('user-add-raise-ticket/',views.UserRaiseTicketView.as_view(),name='UserRaiseTicket'),
    path('show-raised-ticket/',views.ShowRaisedTicketDataView.as_view(),name='ShowRaisedTicketData'),
    path('show-particular-ticket-data/',views.ShowParticularTicketDrtailsView.as_view(),name='ShowParticularTicketDrtails'),
    path('add-satisfaction-score/',views.AddSatisfactionScoreView.as_view(),name='AddSatisfactionScore'),
    path('feedback-details/',views.ShowTicketFeedbackView.as_view(),name='ShowTicketFeedback'),
    path('show-receiver-niotification/',views.ShowNotificationView.as_view(),name='ShowReceiverNotification'),
    path('show-number-notification/',views.NotificationNumberView.as_view(),name='NotificationNumber'),
    path('particular-notification-delete/',views.ParticularNotificationDeleteView.as_view(),name='ParticularNotificationDelete'),
    path('delete-all-notification/',views.ClearAllNotificationView.as_view(),name='ClearAllNotification'),
    path('send-chat-ticket/',views.ChatTicketCreateView.as_view(),name='ChatTicketCreate'),
    path('show-chat-ticket/',views.ShowTicketChatView.as_view(),name='ShowTicketChat')

    
]
