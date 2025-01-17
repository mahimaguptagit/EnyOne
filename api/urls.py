from django.urls import path
from . import views

urlpatterns = [
    path('user-login/',views.UserLoginView.as_view(),name='UserLogin'),
    path('user-profile-detail/',views.UserProfileView.as_view(),name='UserProfile'),
    path('user-add-raise-ticket/',views.UserRaiseTicketView.as_view(),name='UserRaiseTicket'),
    path('show-raised-ticket/',views.ShowRaisedTicketDataView.as_view(),name='ShowRaisedTicketData'),
    path('show-particular-ticket-data/',views.ShowParticularTicketDrtailsView.as_view(),name='ShowParticularTicketDrtails')
    
]
