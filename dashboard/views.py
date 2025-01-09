from django.shortcuts import render,redirect
from django.views import View
from django.contrib.auth import authenticate,login,logout
from .models import *

# Create your views here.

class AdminLoginView(View):
    def get(self,request):
        return render(request,'dashboard/admin-login.html')
    def post(self,request):
        username=request.POST.get('username')
        password=request.POST.get('password')
        user= authenticate(request=request,username=username,password=password)
        if user:
            user=User.objects.get(username=username)
            print(user.username)
            login(request,user)
            return redirect ('AdminDashboard')
        return redirect('AdminLogin')
    
class AdminUpdateProfileView(View):
    def get(self,request,id):
        userdata=User.objects.get(id=id)
        return render(request,'dashboard/admin-profile.html',{'userdetail':userdata})
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
        return redirect('AdminUpdateProfile',id=userdata.id)

class AdminDashboardView(View):
    def get(self,request):
        return render(request,'dashboard/index.html',{'active1':'active'})
    
class AnalyticDashboardView(View):
    def get(self,request):
        return render(request,'dashboard/analytical_dashboard.html')
    
class RaiseTicketListView(View):
    def get(self,request):
        ticketdata=Ticket.objects.all()
        return render(request,'dashboard/raise_ticket/show_ticketlist.html',{'ticketdetails':ticketdata,'active3':'active','active310':'active'})
