from django.shortcuts import render
from rest_framework.views import APIView ,View
from django.contrib.auth import authenticate,login,logout
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from .powerbi_service import PowerBIService

# Create your views here.

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return{str(refresh.access_token)}

class UserLoginView(APIView):
    def post(self,request):
        username=request.data.get('username')
        password=request.data.get('password')
        if not username or not password:
            return Response({'status':'False','message':'Both username and password are required.'})
        user = authenticate(request=request,username=username,password=password)
        if user:
            login(request,user)
            token=get_tokens_for_user(user)
            return Response({'status':'True','access':token,'message':'LogIn Successfully'})
        return Response({'status':'False','message':'Check UserName or Password !!'})
    
# class 


