from django.shortcuts import render,redirect
from django.views import View
from django.contrib.auth import authenticate,login as dj_login,logout as dj_logout
from .models import *
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .utils import *
from django.utils import timezone
from django.contrib import messages

# Create your views here.

class AdminLoginView(View):
    def get(self,request):
        return render(request,'dashboard/Admin/admin-login.html')
    def post(self,request):
        username=request.POST.get('username')
        password=request.POST.get('password')
        user= authenticate(request=request,username=username,password=password)
        if user:
            user=User.objects.get(username=username)
            print(user.username)
            dj_login(request,user)
            return redirect ('AdminDashboard')
        return redirect('AdminLogin')
    
def admin_logout(request):
    dj_logout(request)
    messages.success(request, 'Admin Logged Out Successfully..!!')
    return redirect('AdminLogin')

@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')   
class AdminUpdateProfileView(View):
    def get(self,request,id):
        userdata=User.objects.get(id=id)
        return render(request,'dashboard/Admin/admin-profile.html',{'user':userdata})
    def post(self,request,id):
        username=request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        image = request.FILES.get('image')
        phone_number = request.POST.get('phone_number')
        userdata=User.objects.get(id=id)
        userdata.username=username
        userdata.first_name=first_name
        userdata.last_name=last_name
        userdata.email=email
        userdata.phone_number=phone_number
        if image:
            userdata.image=image
        userdata.save()
        return redirect('AdminDashboard')

@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')
class AdminChangePasswordView(View):
    def get(self,request):
        return render(request,'dashboard/Admin/admin-change-password.html')
    def post(self,request):
        old_password=request.POST.get('old_password')
        password=request.POST.get('password')
        confirm_password=request.POST.get('confirm_password')
        print(confirm_password)
        id=request.user.id
        user=User.objects.get(id=id)
        print(user)
        if password == confirm_password:
            if user.check_password(old_password):        
                    user.set_password(password)
                    user.save()    
                    user= authenticate(request,phone_number=user.phone_number, password=password)  
                    if user:
                        dj_login(request,user)
                    messages.success(request,'Password Change Successfully!!!')
                    return redirect('AdminDashboard')
            else:
                messages.error(request,'Check Old Password ')
                return redirect('AdminChangePass')
        else:
                messages.error(request,'New Password and Confirm Password must be same ')
                return redirect('AdminChangePass') 
        
class EmailVerificationView(View):
    def get(self, request):
        return render(request,'dashboard/Admin/emailverification.html')
    def post(self, request):
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email,is_admin=True)
        except User.DoesNotExist:
            messages.error(request, 'Admin with this email does not exist!!')
            return redirect('AdminForgetPassword')
        send_otp(user.email)
        request.session['reset_email'] = email
        messages.success(request, 'OTP sent successfully! Check your email to reset the password.')
        return redirect('VerifyOtp')
    
class VerifyOtpView(View):
    def get(self,request):
        return render(request,'dashboard/Admin/otpverification.html')
    def post(self, request):
        email = request.session.get('reset_email')
        otp = request.POST.get('otp')
        try:
            user = User.objects.get(email=email,is_admin=True)
        except User.DoesNotExist:
            messages.error(request, 'Admin with this email does not exist!!')
            return redirect('VerifyOtp')
        if user.otp==otp:
            messages.success(request, 'Change Password as OTP is correct')
            return redirect('AdminForgetPassword')
        else :
            messages.error(request, 'OTP Not Matched!!')
            return redirect('VerifyOtp')

class AdminForgetPasswordView(View):
    def get(self, request):
        return render(request,'dashboard/Admin/admin_forgetpassword.html')
    def post(self, request):
        email = request.session.get('reset_email')
        newpassword = request.POST.get('newpassword')
        confirmpassword = request.POST.get('confirmpassword')
        try:
            user = User.objects.get(email=email,is_admin=True)
        except User.DoesNotExist:
            messages.error(request, 'Admin with this phone number does not exist!!')
            return redirect('AdminForgetPassword')
        if newpassword != confirmpassword:
            messages.error(request, 'New Password and Confirm Password must be the same.')
            return redirect('AdminForgetPassword')
        user.set_password(newpassword)
        user.save()
        messages.success(request, 'Password changed successfully!')
        return redirect('AdminLogin') 

@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')
class AdminDashboardView(View):
    def get(self,request):
        ticketdata=Ticket.objects.all().count()
        # customerdata=User.objects.filter(is_admin=False,is_superuser=False).count()
        customerdata=User.objects.filter(is_superuser=False).count()
        return render(request,'dashboard/Admin/index.html',{'active1':'active','ticketdatacount':ticketdata,'customerdatacount':customerdata})
    
@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')
class ManageUserView(View):
    def get(self,request):
        userdata=User.objects.filter(is_superuser=False).order_by('-id')
        return render(request,'dashboard/User/show_userlist.html',{'userdatas':userdata,'active2':'active'})
    
@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')
class ShowUserDetailsView(View):
    def get(self,request,id):
        userdata=User.objects.get(id=id)
        return render(request,'dashboard/User/show_userdetails.html',{'user':userdata,'active2':'active'})
    
@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')    
class AddUserView(View):
    def get(self,request):
        return render(request,'dashboard/User/add_userdata.html')
    def post(self,request):
        username=request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        image = request.FILES.get('image')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        userdata=User.objects.create_user(username=username,first_name=first_name,last_name=last_name,email=email,image=image,phone_number=phone_number,password=password)
        userdata.image=image
        userdata.save()
        messages.success(request,'User Created Successfully !!')
        return redirect('ManageUserLists')

