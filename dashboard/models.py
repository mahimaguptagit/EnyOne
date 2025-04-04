from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager

# Create your models here.

class Company(models.Model):
    company_id = models.IntegerField(primary_key=True, db_column='company_id')  
    company_name=models.CharField(max_length=225,null=True,blank=True)
    email=models.EmailField(max_length=225,null=True,blank=True)
    phone_number = models.CharField(max_length=15, unique=True)
    logo = models.FileField(null=True, blank=True)
    pbi_report_id=models.CharField(max_length=225,null=True,blank=True)

    class Meta: 
        db_table = 'dashboard_company'
    

class CustomUserManager(BaseUserManager):
    def create_user(self,first_name,last_name,email,phone_number,image,username,password):
        user = self.model(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
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
    image = models.FileField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=10,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    solveticket_title=models.CharField(max_length=225 , null = True,blank=True,choices=[('Sale','Sale'),("Product","Product"),("Customer","Customer")])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    phone_verify=models.CharField(max_length=225, null=True,blank=True)
    company_id=models.IntegerField(null=True,blank=True)
    logoappearance=models.BooleanField(default=True)

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number','username']

    def __str__(self):
        return self.email  

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True
    
    @property
    def is_staff(self):
        return self.is_admin

# database already exist table
class Client(models.Model):
    client_id = models.IntegerField(primary_key=True, db_column='DCLT_CLIENT_ID_DCLT')  
    client_code = models.CharField(max_length=255, null=True, blank=True, db_column='DCLT_CLIENT_CODE_DCLT')  
    last_name = models.CharField(max_length=255, null=True, blank=True, db_column='DCLT_LASTNAME_LBL_DCLT')  
    first_name = models.CharField(max_length=255, null=True, blank=True, db_column='DCLT_FIRSTNAME_LBL_DCLT')  
    dob = models.DateTimeField(null=True, blank=True, db_column='DCLT_BIRTHDAY_DATE_DCLT')  
    phone_number = models.CharField(max_length=20, null=True, blank=True, db_column='DCLT_PHONE_NB_DCLT')  
    email = models.EmailField(max_length=255, null=True, blank=True, db_column='DCLT_EMAIL_LBL_DCLT')  
    city = models.CharField(max_length=225, null=True, blank=True, db_column='DCLT_CITY_LBL_DCLT')  
    country = models.CharField(max_length=225, null=True, blank=True, db_column='DCLT_COUNTRY_LBL_DCLT')  
    zone = models.CharField(max_length=225, null=True, blank=True, db_column='DCLT_ZONE_LBL_DCLT')  
    acc_crea_date = models.BooleanField(default=False, db_column='DCLT_ACC_CREA_DATE_DCLT')  
    cbe_flag = models.BooleanField(default=False, db_column='DCLT_IS_CBE_FLAG_DCLT')  
    cbp_flag = models.BooleanField(default=False, db_column='DCLT_IS_CBP_FLAG_DCLT')  
    cbm_flag = models.BooleanField(default=False, db_column='DCLT_IS_CBM_FLAG_DCLT')  
    date_ins = models.DateTimeField(null=True, blank=True, db_column='DCLT_DATE_INSCRIPTION_DATE_DCLT')  
    sex = models.CharField(max_length=225, null=True, blank=True, db_column='DCLT_SEXE_LBL_DCLT')  

    class Meta:
        managed = False  
        db_table = 'DIM_CLIENT_DCLT'

# class Employees(models.Model):
#     emp_id=models.IntegerField(primary_key=True,db_column='DEMP_EMPLOYEES_ID_DEMP')
#     staff_code=models.CharField(max_length=225,null=True,db='DEMP_STAFF_CODE_DEMP')
#     last_name=models.CharField(max_length=225,null=True)#DEMP_LAST_NAME_DEMP)
#     first_name=models.CharField(max_length=225,null=True)#DEMP_FIRST_NAME_DEMP)
#     sex=models.CharField(max_length=225,null=True)#DEMP_SEXE_LBL_DEMP)
#     dob=models.DateTimeField(null=True)#DEMP_BIRTHDAY_DATE_DEMP)
#     phone_number=models.IntegerField(null=True)#DEMP_PHONENUMBER_DEC_DEMP)
#     email=models.EmailField(max_length=225,null=True)#DEMP_EMAIL_DEMP)
#     city=models.CharField(max_length=225,null=True)#DEMP_CITY_LBL_DEMP)
#     country=models.CharField(max_length=225,null=True)#DEMP_COUNTRY_LBL_DEMP)
#     contract_type=models.CharField(max_length=225,null=True)#DEMP_CONTRACT_TYPE_LBL_DEMP)
#     gross_salary=models.DecimalField(max_digits=25, decimal_places=8,null=True)#DEMP_GROSS_SALARY_DEC_DEMP)
#     net_salary=models.DecimalField(max_digits=25, decimal_places=8,null=True)#DEMP_NET_SALARY_DEC_DEMP)
#     contract_startdate=models.DateTimeField(null=True)#DEMP_CONTRACT_START_DATE_DEMP)
#     contract_enddate=models.DateTimeField(null=True)#DEMP_CONTRACT_END_DATE_DEMP)
#     fee_transport=models.DecimalField(max_digits=25, decimal_places=8,null=True)#DEMP_FEE_TRANSPORT_DEC_DEMP)
#     fee_healthcare=models.DecimalField(max_digits=25, decimal_places=8,null=True)#DEMP_FEE_HEALTHCARE_DEC_DEMP)
#     fee_meal=models.DecimalField(max_digits=25, decimal_places=8,null=True)#DEMP_FEE_MEAL_DEC_DEMP)
#     monthly_glb_cost=models.DecimalField(max_digits=25, decimal_places=8,null=True)#DEMP_MONTH_GLB_COST_DEC_DEMP)
#     job_title=models.CharField(max_length=225,null=True)#DEMP_JOB_TITLE_LBL_DEMP
#     job_type=models.CharField(max_length=225,null=True)#DEMP_JOB_TYPE_LBL_DEMP
#     month_total=models.DecimalField(max_digits=25, decimal_places=8,null=True)#DEMP_MONTH_TOTAL_HOUR_DEC_DEMP

#     class Meta:
#         managed = False  # Tell Django not to manage this table
#         db_table = 'DIM_EMPLOYEES_DEMP'

class Ticket(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='requested_tickets')
    ticket_type=models.CharField(max_length=225,null=True,blank=True,choices=[("Issue","Issue"),("Request","Request")])#issue or request for evolution
    ticket_title=models.CharField(max_length=225 , null = True,blank=True,choices=[('Sale','Sale'),("Product","Product"),("Customer","Customer")])# sale, product,customer
    ticket_description=models.CharField(max_length=225 , null = True,blank=True)
    ticket_number=models.CharField(max_length=225, null=True,blank=True)
    priority_level=models.CharField(max_length=225,null=True,blank=True,choices=[("Low","Low"),("Medium","Medium"),("High","High")])#e.g., Low, Medium, High
    ticket_file=models.FileField(upload_to='ticket_file/',blank=True,null=True)#with optional attachments/screenshots
    submission_status=models.CharField(max_length=50,default='Received',choices=[("Received","Received"),("In Progress","In Progress"),("Resolved","Resolved")])# e.g., Received, In Progress, Resolved
    assigned_request=models.ForeignKey(User,on_delete=models.CASCADE,related_name='assigned_tickets',null=True,blank=True)#e.g., technical, feature development
    is_assign=models.BooleanField(default=False)
    is_feedback=models.BooleanField(default=False)
    solved_date=models.DateTimeField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

class TicketFeedback(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    ticket_id=models.ForeignKey(Ticket,on_delete=models.CASCADE)
    satisfaction_score=models.PositiveIntegerField(null=True,blank=True) 
    feedback_desciption=models.CharField(max_length=225,null=True,blank=True)

class Notification(models.Model):
    sender=models.ForeignKey(User,on_delete=models.CASCADE,related_name='notification_sender',null=True,blank=True)
    receiver=models.ForeignKey(User,on_delete=models.CASCADE,related_name='notification_receiver',null=True,blank=True)
    is_delete=models.BooleanField(default=False)
    notification_title=models.CharField(max_length=225,null=True,blank=True)
    notification_description=models.CharField(max_length=1000,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    reader=models.BooleanField(default=False)

class ChatTicketDetails(models.Model):
    ticket_number=models.ForeignKey(Ticket,on_delete=models.CASCADE,null=True,blank=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    chat=models.CharField(max_length=1000,null=True,blank=True)
    is_reader=models.BooleanField(default=False)
    is_delete=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_at=models.DateTimeField(auto_now=True,null=True,blank=True)
   
