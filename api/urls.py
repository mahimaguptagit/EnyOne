from django.urls import path
from . import views

urlpatterns = [
    path('user-login/',views.UserLoginView.as_view(),name='UserLogin'),
    path('user-profile-detail/',views.UserProfileView.as_view(),name='UserProfile')
    
]
