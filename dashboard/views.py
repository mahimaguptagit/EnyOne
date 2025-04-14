from django.shortcuts import render,redirect
from django.views import View
from django.contrib.auth import authenticate ,login as dj_login,logout as dj_logout
from .models import *
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .utils import *
from django.utils import timezone
from django.contrib import messages
from .admin import *
from django.http import HttpResponse
from django.db import IntegrityError
import io
import os
from django.db.models import Q


# Create your views here.

class AdminLoginView(View):
    def get(self,request):
        return render(request,'dashboard/Admin/admin-login.html')
    def post(self,request):
        email=request.POST.get('username')
        password=request.POST.get('password')
        user= authenticate(request=request, email=email, password=password)
        if user:
            user=User.objects.get(email=email)
            dj_login(request,user)
            if user.is_superuser == True:
                messages.success(request, 'Log In Successfully..!!')
                return redirect ('AdminDashboard')
            else:
                messages.success(request, 'Log In Successfully..!!')
                return redirect('StaffDashboard')
        return redirect('AdminLogin')
    
def admin_logout(request):
    dj_logout(request)
    return redirect('AdminLogin')

@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')   
class AdminUpdateProfileView(View):
    def get(self,request,id):
        userdata=User.objects.get(id=id)
        notificationcount=Notification.objects.filter(receiver=request.user,reader=False).count()
        return render(request,'dashboard/Admin/admin-profile.html',{'user':userdata,'unreadnotificationcount':notificationcount})
    def post(self,request,id):
        try:
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
            if userdata.is_superuser == True:
                    return redirect ('AdminDashboard')
            else:
                    return redirect('StaffDashboard')
        except IntegrityError as e:
                if 'phone_number' in str(e):
                    messages.error(request, "This phone number is already in use. Please use a different phone number.")
                elif 'email' in str(e):
                    messages.error(request, "This email is already in use. Please use a different email.")
                else:
                    messages.error(request, "An error occurred during the registration process. Please try again.")
                return redirect ('AdminUpdateProfile',id=id)
                

@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')
class AdminChangePasswordView(View):
    def get(self,request):
        notificationcount=Notification.objects.filter(receiver=request.user,reader=False).count()
        return render(request,'dashboard/Admin/admin-change-password.html',{'unreadnotificationcount':notificationcount})
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
                    if user.is_superuser == True:
                            return redirect ('AdminDashboard')
                    else:
                            return redirect('StaffDashboard')
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
        ticketfeedbackcount=TicketFeedback.objects.all().count()
        customerdata=User.objects.filter(is_admin=False, company_id__isnull=False, company_id__gt=0,is_superuser=False,is_active=True).count()
        notificationcount=Notification.objects.filter(receiver=request.user,reader=False).count()
        # clientdata=Client.objects.all()
        # customerdata=Client.objects.all().count()
        # print(clientdata)
        return render(request,'dashboard/Admin/index.html',{'active1':'active','ticketdatacount':ticketdata,'customerdatacount':customerdata,'ticketfeedbackcount':ticketfeedbackcount,'unreadnotificationcount':notificationcount})
    
@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')
class StaffDashboardView(View):
    def get(self,request):
        ticketdata=Ticket.objects.filter(assigned_request=request.user).count()
        ticketfeedbackcount=TicketFeedback.objects.filter(ticket_id__assigned_request = request.user).count()
        customerdata=User.objects.filter(is_admin=False, company_id__isnull=False, company_id__gt=0,is_superuser=False,is_active=True).count()
        notificationcount=Notification.objects.filter(receiver=request.user,reader=False).count()
        return render(request,'dashboard/Staff/staff_index.html',{'active03':'active','ticketdatacount':ticketdata,'customerdatacount':customerdata,'ticketfeedbackcount':ticketfeedbackcount,'unreadnotificationcount':notificationcount})
    