@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')
class RaiseTicketListView(View):
    def get(self,request):
        ticketdata=Ticket.objects.all().order_by('-id')
        return render(request,'dashboard/raise_ticket/show_ticketlist.html',{'ticketdetails':ticketdata,'active3':'active','active310':'active'}) 
    
@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')
class TicketDetailPageView(View):
    def get(self,request,id):
        ticket_data=Ticket.objects.get(id=id)
        return render(request,'dashboard/raise_ticket/ticket_details.html',{'data':ticket_data,'active3':'active','active310':'active'})

@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')   
class TicketUpdateDetailsView(View):
    def get(self,request,id):
        ticket_data=Ticket.objects.get(id=id)
        admindatas=User.objects.filter(is_admin=True)
        return render(request,'dashboard/raise_ticket/ticketupdate_details.html',{'data':ticket_data,'active3':'active','active310':'active','admindata':admindatas})
    def post(self,request,id):
        assigned_data=request.POST.get('assigned_data')
        submission_status=request.POST.get('submission_status')
        ticket_data=Ticket.objects.get(id=id)
        userdata=User.objects.filter(id=assigned_data,is_admin=True).first()
        currentdatetime=timezone.now()
        if assigned_data:
            if submission_status == 'Resolved':
                messages.success(request,'First Assign Ticket')
                return redirect('TicketUpdateDetails', id=id)
            elif submission_status == 'In Progress':
                ticket_data.assigned_request=userdata
                ticket_data.is_assign=True
                ticket_data.submission_status=submission_status
                ticket_data.save()
                messages.success(request,'Ticket Data Updated')
                return redirect('RaiseTicketList')
            else:
                messages.error(request,'Ticket already received !!')
                return redirect('TicketUpdateDetails', id=id)
        else:
            if submission_status == 'Resolved':
                if ticket_data.is_assign == True:
                    if ticket_data.submission_status == 'Resolved':
                        messages.error(request,'Already Resolved')
                        return redirect('TicketUpdateDetails', id=id)
                    ticket_data.solved_date=currentdatetime
                    ticket_data.submission_status=submission_status
                    ticket_data.save()
                    send_resolved_ticket(ticket_data.user.email,ticket_data.ticket_number,ticket_data.user)
                    messages.success(request,'Ticket Data Updated')
                    return redirect('RaiseTicketList')
                else:
                    messages.success(request,'First Assign Ticket')
                    return redirect('TicketUpdateDetails', id=id)
            elif submission_status == 'In Progress' : 
                    messages.error(request,'Already Assign')
                    return redirect('TicketUpdateDetails', id=id)
            else:
                messages.error(request,'Ticket already received !!')
                return redirect('TicketUpdateDetails', id=id)

@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')   
class TicketParticularDeleteView(View):
    def get(self,request,id):
        ticket_data=Ticket.objects.get(id=id).delete()
        return redirect('RaiseTicketList')
    
@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')
class TicketFeedbackView(View):
    def get(self,request):
        ticketfeedbackdatas=TicketFeedback.objects.all().order_by('-id')
        return render(request,'dashboard/raise_ticket/ticket_feedbacklists.html',{'tikcetfeedbackdata':ticketfeedbackdatas,'active311':'active','active3':'active'})

@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')    
class TicketFeedbackDetailPageView(View):
    def get(self,request,id):
        ticket_data=Ticket.objects.get(id=id)
        return render(request,'dashboard/raise_ticket/showticketfeedbackdetails.html',{'data':ticket_data,'active3':'active','active311':'active'})

@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')   
class TicketFeedbackDeleteView(View):
    def get(self,request,id):
        ticketdata=TicketFeedback.objects.get(id=id).delete()
        return redirect('TicketFeedback')

@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')   
class NotificationListsView(View):
    def get(self,request):
        notificationdata=Notification.objects.filter(sender=request.user).order_by('-id')
        return render(request,'dashboard/Notification/notification_list.html',{'active4':'active','notifidetails':notificationdata})

@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')   
class NotificationreceiveView(View):
    def get(self,request):
        notifidata=Notification.objects.filter(receiver=request.user).order_by('-id')
        return render(request,'dashboard/Notification/notification_receive.html',{'notifidatas':notifidata})

@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')   
class AddNotificationView(View):
    def get(self,request):
        userdatas=User.objects.filter(is_superuser=False,is_active=True)
        return render(request,'dashboard/Notification/add_notification.html',{'user_datas':userdatas})
    def post(self,request):
        notification_title=request.POST.get('title')
        notification_description=request.POST.get('description')
        selected_users = request.POST.getlist('selected_users')
        recipients = User.objects.filter(pk__in=selected_users,is_active=True)
        for recipient in recipients:
            Notification.objects.create(notification_title=notification_title,notification_description=notification_description,sender=request.user,receiver=recipient)
        return redirect('NotificationLists')

@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')   
class DeleteAdminParticularNotificationView(View):
    def get(self,request,id):
        Notification.objects.get(id=id).delete()
        return redirect('NotificationLists')


@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')   
class AnalyticDashboardView(View):
    def get(self,request):
        return render(request,'dashboard/analytical_dashboard.html')
