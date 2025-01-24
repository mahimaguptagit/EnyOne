from django.core.mail import send_mail
import random
from django.conf import settings
from .models import *


def send_otp(email):
        subject='OTP for Reset Password'
        otp=random.randint(1000,9999)
        # print(subject)
        # print(otp)
        message=f'Your OTP for reset password is {otp}'
        from_email=settings.EMAIL_HOST_USER
        send_mail(subject,message,from_email,[email])
        user=User.objects.get(email=email)
        user.otp=otp
        user.save()

def send_acknowleadgemnet_confirm(email,refernce_number,userdata):
        ticket_number=refernce_number
        subject='Regarding Ticket Status'
        message=f'Ticket has been received successfully . Reference Number of ticket is {ticket_number} for tracking '
        from_email=settings.EMAIL_HOST_USER
        send_mail(subject,message,from_email,[email])
        admindata=User.objects.filter(is_superuser=True,is_admin=True)
        Notification.objects.create(sender=admindata,receiver=userdata,notification_title=subject,notification_description=message)

def send_resolved_ticket(email,refernce_number,userdata):
        ticket_number=refernce_number
        subject='Regarding Ticket Status'
        message=f'Ticket has been resolved successfully for reference number - {ticket_number}'
        from_email=settings.EMAIL_HOST_USER
        send_mail(subject,message,from_email,[email])
        admindata=User.objects.filter(is_superuser=True,is_admin=True)
        Notification.objects.create(sender=admindata,receiver=userdata,notification_title=subject,notification_description=message)



  
    
   