@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')
class ManageUserView(View):
    def get(self,request):
        userdata=User.objects.filter(is_admin=False, company_id__isnull=False, company_id__gt=0,is_superuser=False,is_active=True).order_by('-id')
        notificationcount=Notification.objects.filter(receiver=request.user,reader=False).count()
        return render(request,'dashboard/User/show_userlist.html',{'userdatas':userdata,'unreadnotificationcount':notificationcount})
        # return render(request,'dashboard/User/show_userlist.html',{'userdatas':userdata,'active2':'active'})
    
@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')
class ShowUserDetailsView(View):
    def get(self,request,id):
        userdata=User.objects.get(id=id)
        notificationcount=Notification.objects.filter(receiver=request.user,reader=False).count()
        return render(request,'dashboard/User/show_userdetails.html',{'user':userdata,'unreadnotificationcount':notificationcount})
        # return render(request,'dashboard/User/show_userdetails.html',{'user':userdata,'active2':'active'})
    
@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')    
class AddUserView(View):
    def get(self,request):
        company_data=Company.objects.all()
        notificationcount=Notification.objects.filter(receiver=request.user,reader=False).count()
        return render(request,'dashboard/User/add_userdata.html',{'company_data':company_data,'unreadnotificationcount':notificationcount})
    def post(self,request):
        try:
            username=request.POST.get('username')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            image = request.FILES.get('image')
            phone_number = request.POST.get('phone_number')
            password = request.POST.get('password')
            company=request.POST.get('company')
            userdata=User.objects.create_user(username=username,first_name=first_name,last_name=last_name,email=email,image=image,phone_number=phone_number,password=password)
            userdata.image=image
            userdata.company_id=company
            userdata.save()
            messages.success(request,'User Created Successfully !!')
            return redirect('ManageUserLists')
        except IntegrityError as e:
                if 'phone_number' in str(e):
                    messages.error(request, "This phone number is already in use. Please use a different phone number.")
                elif 'email' in str(e):
                    messages.error(request, "This email is already in use. Please use a different email.")
                else:
                    messages.error(request, "An error occurred during the registration process. Please try again.")
                
                return redirect ('ManageUserLists')
    
@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')
class ManageStaffView(View):
    def get(self,request):
        userdata=User.objects.filter(is_superuser=False,is_admin=True).order_by('-id')
        notificationcount=Notification.objects.filter(receiver=request.user,reader=False).count()
        return render(request,'dashboard/Staff/staff_lists.html',{'userdatas':userdata,'active2':'active','unreadnotificationcount':notificationcount})
    
@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')
class ShowStaffDetailsView(View):
    def get(self,request,id):
        userdata=User.objects.get(id=id)
        notificationcount=Notification.objects.filter(receiver=request.user,reader=False).count()
        return render(request,'dashboard/Staff/show_staffdetails.html',{'user':userdata,'active2':'active','unreadnotificationcount':notificationcount})
    
@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')    
class AddStaffView(View):
    def get(self,request):
        notificationcount=Notification.objects.filter(receiver=request.user,reader=False).count()
        return render(request,'dashboard/Staff/add_staff.html',{'unreadnotificationcount':notificationcount})
    def post(self,request):
        try:
            username=request.POST.get('username')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            image = request.FILES.get('image')
            phone_number = request.POST.get('phone_number')
            password = request.POST.get('password')
            solveticket_title=request.POST.get('solveticket_title')
            userdata=User.objects.create_user(username=username,first_name=first_name,last_name=last_name,email=email,image=image,phone_number=phone_number,password=password)
            userdata.solveticket_title=solveticket_title
            userdata.image=image
            userdata.is_admin=True
            userdata.save()
            messages.success(request,'Staff Created Successfully !!')
            return redirect('ManageStaff')
        except IntegrityError as e:
                if 'phone_number' in str(e):
                    messages.error(request, "This phone number is already in use. Please use a different phone number.")
                elif 'email' in str(e):
                    messages.error(request, "This email is already in use. Please use a different email.")
                else:
                    messages.error(request, "An error occurred during the registration process. Please try again.")
                    return redirect('ManageStaff')
    
