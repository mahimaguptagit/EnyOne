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
            login(request,user)
            token=get_tokens_for_user(user)
            return Response({'status':'true','access_token':token,'message':'LogIn Successfully'})
        return Response({'status':'false','message':'Check UserName or Password !!'})
    
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request,format=None):
        try:
            userdata=User.objects.filter(id=request.user.id).first()
            userdetail={
                "username":userdata.username,
                "first_name":userdata.first_name,
                "last_name":userdata.last_name,
                "email":userdata.email,
                "image":userdata.image.url,
                "phone_number":userdata.phone_number,}
            return Response({'status':'true','message':'User Profile Data','user_data':userdetail})
        except User.DoesNotExist:
            return Response({'status':'false','message':'User data not found !!'})


# class UserRaiseTicketView(APIView):
#     permission_classes=[IsAuthenticated]
#     def post(self,request,format=None):
#         userdata=request.user
#         serializer = TicketSerializer(data=request.data)
#         if serializer.is_valid():
#             data = serializer.validated_data
#             try:
#                 user=request.user
#                 userdata=User.objects.filter(id=user.id)
#                 ticket_type=data['ticket_type']
#                 ticket_title=data['ticket_title']
#                 priority_level=data['priority_level']
#                 ticket_description=data['ticket_description']
#                 ticket_file=data['ticket_file']
#                 booking_id = Ticket.objects.latest('id').id +1 if Ticket.objects.exists() else 1
#                 timestamp_part = datetime.now().strftime('%y%m%d%H%M%S%f')[:-3]
#                 ticket_number = f"ENYONE0260{booking_id}{timestamp_part}"
#                 ticket_data=Ticket.objects.create(user=userdata,ticket_type=ticket_type,ticket_title=ticket_title,ticket_description=ticket_description,ticket_number=ticket_number,priority_level=priority_level,ticket_file=ticket_file)
#                 return Response({'status':'true','message':'Ticket Raise Successfully'})
#             except User.DoesNotExist:
#                 return Response({'status':'false','message':'User not Found'})
    
class UserRaiseTicketView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        # Get the logged-in user
        user = request.user

        # Deserialize and validate the request data
        serializer = TicketSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            # Extract data from validated serializer
            ticket_type = data.get('ticket_type')
            ticket_title = data.get('ticket_title')
            priority_level = data.get('priority_level')
            ticket_description = data.get('ticket_description')
            ticket_file = data.get('ticket_file')

            try:
                # Generate ticket number
                latest_ticket_id = Ticket.objects.latest('id').id + 1 if Ticket.objects.exists() else 1
                timestamp_part = datetime.now().strftime('%y%m%d%H%M%S%f')[:-3]
                ticket_number = f"ENYONE0{latest_ticket_id}0{timestamp_part}"

                # Create ticket record
                ticket_data = Ticket.objects.create(
                    user=user,
                    ticket_type=ticket_type,
                    ticket_title=ticket_title,
                    ticket_description=ticket_description,
                    ticket_number=ticket_number,
                    priority_level=priority_level,
                    ticket_file=ticket_file
                )

                return Response({'status': 'true', 'message': 'Ticket raised successfully'}, status=201)

            except Exception as e:
                return Response({'status': 'false', 'message': str(e)})
        
        return Response({'status': 'false', 'message': 'Invalid data', 'errors': serializer.errors})
    

class ShowRaisedTicketDataView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        ticket_type=request.data.get('ticket_type')
        ticket_datas=Ticket.objects.filter(user=request.user,ticket_type=ticket_type)
        ticketdetails=[{
            "ticket_type":ticket_data.ticket_type,
            "ticket_title":ticket_data.ticket_title,
            "ticket_description":ticket_data.ticket_description,
            "ticket_number":ticket_data.ticket_number,
            "priority_level":ticket_data.priority_level,
            "ticket_file":ticket_data.ticket_file.url if ticket_data.ticket_file else None,
            "submission_status":ticket_data.submission_status,
            "assigned_request":ticket_data.assigned_request.id if ticket_data.assigned_request else None,
            "created_at":ticket_data.created_at,
            "solved_date":ticket_data.solved_date,
            "satisfaction_score":ticket_data.satisfaction_score,
            "ticket_type":ticket_data.ticket_type, 
        }
        for ticket_data in ticket_datas
        ]
        return Response({'status':'true','message':'Rised Ticket Data','ticket_details':ticketdetails})


    
