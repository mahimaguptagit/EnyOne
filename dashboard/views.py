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
    
class AdminDashboardView(View):
    def get(self,request):
        return render(request,'dashboard/index.html')
    
class AnalyticDashboardView(View):
    def get(self,request):
        return render(request,'dashboard/analytical_dashboard.html')