@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')
class UpdateStaffDetailsView(View):
    def get(self,request,id):
        userdata=User.objects.get(id=id)
        notificationcount=Notification.objects.filter(receiver=request.user,reader=False).count()
        return render(request,'dashboard/Staff/edit_staff.html',{'user':userdata,'active2':'active','unreadnotificationcount':notificationcount})
    def post(self,request,id):
        try :
            username=request.POST.get('username')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            image = request.FILES.get('image')
            phone_number = request.POST.get('phone_number')
            solveticket_title=request.POST.get('solveticket_title')
            userdata=User.objects.get(id=id)
            userdata.username=username
            userdata.first_name=first_name
            userdata.last_name=last_name
            userdata.email=email
            userdata.phone_number=phone_number
            userdata.solveticket_title=solveticket_title
            if image:
                userdata.image=image
            userdata.save()
            messages.success(request,'Staff Updated Successfully !!')
            return redirect('ManageStaff')
        except IntegrityError as e:
                if 'phone_number' in str(e):
                    messages.error(request, "This phone number is already in use. Please use a different phone number.")
                elif 'email' in str(e):
                    messages.error(request, "This email is already in use. Please use a different email.")
                else:
                    messages.error(request, "An error occurred during the registration process. Please try again.")
                    return redirect('ManageStaff')

class DeleteStaffDetailsView(View):
    def get(self,request,id):
        User.objects.get(id=id).delete()
        return redirect('ManageStaff')

@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')
class RaiseTicketListView(View):
    def get(self,request):
        if request.user.is_superuser:
            ticketdata=Ticket.objects.all().order_by('-id')
        else:
            ticketdata=Ticket.objects.filter(assigned_request=request.user).order_by('-id')
        notificationcount=Notification.objects.filter(receiver=request.user,reader=False).count()
        return render(request,'dashboard/raise_ticket/show_ticketlist.html',{'ticketdetails':ticketdata,'active3':'active','active310':'active','bright1':'headbuttonactive','unreadnotificationcount':notificationcount}) 
    
@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')
class RaiseIssueListView(View):
    def get(self,request):
        if request.user.is_superuser:
            ticketdata=Ticket.objects.filter(ticket_type='Issue').order_by('-id')
        else:
            ticketdata=Ticket.objects.filter(assigned_request=request.user,ticket_type='Issue').order_by('-id')
        notificationcount=Notification.objects.filter(receiver=request.user,reader=False).count()
        return render(request,'dashboard/raise_ticket/show_all_issue.html',{'ticketdetails':ticketdata,'active3':'active','active310':'active','bright2':'headbuttonactive','unreadnotificationcount':notificationcount}) 
    
@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')
class RaiseRequestListView(View):
    def get(self,request):
        if request.user.is_superuser:
            ticketdata=Ticket.objects.filter(ticket_type='Request').order_by('-id')
        else:
            ticketdata=Ticket.objects.filter(assigned_request=request.user,ticket_type='Request').order_by('-id')
        notificationcount=Notification.objects.filter(receiver=request.user,reader=False).count()
        return render(request,'dashboard/raise_ticket/show_all_request.html',{'ticketdetails':ticketdata,'active3':'active','active310':'active','bright3':'headbuttonactive','unreadnotificationcount':notificationcount}) 
    
@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')
class TicketDetailPageView(View):
    def get(self,request,id):
        ticket_data=Ticket.objects.get(id=id)
        is_pdf = is_doc = is_image = False
        if ticket_data.ticket_file:
            ext = os.path.splitext(ticket_data.ticket_file.name.lower())[1] 
            if ext == ".pdf":
                is_pdf = True
            elif ext in [".doc", ".docx"]:
                is_doc = True
            elif ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
                is_image = True
        notificationcount=Notification.objects.filter(receiver=request.user,reader=False).count()
        return render(request,'dashboard/raise_ticket/ticket_details.html',{'data':ticket_data,'active3':'active','active310':'active','is_pdf': is_pdf,'is_doc': is_doc,'is_image': is_image,'unreadnotificationcount':notificationcount})

