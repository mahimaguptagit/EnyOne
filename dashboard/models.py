from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager

# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self,first_name,last_name,email,phone_number,address,image,username,password):
        user = self.model(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            address=address,
            username=username,
            image=image,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self,email,phone_number,username,password):
        user=self.model(
            email=email,
            phone_number=phone_number,
            username=username
        )
        user.set_password(password)
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = models.CharField(max_length=250,null=True,blank=True,unique=True)
    first_name = models.CharField(max_length=250,null=True,blank=True)
    last_name = models.CharField(max_length=250,null=True,blank=True)
    email = models.EmailField(verbose_name='Email', max_length=255, unique=True, null=True, blank=True)
    image = models.FileField(null=True, blank=True,upload_to='media')
    phone_number = models.CharField(max_length=15, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email','phone_number']

    def __str__(self):
        return self.username  

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True
    
    @property
    def is_staff(self):
        return self.is_admin


class Ticket(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='requested_tickets')
    ticket_type=models.CharField(max_length=225,null=True,blank=True)#issue or request for evolution
    ticket_title=models.CharField(max_length=225 , null = True,blank=True)
    ticket_description=models.CharField(max_length=225 , null = True,blank=True)
    ticket_number=models.CharField(max_length=225, null=True,blank=True)
    priority_level=models.CharField(max_length=225,null=True,blank=True)#e.g., Low, Medium, High
    ticket_file=models.FileField(upload_to='ticket_file/',blank=True,null=True)#with optional attachments/screenshots
    submission_status=models.CharField(max_length=50,default='Received',choices=[("Received","Received"),("In Progress","In Progress"),("Resolved","Resolved")])# e.g., Received, In Progress, Resolved
    assigned_request=models.ForeignKey(User,on_delete=models.CASCADE,related_name='assigned_tickets')#e.g., technical, feature development
    is_assign=models.BooleanField(default=False)
    solved_date=models.DateTimeField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    satisfaction_score=models.PositiveIntegerField(null=True,blank=True) 

class Report(models.Model):
    report_id=models.IntegerField(null=True,blank=True)
    report_name=models.CharField(max_length=225,null=True,blank=True)



    
   
