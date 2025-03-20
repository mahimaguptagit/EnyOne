from django.core.mail import send_mail
import random
from django.conf import settings
from .models import *
import firebase_admin
from firebase_admin import credentials, messaging, exceptions


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
        admindata=User.objects.filter(is_superuser=True,is_admin=True).first()
        Notification.objects.create(sender=admindata,receiver=userdata,notification_title=subject,notification_description=message)
        registration_token = userdata.phone_verify  
        print(f"User FCM Token: {registration_token}")
        if registration_token:  
            send_push_notification(registration_token, subject, message)
        else:
            print("Error: No FCM token found for the user.")

def send_resolved_ticket(email,refernce_number,userdata):
        ticket_number=refernce_number
        subject='Regarding Ticket Status'
        message=f'Ticket has been resolved successfully for reference number - {ticket_number}'
        from_email=settings.EMAIL_HOST_USER
        send_mail(subject,message,from_email,[email])
        admindata=User.objects.filter(is_superuser=True,is_admin=True).first()
        Notification.objects.create(sender=admindata,receiver=userdata,notification_title=subject,notification_description=message)
        registration_token = userdata.phone_verify  
        print(f"User FCM Token: {registration_token}")
        if registration_token:  
            send_push_notification(registration_token, subject, message)
        else:
            print("Error: No FCM token found for the user.")

cred = credentials.Certificate(settings.FCM_PATH)
firebase_admin.initialize_app(cred)

def send_push_notification(registration_token, title, body):
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=registration_token, 
        )
        response = messaging.send(message)
        print('Successfully sent message:', response)
        return response
    
    except exceptions.FirebaseError as e:  
        print(f"Firebase Error: {e}")

    except Exception as e:
        print(f"Unexpected Error: {e}")




  
    
   