@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch') 
class TicketUpdateDetailsView(View):
    def get(self,request,id):
        ticket_data=Ticket.objects.get(id=id)
        admindatas=User.objects.filter(solveticket_title=ticket_data.ticket_title,is_admin=True,is_superuser=False)
        is_pdf = is_doc = is_image = False
        if ticket_data.ticket_file:
            ext = os.path.splitext(ticket_data.ticket_file.name.lower())[1] 
            if ext == ".pdf":
                is_pdf = True
            elif ext in [".doc", ".docx"]:
                is_doc = True
            elif ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
                is_image = True
        notificationcount=Notification.objects.filter(receiver=request.user,reader=False).count()
        return render(request,'dashboard/raise_ticket/ticketupdate_details.html',{'data':ticket_data,'active3':'active','active310':'active','admindata':admindatas,'is_pdf': is_pdf,'is_doc': is_doc,'is_image': is_image,'unreadnotificationcount':notificationcount})
    def post(self,request,id):
        assigned_data=request.POST.get('assigned_data')
        submission_status=request.POST.get('submission_status')
        ticket_data=Ticket.objects.get(id=id)
        current_datetime=timezone.now()
        if assigned_data:
            userdata = User.objects.filter(id=assigned_data, is_admin=True).first()
            if not userdata:
                messages.error(request, 'Invalid Staff selected!')
                return redirect('TicketUpdateDetails', id=id)
            if ticket_data.is_assign:
                messages.error(request, 'This ticket is already assigned!')
                return redirect('TicketUpdateDetails', id=id)
            ticket_data.assigned_request = userdata
            ticket_data.is_assign = True
            ticket_data.submission_status = 'In Progress'
            ticket_data.save()
            messages.success(request, 'Ticket Assigned Successfully!')
            return redirect('RaiseTicketList')
        if submission_status == 'Resolved':
            if not ticket_data.is_assign:
                messages.error(request, 'First assign the ticket!')
                return redirect('TicketUpdateDetails', id=id)
            if ticket_data.submission_status == 'Resolved':
                messages.error(request, 'Ticket is already resolved!')
                return redirect('TicketUpdateDetails', id=id)
            ticket_data.solved_date = current_datetime
            ticket_data.submission_status = 'Resolved'
            ticket_data.save()
            send_resolved_ticket(ticket_data.user.email, ticket_data.ticket_number, ticket_data.user)
            messages.success(request, 'Ticket marked as resolved!')
            return redirect('RaiseTicketList')
        elif submission_status == 'In Progress':
            if not ticket_data.is_assign:
                messages.error(request, 'First assign the ticket!')
                return redirect('TicketUpdateDetails', id=id)
        messages.error(request, 'Invalid action!')
        return redirect('TicketUpdateDetails', id=id)
        # if assigned_data:
        #         userdata=User.objects.filter(id=assigned_data,is_admin=True).first()
        #         ticket_data.assigned_request=userdata
        #         ticket_data.is_assign=True
        #         ticket_data.submission_status='In Progress'
        #         ticket_data.save()
        #         messages.success(request,'Ticket Data Updated')
        #         return redirect('RaiseTicketList')

            # if submission_status == 'Resolved':
            #     messages.success(request,'First Assign Ticket')
            #     return redirect('TicketUpdateDetails', id=id)
            # elif submission_status == 'In Progress':
            #     ticket_data.assigned_request=userdata
            #     ticket_data.is_assign=True
            #     ticket_data.submission_status=submission_status
            #     ticket_data.save()
            #     messages.success(request,'Ticket Data Updated')
            #     return redirect('RaiseTicketList')
            # else:
            #     messages.error(request,'Ticket already received !!')
            #     return redirect('TicketUpdateDetails', id=id)
        # else:
        #     if submission_status == 'Resolved':
        #         if ticket_data.is_assign == True:
        #             if ticket_data.submission_status == 'Resolved':
        #                 messages.error(request,'Already Resolved')
        #                 return redirect('TicketUpdateDetails', id=id)
        #             ticket_data.solved_date=currentdatetime
        #             ticket_data.submission_status=submission_status
        #             ticket_data.save()
        #             send_resolved_ticket(ticket_data.user.email,ticket_data.ticket_number,ticket_data.user)
        #             messages.success(request,'Ticket Data Updated')
        #             return redirect('RaiseTicketList')
        #         else:
        #             messages.success(request,'First Assign Ticket')
        #             return redirect('TicketUpdateDetails', id=id)
        #     elif submission_status == 'In Progress' : 
        #             messages.error(request,'Already Assign')
        #             return redirect('TicketUpdateDetails', id=id)
        #     else:
        #         messages.error(request,'Ticket already received !!')
        #         return redirect('TicketUpdateDetails', id=id)

