from django.shortcuts import render
from rest_framework.views import APIView ,View
from django.contrib.auth import authenticate,login,logout
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from .powerbi_service import PowerBIService
from dashboard.models import *
from .serializers import *
from datetime import datetime

# Create your views here.

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

class UserLoginView(APIView):
    def post(self,request):
        username=request.data.get('username')
        password=request.data.get('password')
        if not username or not password:
            return Response({'status':'false','message':'Both username and password are required.'})
        user = authenticate(request=request,username=username,password=password)
        if user:
            userdata=User.objects.filter(is_superuser=False,id=user.id).first()
            if userdata:
                login(request,user)
                token=get_tokens_for_user(user)
                return Response({'status':'true','access_token':token,'message':'LogIn Successfully'})
            else:
                return Response({'status':'false','message':'Please Check User Details !!'})
        return Response({'status':'false','message':'Check UserName or Password !!'})
    
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request,format=None):
        userdata=User.objects.filter(id=request.user.id).first()
        if not userdata:
            return Response({'status':'false','message':'User data not found !!'})
        userdetail={
                "username":userdata.username,
                "first_name":userdata.first_name,
                "last_name":userdata.last_name,
                "email":userdata.email,
                "image":userdata.image.url,
                "phone_number":userdata.phone_number,}
        return Response({'status':'true','message':'User Profile Data','user_data':userdetail})
            
    
class UserRaiseTicketView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        user = request.user
        userdata=User.objects.filter(is_superuser=False,id=user.id).first()
        serializer = TicketSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            ticket_type = data.get('ticket_type')
            ticket_title = data.get('ticket_title')
            priority_level = data.get('priority_level')
            ticket_description = data.get('ticket_description')
            ticket_file = data.get('ticket_file')

            if not ticket_type and not ticket_title and not priority_level and not ticket_description:
                return Response({'status':'false','message':'Check Required Fields !!'})

            try:
                latest_ticket_id = Ticket.objects.latest('id').id + 1 if Ticket.objects.exists() else 1
                timestamp_part = datetime.now().strftime('%y%m%d%H%M%S%f')[:-3]
                ticket_number = f"ENYONE0{latest_ticket_id}0{timestamp_part}"
                ticket_data = Ticket.objects.create(
                    user=userdata,
                    ticket_type=ticket_type,
                    ticket_title=ticket_title,
                    ticket_description=ticket_description,
                    ticket_number=ticket_number,
                    priority_level=priority_level,
                    ticket_file=ticket_file
                )

                return Response({'status': 'true', 'message': 'Ticket raised successfully'})

            except Exception as e:
                return Response({'status': 'false', 'message': 'Something went wrong'})
        
        return Response({'status': 'false', 'message': 'Invalid data'})
    

class ShowRaisedTicketDataView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        ticket_type=request.data.get('ticket_type')
        if ticket_type:
            ticket_datas=Ticket.objects.filter(user=request.user,ticket_type=ticket_type).order_by('-id')
        else:
            ticket_datas=Ticket.objects.filter(user=request.user).order_by('-id')
        ticketdetails=[{
            "ticket_id":ticket_data.id,
            "ticket_type":ticket_data.ticket_type,
            "ticket_title":ticket_data.ticket_title,
            "ticket_description":ticket_data.ticket_description,
            "ticket_number":ticket_data.ticket_number,
            "priority_level":ticket_data.priority_level,
            "ticket_file":ticket_data.ticket_file.url if ticket_data.ticket_file else None,
            "submission_status":ticket_data.submission_status,
            "assigned_request":ticket_data.assigned_request.id if ticket_data.assigned_request else 0,
            "assigned_username":ticket_data.assigned_request.username if ticket_data.assigned_request else None,
            "assigned_user_image":ticket_data.assigned_request.image.url if  ticket_data.assigned_request.image  else None,
            "created_at":ticket_data.created_at,
            "solved_date":ticket_data.solved_date,
            "satisfaction_score":ticket_data.satisfaction_score,
            "ticket_type":ticket_data.ticket_type, 
        }
        for ticket_data in ticket_datas
        ]
        return Response({'status':'true','message':'Rised Ticket Data','ticket_details':ticketdetails})
    
class ShowParticularTicketDrtailsView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        ticket_id=request.data.get('ticket_id')
        if ticket_id:
            ticket_data=Ticket.objects.filter(id=ticket_id,user=request.user).first()
            if not ticket_data:
                return Response({'status': 'false', 'message': 'Ticket not found'})
            ticket_details={
            "ticket_id":ticket_data.id,
            "ticket_type":ticket_data.ticket_type,
            "ticket_title":ticket_data.ticket_title,
            "ticket_description":ticket_data.ticket_description,
            "ticket_number":ticket_data.ticket_number,
            "priority_level":ticket_data.priority_level,
            "ticket_file":ticket_data.ticket_file.url if ticket_data.ticket_file else None,
            "submission_status":ticket_data.submission_status,
            "assigned_request":ticket_data.assigned_request.id if ticket_data.assigned_request else 0,
            "assigned_username":ticket_data.assigned_request.username if ticket_data.assigned_request else None,
            "assigned_user_image":ticket_data.assigned_request.image.url if ticket_data.assigned_request.image  else None,
            "created_at":ticket_data.created_at,
            "solved_date":ticket_data.solved_date,
            "satisfaction_score":ticket_data.satisfaction_score,
            "ticket_type":ticket_data.ticket_type, 
            }
            return Response({'status':'true','message':'Ticket Details !!','ticketdetail':ticket_details})
        else:
            return Response({'status':'false','message':'Ticket ID Not Found '})
        
class AddSatisfactionScoreView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        ticket_id=request.data.get('ticket_id')
        satisfaction_score=request.data.get('satisfaction_score')
        score=int(satisfaction_score)
        if not ticket_id or not satisfaction_score:
            return Response({'status':'false','message':'Please add required fields'})
        ticket_data=Ticket.objects.filter(id=ticket_id,user=request.user,submission_status="Resolved").first()
        if not ticket_data:
            return Response({'status': 'false', 'message': 'Ticket not found or not resolved'})
        ticket_data.satisfaction_score=score
        ticket_data.save()
        return Response({'status':'true','message':'Satisfaction Score Updated Successfully'})
        

    
