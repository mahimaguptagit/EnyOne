from django.core.mail import send_mail
import random
from django.conf import settings
from .models import User


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



  
    
   