@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')   
class TicketParticularDeleteView(View):
    def get(self,request,id):
        ticket_data=Ticket.objects.get(id=id)
        if ticket_data: 
            TicketFeedback.objects.filter(ticket_id=id).delete()
            ticket_data.delete()
        return redirect('RaiseTicketList')
    
@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')
class TicketFeedbackView(View):
    def get(self,request):
        if request.user.is_superuser:
            ticketfeedbackdatas=TicketFeedback.objects.all().order_by('-id')
        else:
            ticketfeedbackdatas=TicketFeedback.objects.filter(ticket_id__assigned_request=request.user)
        notificationcount=Notification.objects.filter(receiver=request.user,reader=False).count()
        return render(request,'dashboard/raise_ticket/ticket_feedbacklists.html',{'tikcetfeedbackdata':ticketfeedbackdatas,'active311':'active','active3':'active','unreadnotificationcount':notificationcount})

@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')    
class TicketFeedbackDetailPageView(View):
    def get(self,request,id):
        ticketfeedbackdata=TicketFeedback.objects.filter(id=id).first()
        ticket_data=Ticket.objects.get(id=ticketfeedbackdata.ticket_id.id)
        is_pdf = is_doc = is_image = False
        if ticket_data.ticket_file:
            ext = os.path.splitext(ticket_data.ticket_file.name.lower())[1] 
            if ext == ".pdf":
                is_pdf = True
            elif ext in [".doc", ".docx"]:
                is_doc = True
            elif ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
                is_image = True
        notificationcount=Notification.objects.filter(receiver=request.user,reader=False).count()
        return render(request,'dashboard/raise_ticket/showticketfeedbackdetails.html',{'data':ticket_data,'active3':'active','active311':'active','is_pdf': is_pdf,'is_doc': is_doc,'is_image': is_image,'unreadnotificationcount':notificationcount})

@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')   
class TicketFeedbackDeleteView(View):
    def get(self,request,id):
        ticketdata=TicketFeedback.objects.get(id=id).delete()
        return redirect('TicketFeedback')

@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')   
class NotificationListsView(View):
    def get(self,request):
        notificationcount=Notification.objects.filter(receiver=request.user,reader=False).count()
        notificationdata=Notification.objects.filter(sender=request.user).order_by('-id')
        return render(request,'dashboard/Notification/notification_list.html',{'active4':'active','notifidetails':notificationdata,'unreadnotificationcount':notificationcount})

@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')   
class NotificationreceiveView(View):
    def get(self,request):
        notificationcount=0
        notifidata=Notification.objects.filter(receiver=request.user).order_by('-id')
        for notif in notifidata:
                notif.reader=True
                notif.save()
        return render(request,'dashboard/Notification/notification_receive.html',{'notifidatas':notifidata,'unreadnotificationcount':notificationcount})

@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')   
class AddNotificationView(View):
    def get(self,request):
        userdatas = User.objects.filter(Q(is_admin=True) | Q(is_admin=False, company_id__isnull=False, company_id__gt=0),is_superuser=False,is_active=True)
        staffdata=User.objects.filter(is_admin=True,is_superuser=False,is_active=True)
        clientdata = User.objects.filter(is_admin=False,is_active=True).exclude(company_id__isnull=True).exclude(company_id=0)
        notificationcount=Notification.objects.filter(receiver=request.user,reader=False).count()
        return render(request,'dashboard/Notification/add_notification.html',{'user_datas':userdatas,'staffdatas':staffdata,'clientdatas':clientdata,'unreadnotificationcount':notificationcount})
    def post(self,request):
        notification_title=request.POST.get('title')
        notification_description=request.POST.get('description')
        selected_users = request.POST.getlist('selected_users')
        recipients = User.objects.filter(pk__in=selected_users,is_active=True)
        for recipient in recipients:
            Notification.objects.create(notification_title=notification_title,notification_description=notification_description,sender=request.user,receiver=recipient)
            registration_token = recipient.phone_verify  
            print(f"User FCM Token: {registration_token}")
            if registration_token:  
                send_push_notification(registration_token, notification_title, notification_description)
            else:
                print("Error: No FCM token found for the user.")
        return redirect('NotificationLists')

@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')   
class DeleteAdminParticularNotificationView(View):
    def get(self,request,id):
        Notification.objects.get(id=id).delete()
        return redirect('NotificationLists')
    
# class ChatTicketDetails(models.Model):
    # ticket_number=models.ForeignKey(Ticket,on_delete=models.CASCADE,null=True,blank=True)
    # user=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    # chat=models.CharField(max_length=1000,null=True,blank=True)
    # created_at=models.DateTimeField(auto_now_add=True)
    # updated_at=models.DateTimeField(auto_now=True)

@method_decorator(login_required(login_url='/dashboard/admin-login/'), name='dispatch')
class ChatSendReceiveView(View):
    def get(self,request,id):
        notificationcount=Notification.objects.filter(receiver=request.user,reader=False).count()
        chatdatas=ChatTicketDetails.objects.filter(ticket_number=id)
        return render(request,'dashboard/Chat/chatsend.html',{'chatdetails':chatdatas,'unreadnotificationcount':notificationcount})
    def post(self,request,id):
        message=request.POST.get('message')
        ticket_data=Ticket.objects.filter(id=id).first()
        chatdatas=ChatTicketDetails.objects.create(ticket_number=ticket_data,user=request.user,chat=message)
        title='New Message'
        description=f'New message for ticket number {ticket_data.ticket_number}'
        Notification.objects.create(sender=request.user,receiver=ticket_data.user,notification_title=title,notification_description=description)
        registration_token = ticket_data.user.phone_verify  
        print(f"User FCM Token: {registration_token}")
        if registration_token:  
                send_push_notification(registration_token, title, description)
        else:
                print("Error: No FCM token found for the user.")
        return redirect('ChatSendReceive' , id=id)
    
class ExportAllTicketView(View):
    def get(self,request):
        if request.user.is_superuser:
            total_ticketdata=Ticket.objects.all().order_by('-id')
        else:
            total_ticketdata=Ticket.objects.filter(assigned_request=request.user).order_by('-id')
        ticket_resource = TicketDataResources()
        dataset = ticket_resource.export(total_ticketdata)
        response = HttpResponse(dataset.xlsx, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="totalticket.xls"'
        return response
        pass

class ExportAllRequestView(View):
    def get(self,request):
        if request.user.is_superuser:
            ticketdata=Ticket.objects.filter(ticket_type='Request').order_by('-id')
        else:
            ticketdata=Ticket.objects.filter(assigned_request=request.user,ticket_type='Request').order_by('-id')
        ticket_resource = TicketDataResources()
        dataset = ticket_resource.export(ticketdata)
        response = HttpResponse(dataset.xlsx, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="totalrequests.xls"'
        return response


class ExportAllIssueView(View):
    def get(self,request):
        if request.user.is_superuser:
            ticketdata=Ticket.objects.filter(ticket_type='Issue').order_by('-id')
        else:
            ticketdata=Ticket.objects.filter(assigned_request=request.user,ticket_type='Request').order_by('-id')
        ticket_resource = TicketDataResources()
        dataset = ticket_resource.export(ticketdata)
        response = HttpResponse(dataset.xlsx, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="totalissue.xls"'
        return response
        
