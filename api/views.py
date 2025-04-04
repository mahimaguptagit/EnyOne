from django.shortcuts import render
from rest_framework.views import APIView ,View
from django.contrib.auth import authenticate,login,logout
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from dashboard.models import *
from .serializers import *
from datetime import datetime
from dashboard.utils import *
from .powerbi_service import *
import json
from collections import defaultdict
from datetime import datetime, timedelta
import requests
from django.db.models import Count

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

class UserLoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        phone_verify = request.data.get('device_id')

        if not username or not password or not phone_verify:
            return Response({'status': 'false', 'message': 'Both username and password are required.'})

        url = 'https://enyone-api2-f5gze2bpdfdwg8eh.southeastasia-01.azurewebsites.net/test/'
        headers = {
            'authorization': 'Bearer Mye8MLyEHkcgbba2zfe94HTFwUQjr8Z5tr0FpE41Sb73OYWK3BYMqvxBdVkBzqpP',
            'Content-Type': 'application/json'
        }
        print("Headers being sent:", headers)
        response1 = requests.get(url, headers=headers)
        if response1.status_code == 200:
            response_data = response1.json()
            print(response_data)
            if response_data.get('message') == 'Test succesfully!':
                
                url1 = f"https://enyone-api2-f5gze2bpdfdwg8eh.southeastasia-01.azurewebsites.net/validate-email/?email={username}"
                
                response2 = requests.get(url1, headers=headers)
                
                if response2.status_code == 200:
                    response_data2 = response2.json()
                    
                    if response_data2.get('is_exist'):
                            userdata = User.objects.filter(is_superuser=False, email=username).first()
                            userdata.phone_verify=phone_verify
                            userdata.save()
                            logo_url = response_data2.get("logo")  

                            if logo_url:
                                    sas_url = generate_sas_url_from_api(logo_url)
                            
                            if userdata.password == password:
                                login(request, userdata)
                                token = get_tokens_for_user(userdata)  
                                return Response({
                                    'status': 'true',
                                    'access_token': token,
                                    'message': 'LogIn Successfully',
                                    'data': response_data2,
                                    'working_logo_url':sas_url,
                                    'show_logo':userdata.logoappearance
                                })
                            else:
                                return Response({'status': 'false', 'message': 'Please Check User Details !!'})
                    
                    else:
                        return Response({'status': 'false', 'message': 'Register Email with EnyOne team !!'})
                
                else:
                    return Response({'status': 'false', 'message': 'Register Email with EnyOne team !!'})

            else:
                return Response({'status': 'false', 'message': 'Check RestAPI'})

        return Response({'status': 'false', 'message': 'Failed to connect to test API'})
        # userdata = User.objects.filter(is_superuser=False, email=username,is_admin=False).first()
        # userdata.phone_verify=phone_verify
        # userdata.save()
                            
        # if userdata:
        #     login(request, userdata)
        #     token = get_tokens_for_user(userdata)  
        #     return Response({'status': 'true', 'access_token': token, 'message': 'LogIn Successfully','data': 'data', 'working_logo_url':'url', 'show_logo':userdata.logoappearance })
        # else:
        #     return Response({'status': 'false', 'message': 'Please Check User Details !!'})
    
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request,format=None):
        userdata=User.objects.filter(id=request.user.id).first()
        if not userdata:
            return Response({'status':'false','message':'User data not found !!'})
        url1 = f"https://enyone-api2-f5gze2bpdfdwg8eh.southeastasia-01.azurewebsites.net/validate-email/?email={userdata.email}"

        headers = {
            'authorization': 'Bearer Mye8MLyEHkcgbba2zfe94HTFwUQjr8Z5tr0FpE41Sb73OYWK3BYMqvxBdVkBzqpP',
            'Content-Type': 'application/json'
        }
                
        response2 = requests.get(url1, headers=headers)
                
        if response2.status_code == 200:
            response_data2 = response2.json()
                    
            if response_data2.get('is_exist'):
                            logo_url = response_data2.get("logo") 
                            if logo_url:
                                    sas_url = generate_sas_url_from_api(logo_url)
                                    userdetail={
                                            "username":userdata.username,
                                            "first_name":userdata.first_name,
                                            "last_name":userdata.last_name,
                                            "email":userdata.email,
                                            "image":userdata.image.url if userdata.image else None,
                                            "phone_number":userdata.phone_number,
                                            "show_logo":userdata.logoappearance,
                                            "working_logo_url": sas_url
                                            }
                                    return Response({'status':'true','message':'User Profile Data','user_data':userdetail})
            else:
                return Response({'status': 'false', 'message': 'Register Email with EnyOne team !!'})
        else:
            return Response({'status': 'false', 'message': 'Check RestAPI'})
    
class UserEmailVerificationView(APIView):
    def post(self,request,format=None):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'status':'false','message':'User with this email does not exist!!'})
        send_otp(user.email)
        return Response({'status':'true','message':'OTP sent successfully! Check your email to reset the password.'})
    
class UserVerifyOtpView(APIView):
    def post(self, request,format=None):
        email = request.data.get('email')
        otp = request.data.get('otp')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
           return Response({'status':'false','message':'User Not Found'})
        if user.otp==otp:
            return Response({'status':'true','message':'Change Password as OTP is correct'})
        else :
            return  Response({'status':'false','message':'OTP Not Matched!!'})
        
class ResetUserPasswordView(APIView):
    def post(self,request,format=None):
        email = request.data.get('email')
        newpassword = request.data.get('newpassword')
        confirmpassword = request.data.get('confirmpassword')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'status':'false','message':'User Not Found'})
        if newpassword != confirmpassword:
            return Response({'status':'false','message':'New Password and Confirm Password must be the same.'})
        user.set_password(newpassword)
        user.save()
        return Response({'status':'true','message':'Password changed successfully!'})

    
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
                send_acknowleadgemnet_confirm(ticket_data.user.email,ticket_data.ticket_number,userdata)
                return Response({'status': 'true', 'message': 'Ticket raised successfully'})

            except Exception as e:
                # return Response({'status': 'false', 'message': str(e)})
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

        unread_chat_counts = (
            ChatTicketDetails.objects.filter(
                ticket_number__user=request.user,
                is_delete=False,
                is_reader=False
            )
            .values('ticket_number_id')
            .annotate(unread_count=Count('id'))
        )
        unread_chat_dict = {entry['ticket_number_id']: entry['unread_count'] for entry in unread_chat_counts}

        userdata=request.user.id
        print(userdata)
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
            "assigned_user_image":ticket_data.assigned_request.image.url if ticket_data.assigned_request and ticket_data.assigned_request.image  else None,
            "created_at": ticket_data.created_at.strftime('%Y-%m-%d %H:%M:%S') if ticket_data.created_at else None,
            "solved_date": ticket_data.solved_date.strftime('%Y-%m-%d %H:%M:%S') if ticket_data.solved_date else None,
            "ticket_type":ticket_data.ticket_type, 
            "is_feedback":ticket_data.is_feedback,
            "unread_chat_count": unread_chat_dict.get(ticket_data.id, 0)
        }
        for ticket_data in ticket_datas
        ]
        return Response({'status':'true','message':'Rised Ticket Data','ticket_details':ticketdetails,'user_id':userdata})
    
class ShowParticularTicketDetailsView(APIView):
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
            "assigned_user_image":ticket_data.assigned_request.image.url if ticket_data.assigned_request and ticket_data.assigned_request.image  else None,
            "created_at": ticket_data.created_at.strftime('%Y-%m-%d %H:%M:%S') if ticket_data.created_at else None,
            "solved_date": ticket_data.solved_date.strftime('%Y-%m-%d %H:%M:%S') if ticket_data.solved_date else None,
            "ticket_type":ticket_data.ticket_type, 
            "is_feedback":ticket_data.is_feedback,
        }
            return Response({'status':'true','message':'Ticket Details !!','ticketdetail':ticket_details})
        else:
            return Response({'status':'false','message':'Ticket ID Not Found '})
        
class AddSatisfactionScoreView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        ticket_id=request.data.get('ticket_id')
        satisfaction_score=request.data.get('satisfaction_score')
        feedback_desciption=request.data.get('feedback_desciption')
        
        score=int(satisfaction_score)
        if not ticket_id or not satisfaction_score:
            return Response({'status':'false','message':'Please add required fields'})
        ticket_data=Ticket.objects.filter(id=ticket_id,user=request.user,submission_status="Resolved").first()
        if not ticket_data:
            return Response({'status': 'false', 'message': 'Ticket not found or not resolved'})
        if ticket_data.is_feedback == True:
            return Response({'status':'false','message':'Feedback already given for the given ticket'})
        TicketFeedback.objects.create(user=request.user,ticket_id=ticket_data,satisfaction_score=score,feedback_desciption=feedback_desciption)
        ticket_data.is_feedback=True
        ticket_data.save()
        return Response({'status':'true','message':'Satisfaction Score Updated Successfully'})
    
class ShowTicketFeedbackView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        ticket_id=request.data.get('ticket_id')
        if not ticket_id :
            return Response({'status':'false','message':'Please add ticket id'})
        ticket_data=Ticket.objects.filter(id=ticket_id,user=request.user,submission_status="Resolved").first()
        if not ticket_data:
            return Response({'status': 'false', 'message': 'Ticket not found or not resolved'})
        if ticket_data.is_feedback == False:
            return Response({'status':'false','message':'Feedback Not Given Yet !!'})
        feedback_data=TicketFeedback.objects.filter(user=request.user,ticket_id=ticket_data).first()
        feedbackdata={
            'user':feedback_data.user.username,
            'ticket_id':feedback_data.ticket_id.id,
            'satisfaction_score':feedback_data.satisfaction_score,
            'feedback_desciption':feedback_data.feedback_desciption
        }
        return Response({'status':'true','message':'Feedback Data For Given Ticket ID','feedback_details':feedbackdata})
    
class ShowNotificationView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        notifi_datas = Notification.objects.filter(receiver=request.user,is_delete=False).order_by('-id')
        for notif in notifi_datas:
                notif.reader=True
                notif.save()
        notifi_data_lists = [
                {
                    'id': notifi_data.id,
                    'receiver': notifi_data.receiver.username,
                    'sender': notifi_data.sender.username,
                    'notification_title': notifi_data.notification_title,
                    'notification_description': notifi_data.notification_description,
                    'reader': notifi_data.reader,
                    'created_at': notifi_data.created_at.strftime('%Y-%m-%d %H:%M:%S') if notifi_data.created_at else None,
                }
                for notifi_data in notifi_datas
            ]
        return Response({'status':'true', 'msg':'Notification Details', "data": notifi_data_lists}) 
    
class NotificationNumberView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,format=None):
        notification_read=Notification.objects.filter(receiver=request.user,reader=False).count()
        return Response({'status':'true','msg':'Notification Count','count':notification_read})
    
class ParticularNotificationDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            noti_id=request.data.get('notification_id')
            notifi_datas = Notification.objects.get(receiver=request.user,id=noti_id,is_delete=False)
            notifi_datas.is_delete = True
            notifi_datas.save()
            return Response({'status':'true', 'msg':'Notification Deleted'}) 
        except Notification.DoesNotExist:
            return Response({'status':'false', 'msg': 'Notification record not found.'})

class ClearAllNotificationView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        notifi_data = Notification.objects.filter(receiver=request.user,is_delete=False)
        for i in notifi_data:
            i.is_delete = True
            i.save()
        return Response({'status':'true', 'msg':'All Notification Delete'})

class ChatTicketCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None): 
        ticket_id=request.data.get('ticket_id')
        message=request.data.get('message')
        if not ticket_id or not message:
            return Response({'status':'false','message':'Please add required fields !!'})
        userdata=User.objects.filter(id=request.user.id).first()
        if not userdata:
            return Response({'status':'false','message':'User Data Not Found'})
        ticketdata=Ticket.objects.filter(id=ticket_id).first()
        if not ticketdata:
            return Response({'status':'false','message':'Ticket Data Not Found'})
        chatdata=ChatTicketDetails.objects.create(ticket_number=ticketdata,user=userdata,chat=message)
        return Response({'status':'true','message':'Chat Send Successfully'})

class ShowTicketChatView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        ticket_id=request.data.get('ticket_id')
        if not ticket_id :
            return Response({'status':'false','message':'Please add required field !!'})
        chat_datas = ChatTicketDetails.objects.filter(ticket_number=ticket_id,is_delete=False).order_by('created_at') 
        for chatdata in chat_datas:
                chatdata.is_reader=True
                chatdata.save()
        chat_data_dict = {}
        for chat_data in chat_datas:
            date_key = chat_data.created_at.strftime('%Y-%m-%d') if chat_data.created_at else 'Unknown'

            if date_key not in chat_data_dict:
                chat_data_dict[date_key] = {
                    'date': date_key,  
                    'chat': []  
                }

            chat_entry = {
                'id': chat_data.id,
                'sender': chat_data.user.username,
                'sender_id': chat_data.user.id,
                'message': chat_data.chat,
                'ticket_id': chat_data.ticket_number.id,
                'reader': chat_data.is_reader,
                'created_at': chat_data.created_at.strftime('%Y-%m-%d %H:%M:%S') if chat_data.created_at else None,
            }

            chat_data_dict[date_key]['chat'].append(chat_entry)
        return Response({'status': 'true', 'msg': 'Chat Details', "data": chat_data_dict.values()})
    

class TicketChatNumberView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        ticket_id=request.data.get('ticket_id')
        chat_counts = ChatTicketDetails.objects.filter(
                ticket_number__user=request.user, 
                ticket_number__id=ticket_id,
                is_delete=False, 
                is_reader=False
            )
        
        return Response({
            'status': 'true',
            'msg': 'Chat Count',
            'ticket_id':ticket_id,
            'count': chat_counts.count()  
        })
    
class ParticularTicketChatDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            chat_id=request.data.get('chat_id')
            if not chat_id :
                return Response({'status':'false','message':'Please add required field !!'})
            chat_datas = ChatTicketDetails.objects.get(id=chat_id,is_delete=False)
            chat_datas.is_delete = True
            chat_datas.save()
            return Response({'status':'true', 'msg':'Chat Deleted'}) 
        except ChatTicketDetails.DoesNotExist:
            return Response({'status':'false', 'msg': 'Chat record not found.'})

class ClearAllTicketChatView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        ticket_id=request.data.get('ticket_id')
        if not ticket_id :
            return Response({'status':'false','message':'Please add required field !!'})
        chat_datas = ChatTicketDetails.objects.filter(ticket_number=ticket_id,is_delete=False)
        for i in chat_datas:
            i.is_delete = True
            i.save()
        return Response({'status':'true', 'msg':'All Chat Delete'})

class SalesGraphDataByStaffView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        min_date_str = request.data.get('min_date')
        max_date_str = request.data.get('max_date')
        companyid = request.data.get('company_id')
        if not (min_date_str and max_date_str and companyid):
            return Response({'status': 'false', 'message': 'All Fields Required'})
        try:
            min_date = datetime.strptime(min_date_str, "%Y-%m-%d")
            max_date = datetime.strptime(max_date_str, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)  
        except ValueError:
            return Response({'status': 'false', 'message': 'Invalid date format. Use YYYY-MM-DD'})

        url = f"https://enyone-api2-f5gze2bpdfdwg8eh.southeastasia-01.azurewebsites.net/sales-data/?company_id={companyid}"
        headers = {
            'Authorization': 'Bearer Mye8MLyEHkcgbba2zfe94HTFwUQjr8Z5tr0FpE41Sb73OYWK3BYMqvxBdVkBzqpP'
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return Response({'status': 'false', 'message': 'Check Rest API'})
        try:
            response_data = response.json()  
            sales_data = response_data.get('sales_data', [])  
        except (json.JSONDecodeError, AttributeError):
            return Response({'status': 'false', 'message': 'Invalid data format received'})

        staff_sales_summary = defaultdict(float)

        for sale in sales_data:
            sale_date_str = sale.get("FSLH_TRANSACTION_DATE_FSLH")
            staff_code = sale.get("FSLH_STAFF_CODE_DEMP")
            sale_quantity = sale.get("FSLL_QUANTITY_FSLL", 0) or 0  
            tax_amount = sale.get("FSLL_TAX_INC_AMNT_FSLL", 0) or 0  

            if sale_date_str and staff_code:
                try:
                    sale_date = datetime.strptime(sale_date_str, "%Y-%m-%d %H:%M:%S")
                    if min_date <= sale_date <= max_date:
                        print(f"Including sale for {staff_code}: {sale_quantity}, Date: {sale_date}")
                        staff_sales_summary[staff_code] += sale_quantity * tax_amount
                except ValueError:
                    continue
        sales_list = [
            {"staff": staff, "CA": round(total_CA, 2)}
            for staff, total_CA in staff_sales_summary.items()
        ]

        if not sales_list:
            return Response({'status': 'true', 'message': 'No data available for the selected date range','data':[]})

        return Response({'status': 'true', 'data': sales_list})
   

class SalesGraphDataBySalesChannelView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        min_date_str = request.data.get('min_date')
        max_date_str = request.data.get('max_date')
        companyid = request.data.get('company_id')
        if not (min_date_str and max_date_str and companyid):
            return Response({'status': 'false', 'message': 'All Fields Required'})
        try:
            min_date = datetime.strptime(min_date_str, "%Y-%m-%d")
            max_date = datetime.strptime(max_date_str, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)  
        except ValueError:
            return Response({'status': 'false', 'message': 'Invalid date format. Use YYYY-MM-DD'})

        url = f"https://enyone-api2-f5gze2bpdfdwg8eh.southeastasia-01.azurewebsites.net/sales-data/?company_id={companyid}"
        headers = {
            'Authorization': 'Bearer Mye8MLyEHkcgbba2zfe94HTFwUQjr8Z5tr0FpE41Sb73OYWK3BYMqvxBdVkBzqpP'
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return Response({'status': 'false', 'message': 'Check Rest API'})
        try:
            response_data = response.json()  
            sales_data = response_data.get('sales_data', [])  
        except (json.JSONDecodeError, AttributeError):
            return Response({'status': 'false', 'message': 'Invalid data format received'})

        channel_sales_summary = defaultdict(float)

        for sale in sales_data:
            sale_date_str = sale.get("FSLH_TRANSACTION_DATE_FSLH")
            channel_code = sale.get("FSLL_CANAL_DE_VENTE_TYPE_LBL_FSLL")
            sale_quantity = sale.get("FSLL_QUANTITY_FSLL", 0) or 0  
            tax_amount = sale.get("FSLL_TAX_INC_AMNT_FSLL", 0) or 0  

            if sale_date_str and channel_code:
                try:
                    sale_date = datetime.strptime(sale_date_str, "%Y-%m-%d %H:%M:%S")
                    if min_date <= sale_date <= max_date:
                        print(f"Including sale for {channel_code}: {sale_quantity}, Date: {sale_date}")
                        channel_sales_summary[channel_code] += sale_quantity * tax_amount
                except ValueError:
                    continue
        sales_list = [
            {"Channel_name": channel_code, "CA": round(total_CA, 2)}
            for channel_code, total_CA in channel_sales_summary.items()
        ]

        if not sales_list:
            return Response({'status': 'true', 'message': 'No data available for the selected date range','data':[]})

        return Response({'status': 'true', 'data': sales_list})
    
class SalesGraphDataByCategoryView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        min_date_str = request.data.get('min_date')
        max_date_str = request.data.get('max_date')
        companyid = request.data.get('company_id')
        if not (min_date_str and max_date_str and companyid):
            return Response({'status': 'false', 'message': 'All Fields Required'})
        try:
            min_date = datetime.strptime(min_date_str, "%Y-%m-%d")
            max_date = datetime.strptime(max_date_str, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)  
        except ValueError:
            return Response({'status': 'false', 'message': 'Invalid date format. Use YYYY-MM-DD'})

        url = f"https://enyone-api2-f5gze2bpdfdwg8eh.southeastasia-01.azurewebsites.net/sales-data/?company_id={companyid}"
        headers = {
            'Authorization': 'Bearer Mye8MLyEHkcgbba2zfe94HTFwUQjr8Z5tr0FpE41Sb73OYWK3BYMqvxBdVkBzqpP'
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return Response({'status': 'false', 'message': 'Check Rest API'})
        try:
            response_data = response.json()  
            sales_data = response_data.get('sales_data', [])  
        except (json.JSONDecodeError, AttributeError):
            return Response({'status': 'false', 'message': 'Invalid data format received'})

        category_sales_summary = defaultdict(float)

        for sale in sales_data:
            sale_date_str = sale.get("FSLH_TRANSACTION_DATE_FSLH")
            category = sale.get("DFPR_MAIN_CATEGORY_LBL_DFPR")
            sale_quantity = float(sale.get("FSLL_QUANTITY_FSLL", 0) or 0)  
            tax_amount = float(sale.get("FSLL_TAX_INC_AMNT_FSLL", 0) or 0)  

            if sale_date_str:
                try:
                    sale_date = datetime.strptime(sale_date_str, "%Y-%m-%d %H:%M:%S")
                    if min_date <= sale_date <= max_date:
                        category_sales_summary[category] += sale_quantity * tax_amount
                except ValueError:
                    continue
        
        sales_list = [
            {"category": category, "CA": round(total_CA, 2)}
            for category, total_CA in category_sales_summary.items()
        ]
        if not sales_list:
            return Response({'status': 'true', 'message': 'No data available for the selected date range','data':[]})

        return Response({'status': 'true', 'data': sales_list})
    

class SalesPerHourWeeklyView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        max_date_str = request.data.get('max_date') 
        companyid = request.data.get('company_id')
        
        if not (max_date_str and companyid):
            return Response({'status': 'false', 'message': 'All Fields Required'})

        try:
            min_date=datetime.strptime(max_date_str, "%Y-%m-%d") - timedelta(days=6)
            max_date = datetime.strptime(max_date_str, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)  
        except ValueError:
            return Response({'status': 'false', 'message': 'Invalid date format. Use YYYY-MM-DD'})
        
        url = f"https://enyone-api2-f5gze2bpdfdwg8eh.southeastasia-01.azurewebsites.net/sales-data/?company_id={companyid}"
        headers = {
            'Authorization': 'Bearer Mye8MLyEHkcgbba2zfe94HTFwUQjr8Z5tr0FpE41Sb73OYWK3BYMqvxBdVkBzqpP'
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return Response({'status': 'false', 'message': 'Check Rest API'})
        try:
            response_data = response.json()  
            sales_data = response_data.get('sales_data', [])  
        except (json.JSONDecodeError, AttributeError):
            return Response({'status': 'false', 'message': 'Invalid data format received'})
        
        sales_per_hour = defaultdict(lambda: {'total_quantity': 0, 'total_tax_amount': 0})

        for sale in sales_data:
            try:
                sale_datetime = datetime.strptime(sale["FSLH_TRANSACTION_DATE_FSLH"], "%Y-%m-%d %H:%M:%S")
                if min_date <= sale_datetime <= max_date:
                    sale_hour = sale_datetime.hour
                    sales_per_hour[sale_hour]['total_quantity'] += float(sale["FSLL_QUANTITY_FSLL"])
                    sales_per_hour[sale_hour]['total_tax_amount'] += float(sale["FSLL_TAX_INC_AMNT_FSLL"])
            except (ValueError, KeyError):
                continue  

        sales_chart_data = [
            {"SaleHour": hour, "CA": data["total_quantity"] * data["total_tax_amount"]}
            for hour, data in sorted(sales_per_hour.items())
        ]

        return Response({'status': 'true', 'data': sales_chart_data})
    

class SalesPerHourMonthlyView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        max_date_str = request.data.get('max_date') 
        companyid = request.data.get('company_id')
        
        if not (max_date_str and companyid):
            return Response({'status': 'false', 'message': 'All Fields Required'})

        try:
            min_date = datetime.strptime(max_date_str, "%Y-%m-%d") - timedelta(days=30)
            max_date = datetime.strptime(max_date_str, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)  
        except ValueError:
            return Response({'status': 'false', 'message': 'Invalid date format. Use YYYY-MM-DD'})
        
        url = f"https://enyone-api2-f5gze2bpdfdwg8eh.southeastasia-01.azurewebsites.net/sales-data/?company_id={companyid}"
        headers = {
            'Authorization': 'Bearer Mye8MLyEHkcgbba2zfe94HTFwUQjr8Z5tr0FpE41Sb73OYWK3BYMqvxBdVkBzqpP'
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return Response({'status': 'false', 'message': 'Check Rest API'})
        try:
            response_data = response.json()  
            sales_data = response_data.get('sales_data', [])  
        except (json.JSONDecodeError, AttributeError):
            return Response({'status': 'false', 'message': 'Invalid data format received'})
        
        sales_per_hour = defaultdict(lambda: {'total_quantity': 0, 'total_tax_amount': 0})

        for sale in sales_data:
            try:
                sale_datetime = datetime.strptime(sale["FSLH_TRANSACTION_DATE_FSLH"], "%Y-%m-%d %H:%M:%S")
                if min_date <= sale_datetime <= max_date:
                    sale_hour = sale_datetime.hour
                    sales_per_hour[sale_hour]['total_quantity'] += float(sale["FSLL_QUANTITY_FSLL"])
                    sales_per_hour[sale_hour]['total_tax_amount'] += float(sale["FSLL_TAX_INC_AMNT_FSLL"])
            except (ValueError, KeyError, TypeError):
                continue  

        sales_chart_data = [
            {"SaleHour": hour, "CA": data["total_quantity"] * data["total_tax_amount"]}
            for hour, data in sorted(sales_per_hour.items())
        ]

        return Response({'status': 'true', 'data': sales_chart_data})
    
class SalesPerHourYearlyView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        max_date_str = request.data.get('max_date') 
        companyid = request.data.get('company_id')
        
        if not (max_date_str and companyid):
            return Response({'status': 'false', 'message': 'All Fields Required'})

        try:
            min_date = datetime.strptime(max_date_str, "%Y-%m-%d") - timedelta(days=365)
            max_date = datetime.strptime(max_date_str, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)  
        except ValueError:
            return Response({'status': 'false', 'message': 'Invalid date format. Use YYYY-MM-DD'})
        
        url = f"https://enyone-api2-f5gze2bpdfdwg8eh.southeastasia-01.azurewebsites.net/sales-data/?company_id={companyid}"
        headers = {
            'Authorization': 'Bearer Mye8MLyEHkcgbba2zfe94HTFwUQjr8Z5tr0FpE41Sb73OYWK3BYMqvxBdVkBzqpP'
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return Response({'status': 'false', 'message': 'Check Rest API'})
        try:
            response_data = response.json()  
            sales_data = response_data.get('sales_data', [])  
        except (json.JSONDecodeError, AttributeError):
            return Response({'status': 'false', 'message': 'Invalid data format received'})
        
        sales_per_hour = defaultdict(lambda: {'total_quantity': 0, 'total_tax_amount': 0})

        for sale in sales_data:
            try:
                sale_datetime = datetime.strptime(sale["FSLH_TRANSACTION_DATE_FSLH"], "%Y-%m-%d %H:%M:%S")
                if min_date <= sale_datetime <= max_date:
                    sale_hour = sale_datetime.hour
                    sales_per_hour[sale_hour]['total_quantity'] += float(sale["FSLL_QUANTITY_FSLL"])
                    sales_per_hour[sale_hour]['total_tax_amount'] += float(sale["FSLL_TAX_INC_AMNT_FSLL"])
            except (ValueError, KeyError, TypeError):
                continue  

        sales_chart_data = [
            {"SaleHour": hour, "CA": data["total_quantity"] * data["total_tax_amount"]}
            for hour, data in sorted(sales_per_hour.items())
        ]

        return Response({'status': 'true', 'data': sales_chart_data})
    
class SalesWeeklyComparisonGraphView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        max_date_str = request.data.get('max_date') 
        companyid = request.data.get('company_id')
        if not (max_date_str and companyid):
            return Response({'status': 'false', 'message': 'All Fields Required'})
        try:
            max_date = datetime.strptime(max_date_str, "%Y-%m-%d").date()
            min_date_prev_week = max_date - timedelta(days=13)  
            max_date_prev_week = max_date - timedelta(days=7)   
            min_date_curr_week = max_date - timedelta(days=6)   
            max_date_curr_week = max_date 

        except ValueError:
            return Response({'status': 'false', 'message': 'Invalid date format'})

        url = f"https://enyone-api2-f5gze2bpdfdwg8eh.southeastasia-01.azurewebsites.net/sales-data/?company_id={companyid}"
        headers = {
            'Authorization': 'Bearer Mye8MLyEHkcgbba2zfe94HTFwUQjr8Z5tr0FpE41Sb73OYWK3BYMqvxBdVkBzqpP'
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return Response({'status': 'false', 'message': 'Check Rest API'})

        try:
            response_data = response.json()
            sales_data = response_data.get('sales_data', [])
        except (json.JSONDecodeError, AttributeError):
            return Response({'status': 'false', 'message': 'Invalid data format received'})

        sales_per_day = defaultdict(lambda: {'current_week': 0, 'previous_week': 0})

        for sale in sales_data:
            try:
                sale_datetime = datetime.strptime(sale["FSLH_TRANSACTION_DATE_FSLH"], "%Y-%m-%d %H:%M:%S").date()
                sale_day = sale_datetime.strftime("%A") 
                sale_value = float(sale["FSLL_QUANTITY_FSLL"]) * float(sale["FSLL_TAX_INC_AMNT_FSLL"])

                if min_date_prev_week <= sale_datetime <= max_date_prev_week:
                    sales_per_day[sale_day]['previous_week'] += sale_value

                if min_date_curr_week <= sale_datetime <= max_date_curr_week:
                    sales_per_day[sale_day]['current_week'] += sale_value

            except (ValueError, KeyError, TypeError):
                continue  

        sales_comparison_data = [
            {"Day": day, "CurrentWeek": data["current_week"], "PreviousWeek": data["previous_week"]}
            for day, data in sales_per_day.items()
        ]

        return Response({'status': 'true', 'data': sales_comparison_data})

class SalesMonthlyComparisonGraphView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        max_date_str = request.data.get('max_date') 
        companyid = request.data.get('company_id')
        if not (max_date_str and companyid):
            return Response({'status': 'false', 'message': 'All Fields Required'})
        try:
            max_date = datetime.strptime(max_date_str, "%Y-%m-%d").date()
            min_date_curr_month = max_date.replace(day=1)
            max_date_curr_month = max_date
            first_day_prev_month = (min_date_curr_month - timedelta(days=1)).replace(day=1)
            last_day_prev_month = min_date_curr_month - timedelta(days=1)

        except ValueError:
            return Response({'status': 'false', 'message': 'Invalid date '})

        url = f"https://enyone-api2-f5gze2bpdfdwg8eh.southeastasia-01.azurewebsites.net/sales-data/?company_id={companyid}"
        headers = {
            'Authorization': 'Bearer Mye8MLyEHkcgbba2zfe94HTFwUQjr8Z5tr0FpE41Sb73OYWK3BYMqvxBdVkBzqpP'
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return Response({'status': 'false', 'message': 'Check Rest API'})

        try:
            response_data = response.json()
            sales_data = response_data.get('sales_data', [])
        except (json.JSONDecodeError, AttributeError):
            return Response({'status': 'false', 'message': 'Invalid data format received'})

        sales_per_day = defaultdict(lambda: {'current_month': 0, 'previous_month': 0})

        for sale in sales_data:
            try:
                sale_datetime = datetime.strptime(sale["FSLH_TRANSACTION_DATE_FSLH"], "%Y-%m-%d %H:%M:%S").date()
                sale_day = sale_datetime.day 

                sale_value = float(sale["FSLL_QUANTITY_FSLL"]) * float(sale["FSLL_TAX_INC_AMNT_FSLL"])

                if first_day_prev_month <= sale_datetime <= last_day_prev_month:
                    sales_per_day[sale_day]['previous_month'] += sale_value

                if min_date_curr_month <= sale_datetime <= max_date_curr_month:
                    sales_per_day[sale_day]['current_month'] += sale_value

            except (ValueError, KeyError, TypeError):
                continue  

        sales_comparison_data = [
            {"Day": day, "CurrentMonth": data["current_month"], "PreviousMonth": data["previous_month"]}
            for day, data in sorted(sales_per_day.items())
        ]
        return Response({'status': 'true', 'data': sales_comparison_data})
    
class SalesYearlyComparisonGraphView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        max_date_str = request.data.get('max_date')
        companyid = request.data.get('company_id')

        if not (max_date_str and companyid):
            return Response({'status': 'false', 'message': 'All Fields Required'})

        try:
            max_date = datetime.strptime(max_date_str, "%Y-%m-%d")
            min_date_curr_year = datetime(max_date.year, 1, 1)
            max_date_curr_year = datetime(max_date.year, max_date.month, max_date.day, 23, 59, 59)
            min_date_prev_year = datetime(max_date.year - 1, 1, 1)
            max_date_prev_year = datetime(max_date.year - 1, 12, 31, 23, 59, 59)
        except ValueError:
            return Response({'status': 'false', 'message': 'Invalid date format. Use YYYY-MM-DD'})

        url = f"https://enyone-api2-f5gze2bpdfdwg8eh.southeastasia-01.azurewebsites.net/sales-data/?company_id={companyid}"
        headers = {
            'Authorization': 'Bearer Mye8MLyEHkcgbba2zfe94HTFwUQjr8Z5tr0FpE41Sb73OYWK3BYMqvxBdVkBzqpP'
        }
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return Response({'status': 'false', 'message': 'Check Rest API'})

        try:
            response_data = response.json()
            sales_data = response_data.get('sales_data', [])
        except (json.JSONDecodeError, AttributeError):
            return Response({'status': 'false', 'message': 'Invalid data format received'})

        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        sales_per_month = defaultdict(lambda: {'current_year': 0, 'previous_year': 0})

        for sale in sales_data:
            try:
                sale_datetime = datetime.strptime(sale["FSLH_TRANSACTION_DATE_FSLH"], "%Y-%m-%d %H:%M:%S")
                sale_month_name = month_names[sale_datetime.month - 1]  
                sale_value = float(sale["FSLL_QUANTITY_FSLL"]) * float(sale["FSLL_TAX_INC_AMNT_FSLL"])

                if min_date_prev_year <= sale_datetime <= max_date_prev_year:
                    sales_per_month[sale_month_name]['previous_year'] += sale_value

                if min_date_curr_year <= sale_datetime <= max_date_curr_year:
                    sales_per_month[sale_month_name]['current_year'] += sale_value

            except (ValueError, KeyError, TypeError):
                continue  

        sales_comparison_data = [
            {"Month": month, "CurrentYear": data["current_year"], "PreviousYear": data["previous_year"]}
            for month, data in sorted(sales_per_month.items(), key=lambda x: month_names.index(x[0]))
        ]
        return Response({'status': 'true', 'data': sales_comparison_data})

class SalesGraphTotalSalesDataView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        companyid = request.data.get('company_id')
        
        if not companyid:
            return Response({'status': 'false', 'message': 'Company ID is required'})

        url = f"https://enyone-api2-f5gze2bpdfdwg8eh.southeastasia-01.azurewebsites.net/sales-data/?company_id={companyid}"
        headers = {
            'Authorization': 'Bearer Mye8MLyEHkcgbba2zfe94HTFwUQjr8Z5tr0FpE41Sb73OYWK3BYMqvxBdVkBzqpP'
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return Response({'status': 'false', 'message': 'Check Rest API'})

        try:
            response_data = response.json()
            sales_data = response_data.get('sales_data', [])
        except (json.JSONDecodeError, AttributeError):
            return Response({'status': 'false', 'message': 'Invalid data format received'})

        total_sales = 0

        for sale in sales_data:
            try:
                quantity = float(sale["FSLL_QUANTITY_FSLL"])
                tax_amount = float(sale["FSLL_TAX_INC_AMNT_FSLL"])
                total_sales += quantity * tax_amount
            except (ValueError, KeyError, TypeError):
                continue  

        return Response({'status': 'true', 'total_sales': total_sales})


class SalesGraphTodayTotalSalesDataView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        companyid = request.data.get('company_id')
        filter_date = request.data.get('max_date')

        if not (companyid and filter_date):
            return Response({'status': 'false', 'message': 'Company ID and Date are required'})
        try:
            datetime.strptime(filter_date, "%Y-%m-%d")
        except ValueError:
            return Response({'status': 'false', 'message': 'Invalid date format'})

        url = f"https://enyone-api2-f5gze2bpdfdwg8eh.southeastasia-01.azurewebsites.net/sales-data/?company_id={companyid}"
        headers = {
            'Authorization': 'Bearer Mye8MLyEHkcgbba2zfe94HTFwUQjr8Z5tr0FpE41Sb73OYWK3BYMqvxBdVkBzqpP'
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return Response({'status': 'false', 'message': 'Check Rest API'})

        try:
            response_data = response.json()
            sales_data = response_data.get('sales_data', [])
        except (json.JSONDecodeError, AttributeError):
            return Response({'status': 'false', 'message': 'Invalid data format received'})

        total_sales = 0

        for sale in sales_data:
            try:
                sale_date = sale["FSLH_TRANSACTION_DATE_FSLH"][:10]
                if sale_date == filter_date:
                    quantity = float(sale["FSLL_QUANTITY_FSLL"])
                    tax_amount = float(sale["FSLL_TAX_INC_AMNT_FSLL"])
                    total_sales += quantity * tax_amount
            except (ValueError, KeyError, TypeError):
                continue  

        return Response({'status': 'true', 'total_sales': total_sales})
    
class LastRefreshedDateDataView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        companyid = request.data.get('company_id')
        if not (companyid ):
            return Response({'status': 'false', 'message': 'Company ID are required'})

        url = f"https://enyone-api2-f5gze2bpdfdwg8eh.southeastasia-01.azurewebsites.net/sales-data/?company_id={companyid}"
        headers = {
            'Authorization': 'Bearer Mye8MLyEHkcgbba2zfe94HTFwUQjr8Z5tr0FpE41Sb73OYWK3BYMqvxBdVkBzqpP'
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return Response({'status': 'false', 'message': 'Check Rest API'})
        try:
            response_data = response.json()
            date = response_data.get('last_refresh')
        except (json.JSONDecodeError, AttributeError):
            return Response({'status': 'false', 'message': 'Invalid data format received'})
        return Response({'status': 'true', 'last_refresh_date': date})
    

class ProductGraphTodayProductSoldView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        companyid = request.data.get('company_id')
        filter_date = request.data.get('max_date')

        if not (companyid and filter_date):
            return Response({'status': 'false', 'message': 'Company ID and Date are required'})
        try:
            datetime.strptime(filter_date, "%Y-%m-%d")
        except ValueError:
            return Response({'status': 'false', 'message': 'Invalid date format'})

        url = f"https://enyone-api2-f5gze2bpdfdwg8eh.southeastasia-01.azurewebsites.net/sales-data/?company_id={companyid}"
        headers = {
            'Authorization': 'Bearer Mye8MLyEHkcgbba2zfe94HTFwUQjr8Z5tr0FpE41Sb73OYWK3BYMqvxBdVkBzqpP'
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return Response({'status': 'false', 'message': 'Check Rest API'})

        try:
            response_data = response.json()
            product_data = response_data.get('sales_data', [])
        except (json.JSONDecodeError, AttributeError):
            return Response({'status': 'false', 'message': 'Invalid data format received'})

        total_product = 0

        for product in product_data:
            try:
                sale_date = product["FSLH_TRANSACTION_DATE_FSLH"][:10]
                if sale_date == filter_date:
                    quantity = float(product["FSLL_QUANTITY_FSLL"])
                    total_product += quantity 
            except (ValueError, KeyError, TypeError):
                continue  

        return Response({'status': 'true', 'total_productsold': total_product})
    
class ProductGraphTodayAverageNumberProductperCustomerView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        companyid = request.data.get('company_id')
        filter_date = request.data.get('max_date')
        if not (companyid and filter_date):
            return Response({'status': 'false', 'message': 'Company ID and Date are required'})
        try:
            datetime.strptime(filter_date, "%Y-%m-%d")
        except ValueError:
            return Response({'status': 'false', 'message': 'Invalid date format'})

        url = f"https://enyone-api2-f5gze2bpdfdwg8eh.southeastasia-01.azurewebsites.net/sales-data/?company_id={companyid}"
        headers = {
            'Authorization': 'Bearer Mye8MLyEHkcgbba2zfe94HTFwUQjr8Z5tr0FpE41Sb73OYWK3BYMqvxBdVkBzqpP'
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return Response({'status': 'false', 'message': 'Check Rest API'})

        try:
            response_data = response.json()
            product_data = response_data.get('sales_data', [])
        except (json.JSONDecodeError, AttributeError):
            return Response({'status': 'false', 'message': 'Invalid data format received'})

        total_today_product = 0
        today_client_count = 0


        for product in product_data:
            try:
                sale_date = product["FSLH_TRANSACTION_DATE_FSLH"][:10]
                client_id = product.get("FSLH_CLIENT_ID_DCLT")
                quantity = float(product.get("FSLL_QUANTITY_FSLL", 0) or 0)
                if sale_date == filter_date and client_id:
                    today_client_count += 1
                    total_today_product += quantity 
            except (ValueError, KeyError, TypeError):
                continue  

        average_of_product_per_client = round(total_today_product / today_client_count, 2) if today_client_count > 0 else 0

        return Response({'status': 'true', 'averageofproductspercustomers': average_of_product_per_client})
    
class ProductGraphDataByTopProductsByQuantityView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        min_date_str = request.data.get('min_date')
        max_date_str = request.data.get('max_date')
        companyid = request.data.get('company_id')
        if not (min_date_str and max_date_str and companyid):
            return Response({'status': 'false', 'message': 'All Fields Required'})
        try:
            min_date = datetime.strptime(min_date_str, "%Y-%m-%d")
            max_date = datetime.strptime(max_date_str, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)  
        except ValueError:
            return Response({'status': 'false', 'message': 'Invalid date format. Use YYYY-MM-DD'})

        url = f"https://enyone-api2-f5gze2bpdfdwg8eh.southeastasia-01.azurewebsites.net/sales-data/?company_id={companyid}"
        headers = {
            'Authorization': 'Bearer Mye8MLyEHkcgbba2zfe94HTFwUQjr8Z5tr0FpE41Sb73OYWK3BYMqvxBdVkBzqpP'
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return Response({'status': 'false', 'message': 'Check Rest API'})
        try:
            response_data = response.json()  
            sales_data = response_data.get('sales_data', [])  
        except (json.JSONDecodeError, AttributeError):
            return Response({'status': 'false', 'message': 'Invalid data format received'})

        product_quantity_summary = defaultdict(float)

        for sale in sales_data:
            sale_date_str = sale.get("FSLH_TRANSACTION_DATE_FSLH")
            product_code = sale.get("FSLL_PRODUCT_CODE_DFPR")
            sale_quantity = sale.get("FSLL_QUANTITY_FSLL", 0) or 0 

            if sale_date_str and product_code:
                try:
                    sale_date = datetime.strptime(sale_date_str, "%Y-%m-%d %H:%M:%S")
                    if min_date <= sale_date <= max_date:
                        print(f"Including qunatity for {product_code}: {sale_quantity}, Date: {sale_date}")
                        product_quantity_summary[product_code] += sale_quantity 
                except ValueError:
                    continue
        topproduct_quantity_list = [
            {"Product_code": product_code, "Quantity": int(sale_quantity)}
            for product_code, sale_quantity in product_quantity_summary.items()
        ]

        if not topproduct_quantity_list:
            return Response({'status': 'true', 'message': 'No data available for the selected date range','data':[]})

        return Response({'status': 'true', 'data': topproduct_quantity_list})
    
class ProductGraphDataBySalesandBeforeMarginView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        min_date_str = request.data.get('min_date')
        max_date_str = request.data.get('max_date')
        companyid = request.data.get('company_id')

        if not (min_date_str and max_date_str and companyid):
            return Response({'status': 'false', 'message': 'All Fields Required'})

        try:
            min_date = datetime.strptime(min_date_str, "%Y-%m-%d")
            max_date = datetime.strptime(max_date_str, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)  
        except ValueError:
            return Response({'status': 'false', 'message': 'Invalid date format. Use YYYY-MM-DD'})

        url = f"https://enyone-api2-f5gze2bpdfdwg8eh.southeastasia-01.azurewebsites.net/sales-data/?company_id={companyid}"
        headers = {'Authorization': 'Bearer Mye8MLyEHkcgbba2zfe94HTFwUQjr8Z5tr0FpE41Sb73OYWK3BYMqvxBdVkBzqpP'}

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return Response({'status': 'false', 'message': 'Check Rest API'})

        try:
            response_data = response.json()  
            sales_data = response_data.get('sales_data', [])  
        except (json.JSONDecodeError, AttributeError):
            return Response({'status': 'false', 'message': 'Invalid data format received'})

        product_summary = defaultdict(lambda: {'CA': 0, 'cost': 0})

        for sale in sales_data:
            sale_date_str = sale.get("FSLH_TRANSACTION_DATE_FSLH")
            product_code = sale.get("FSLL_PRODUCT_CODE_DFPR")
            sale_quantity = sale.get("FSLL_QUANTITY_FSLL", 0) or 0  
            tax_amount = sale.get("FSLL_TAX_INC_AMNT_FSLL", 0) or 0  
            cost_price = sale.get("DFPR_COST_PRICE_DFPR", 0) or 0  

            if sale_date_str and product_code:
                try:
                    sale_date = datetime.strptime(sale_date_str, "%Y-%m-%d %H:%M:%S")
                    if min_date <= sale_date <= max_date:
                        product_summary[product_code]['CA'] += sale_quantity * tax_amount  
                        product_summary[product_code]['cost'] += sale_quantity * cost_price  
                except ValueError:
                    continue

        topproduct_margin_list = [
            {
                "Product_code": product_code,
                "CA": round(product_data['CA'], 2),
                "Marge_HT": round(product_data['CA'] - product_data['cost'], 2)
            }
            for product_code, product_data in product_summary.items()
        ]

        if not topproduct_margin_list:
            return Response({'status': 'true', 'message': 'No data available for the selected date range', 'data': []})

        return Response({'status': 'true', 'data': topproduct_margin_list})
    

class ProductGraphDataByTodayGrossMarginView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request,fomat=None):
        companyid = request.data.get('company_id')
        filter_date = request.data.get('max_date')

        if not (companyid and filter_date):
            return Response({'status': 'false', 'message': 'Company ID and Date are required'})
        try:
            filter_date_obj = datetime.strptime(filter_date, "%Y-%m-%d").date()
        except ValueError:
            return Response({'status': 'false', 'message': 'Invalid date format'})

        url = f"https://enyone-api2-f5gze2bpdfdwg8eh.southeastasia-01.azurewebsites.net/sales-data/?company_id={companyid}"
        headers = {
            'Authorization': 'Bearer Mye8MLyEHkcgbba2zfe94HTFwUQjr8Z5tr0FpE41Sb73OYWK3BYMqvxBdVkBzqpP'
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return Response({'status': 'false', 'message': 'Check Rest API'})

        try:
            response_data = response.json()
            product_data = response_data.get('sales_data', [])
        except (json.JSONDecodeError, AttributeError):
            return Response({'status': 'false', 'message': 'Invalid data format received'})

        total_CA = 0
        total_cost = 0

        for sale in product_data:
            sale_date_str = sale.get("FSLH_TRANSACTION_DATE_FSLH")
            sale_quantity = sale.get("FSLL_QUANTITY_FSLL", 0) or 0  
            tax_amount = sale.get("FSLL_TAX_INC_AMNT_FSLL", 0) or 0  
            cost_price = sale.get("DFPR_COST_PRICE_DFPR", 0) or 0  

            if sale_date_str:
                try:
                    sale_date = datetime.strptime(sale_date_str, "%Y-%m-%d %H:%M:%S").date()
                    if sale_date == filter_date_obj: 
                        total_CA += sale_quantity * tax_amount  
                        print(total_CA)
                        total_cost += sale_quantity * cost_price  
                        print(total_cost)
                except ValueError:
                    continue

        gross_margin = total_CA - total_cost
        return Response({'status': 'true', 'gross_margindata': round(gross_margin, 2)})


class ProductGraphByFoodCostAndDrinkCostView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request,fomat=None):
        min_date_str = request.data.get('min_date')
        max_date_str = request.data.get('max_date')
        companyid = request.data.get('company_id')

        if not (min_date_str and max_date_str and companyid):
            return Response({'status': 'false', 'message': 'All Fields Required'})

        try:
            min_date = datetime.strptime(min_date_str, "%Y-%m-%d")
            max_date = datetime.strptime(max_date_str, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
        except ValueError:
            return Response({'status': 'false', 'message': 'Invalid date format. Use YYYY-MM-DD'})

        url = f"https://enyone-api2-f5gze2bpdfdwg8eh.southeastasia-01.azurewebsites.net/sales-data/?company_id={companyid}"
        headers = {'Authorization': 'Bearer Mye8MLyEHkcgbba2zfe94HTFwUQjr8Z5tr0FpE41Sb73OYWK3BYMqvxBdVkBzqpP'}

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return Response({'status': 'false', 'message': 'Check Rest API'})

        try:
            response_data = response.json()
            sales_data = response_data.get('sales_data', [])
            materialdata = response_data.get('material_data', [])
        except (requests.exceptions.JSONDecodeError, AttributeError):
            return Response({'status': 'false', 'message': 'Invalid data format received'})

        total_food_cost = 0
        total_drink_cost = 0

        for sale in sales_data:
            sale_date_str = sale.get('FSLH_TRANSACTION_DATE_FSLH')
            if not sale_date_str:
                continue

            try:
                sale_date = datetime.strptime(sale_date_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue  

            if min_date <= sale_date <= max_date:  
                quantity = sale.get('FSLL_QUANTITY_FSLL', 0)
                sale_product_code = sale.get('FSLL_PRODUCT_CODE_DFPR')
                category = sale.get('DFPR_MAIN_CATEGORY_LBL_DFPR')
                print('sale',sale_product_code)

                for material in materialdata:
                    material_product_code = material.get('DPRM_PRODUCT_CODE_DFPR')
                    quantity_used = material.get('DPRM_QUANTITY_USED_DPRM', 0)
                    unit_price = material.get('DRMT_UNIT_PRICE_DRMT', 0)
                    print('material',material_product_code)

                    if sale_product_code == material_product_code:
                        print('materialcomparison',material_product_code)
                        cost = quantity * (quantity_used * unit_price)
                        if category == "AL":  
                            total_food_cost += cost
                        elif category == "BO":  
                            total_drink_cost += cost

        category=[{'Food_Cost': round(total_food_cost, 2),
            'Drink_Cost': round(total_drink_cost, 2)}]

# BO means drink cost and AL means food cost
        return Response({
            'status': 'true',
            'data':category
            
        })


class CustomerGraphByAverageCAPerCustomerView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request,format=None):
        companyid = request.data.get('company_id')
        filter_date = request.data.get('max_date')

        if not (companyid and filter_date):
            return Response({'status': 'false', 'message': 'Company ID and Date are required'})
        try:
            filter_date_obj = datetime.strptime(filter_date, "%Y-%m-%d").date()
        except ValueError:
            return Response({'status': 'false', 'message': 'Invalid date format'})

        url = f"https://enyone-api2-f5gze2bpdfdwg8eh.southeastasia-01.azurewebsites.net/sales-data/?company_id={companyid}"
        headers = {
            'Authorization': 'Bearer Mye8MLyEHkcgbba2zfe94HTFwUQjr8Z5tr0FpE41Sb73OYWK3BYMqvxBdVkBzqpP'
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return Response({'status': 'false', 'message': 'Check Rest API'})

        try:
            response_data = response.json()
            product_data = response_data.get('sales_data', [])
        except (json.JSONDecodeError, AttributeError):
            return Response({'status': 'false', 'message': 'Invalid data format received'})

        total_CA = 0
        total_client_transactions = 0 

        for sale in product_data:
            try:
                sale_date_str = sale.get("FSLH_TRANSACTION_DATE_FSLH")  
                client_id = sale.get("FSLH_CLIENT_ID_DCLT")  
                sale_quantity = float(sale.get("FSLL_QUANTITY_FSLL", 0) or 0)  
                tax_amount = float(sale.get("FSLL_TAX_INC_AMNT_FSLL", 0) or 0)  

                if sale_date_str and client_id:
                    sale_date = datetime.strptime(sale_date_str, "%Y-%m-%d %H:%M:%S").date()

                    if sale_date == filter_date_obj:
                        total_client_transactions += 1 
                        total_CA += sale_quantity * tax_amount  
            except (ValueError, KeyError, TypeError):
                continue  

        average_amount_by_client = round(total_CA / total_client_transactions, 2) if total_client_transactions > 0 else 0

        return Response({'status': 'true', 'averageamountbyclient_data': average_amount_by_client})
    

class CustomerGraphByNumberOfCustomerTodayView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request,format=None):
        companyid = request.data.get('company_id')
        filter_date = request.data.get('max_date')

        if not (companyid and filter_date):
            return Response({'status': 'false', 'message': 'Company ID and Date are required'})
        try:
            filter_date_obj = datetime.strptime(filter_date, "%Y-%m-%d").date()
        except ValueError:
            return Response({'status': 'false', 'message': 'Invalid date format'})

        url = f"https://enyone-api2-f5gze2bpdfdwg8eh.southeastasia-01.azurewebsites.net/sales-data/?company_id={companyid}"
        headers = {
            'Authorization': 'Bearer Mye8MLyEHkcgbba2zfe94HTFwUQjr8Z5tr0FpE41Sb73OYWK3BYMqvxBdVkBzqpP'
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return Response({'status': 'false', 'message': 'Check Rest API'})

        try:
            response_data = response.json()
            product_data = response_data.get('sales_data', [])
        except (json.JSONDecodeError, AttributeError):
            return Response({'status': 'false', 'message': 'Invalid data format received'})

        total_client_transactions = 0 

        for sale in product_data:
            try:
                sale_date_str = sale.get("FSLH_TRANSACTION_DATE_FSLH")  
                client_id = sale.get("FSLH_CLIENT_ID_DCLT") 
                if sale_date_str and client_id:
                    sale_date = datetime.strptime(sale_date_str, "%Y-%m-%d %H:%M:%S").date()

                    if sale_date == filter_date_obj:
                        total_client_transactions += 1 
            except (ValueError, KeyError, TypeError):
                continue  

        return Response({'status': 'true', 'today_numberofcustomer': total_client_transactions})
    
class CustomerGraphNumberOfCustomerPerHourWeeklyView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        max_date_str = request.data.get('max_date') 
        companyid = request.data.get('company_id')
        
        if not (max_date_str and companyid):
            return Response({'status': 'false', 'message': 'All Fields Required'})

        try:
            max_date = datetime.strptime(max_date_str, "%Y-%m-%d")
            min_date = max_date - timedelta(days=6)
            max_date = max_date.replace(hour=23, minute=59, second=59)  
        except ValueError:
            return Response({'status': 'false', 'message': 'Invalid date format. Use YYYY-MM-DD'})
        
        url = f"https://enyone-api2-f5gze2bpdfdwg8eh.southeastasia-01.azurewebsites.net/sales-data/?company_id={companyid}"
        headers = {
            'Authorization': 'Bearer Mye8MLyEHkcgbba2zfe94HTFwUQjr8Z5tr0FpE41Sb73OYWK3BYMqvxBdVkBzqpP'
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return Response({'status': 'false', 'message': 'Check Rest API'})
        try:
            response_data = response.json()  
            sales_data = response_data.get('sales_data', [])  
        except (json.JSONDecodeError, AttributeError):
            return Response({'status': 'false', 'message': 'Invalid data format received'})
        
        transactions_per_hour = defaultdict(int)

        for sale in sales_data:
            try:
                sale_datetime = datetime.strptime(sale["FSLH_TRANSACTION_DATE_FSLH"], "%Y-%m-%d %H:%M:%S")

                if min_date <= sale_datetime <= max_date:
                    sale_hour = sale_datetime.hour
                    transactions_per_hour[sale_hour] += 1  
            except (ValueError, KeyError):
                continue  
        sales_chart_data = [
            {"Hour": hour, "NumberOfClient": count}
            for hour, count in sorted(transactions_per_hour.items())
        ]

        return Response({'status': 'true', 'customer_perhour_data': sales_chart_data})
    

class CustomerGraphNumberOfCustomerPerHourMonthlyView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        max_date_str = request.data.get('max_date') 
        companyid = request.data.get('company_id')
        
        if not (max_date_str and companyid):
            return Response({'status': 'false', 'message': 'All Fields Required'})
        
        try:
            max_date = datetime.strptime(max_date_str, "%Y-%m-%d")
            min_date = max_date - timedelta(days=30) 
            max_date = max_date.replace(hour=23, minute=59, second=59)  
        except ValueError:
            return Response({'status': 'false', 'message': 'Invalid date format. Use YYYY-MM-DD'})

        url = f"https://enyone-api2-f5gze2bpdfdwg8eh.southeastasia-01.azurewebsites.net/sales-data/?company_id={companyid}"
        headers = {
            'Authorization': 'Bearer Mye8MLyEHkcgbba2zfe94HTFwUQjr8Z5tr0FpE41Sb73OYWK3BYMqvxBdVkBzqpP'
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return Response({'status': 'false', 'message': 'Check Rest API'})
        try:
            response_data = response.json()  
            sales_data = response_data.get('sales_data', [])  
        except (json.JSONDecodeError, AttributeError):
            return Response({'status': 'false', 'message': 'Invalid data format received'})
        
        transactions_per_hour = defaultdict(int)

        for sale in sales_data:
            try:
                sale_datetime = datetime.strptime(sale["FSLH_TRANSACTION_DATE_FSLH"], "%Y-%m-%d %H:%M:%S")

                if min_date <= sale_datetime <= max_date:
                    sale_hour = sale_datetime.hour
                    transactions_per_hour[sale_hour] += 1  
            except (ValueError, KeyError):
                continue  
        sales_chart_data = [
            {"Hour": hour, "NumberOfClient": count}
            for hour, count in sorted(transactions_per_hour.items())
        ]

        return Response({'status': 'true', 'customer_perhour_data': sales_chart_data})
    
class CustomerGraphNumberOfCustomerPerHourYearlyView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        max_date_str = request.data.get('max_date') 
        companyid = request.data.get('company_id')
        
        if not (max_date_str and companyid):
            return Response({'status': 'false', 'message': 'All Fields Required'})

        try:
            max_date = datetime.strptime(max_date_str, "%Y-%m-%d")
            min_date = max_date - timedelta(days=365)  
            max_date = max_date.replace(hour=23, minute=59, second=59) 
        except ValueError:
            return Response({'status': 'false', 'message': 'Invalid date format. Use YYYY-MM-DD'})

        
        url = f"https://enyone-api2-f5gze2bpdfdwg8eh.southeastasia-01.azurewebsites.net/sales-data/?company_id={companyid}"
        headers = {
            'Authorization': 'Bearer Mye8MLyEHkcgbba2zfe94HTFwUQjr8Z5tr0FpE41Sb73OYWK3BYMqvxBdVkBzqpP'
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return Response({'status': 'false', 'message': 'Check Rest API'})
        try:
            response_data = response.json()  
            sales_data = response_data.get('sales_data', [])  
        except (json.JSONDecodeError, AttributeError):
            return Response({'status': 'false', 'message': 'Invalid data format received'})
        
        transactions_per_hour = defaultdict(int)

        for sale in sales_data:
            try:
                sale_datetime = datetime.strptime(sale["FSLH_TRANSACTION_DATE_FSLH"], "%Y-%m-%d %H:%M:%S")

                if min_date <= sale_datetime <= max_date:
                    sale_hour = sale_datetime.hour
                    transactions_per_hour[sale_hour] += 1  
            except (ValueError, KeyError):
                continue  
        sales_chart_data = [
            {"Hour": hour, "NumberOfClient": count}
            for hour, count in sorted(transactions_per_hour.items())
        ]

        return Response({'status': 'true', 'customer_perhour_data': sales_chart_data})

class CustomerGraphBySalesChannelView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        min_date_str = request.data.get('min_date')
        max_date_str = request.data.get('max_date')
        companyid = request.data.get('company_id')
        if not (min_date_str and max_date_str and companyid):
            return Response({'status': 'false', 'message': 'All Fields Required'})
        try:
            min_date = datetime.strptime(min_date_str, "%Y-%m-%d")
            max_date = datetime.strptime(max_date_str, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)  
        except ValueError:
            return Response({'status': 'false', 'message': 'Invalid date format. Use YYYY-MM-DD'})

        url = f"https://enyone-api2-f5gze2bpdfdwg8eh.southeastasia-01.azurewebsites.net/sales-data/?company_id={companyid}"
        headers = {
            'Authorization': 'Bearer Mye8MLyEHkcgbba2zfe94HTFwUQjr8Z5tr0FpE41Sb73OYWK3BYMqvxBdVkBzqpP'
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return Response({'status': 'false', 'message': 'Check Rest API'})
        try:
            response_data = response.json()  
            sales_data = response_data.get('sales_data', [])  
        except (json.JSONDecodeError, AttributeError):
            return Response({'status': 'false', 'message': 'Invalid data format received'})

        channel_sales_summary = defaultdict(int)

        for sale in sales_data:
            sale_date_str = sale.get("FSLH_TRANSACTION_DATE_FSLH")
            channel_code = sale.get("FSLL_CANAL_DE_VENTE_TYPE_LBL_FSLL")

            if sale_date_str and channel_code:
                try:
                    sale_date = datetime.strptime(sale_date_str, "%Y-%m-%d %H:%M:%S")
                    if min_date <= sale_date <= max_date:
                        channel_sales_summary[channel_code] += 1
                except ValueError:
                    continue

        sales_list = [
            {"Channel_name": channel_code, "total_number_of_clint": transaction_count}
            for channel_code, transaction_count in channel_sales_summary.items()
        ]

        if not sales_list:
            return Response({'status': 'true', 'message': 'No data available for the selected date range', 'data': []})

        return Response({'status': 'true', 'data': sales_list})
    

class CustomerGraphForNumberOfCustomerPerWeekView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request, format=None):
        max_date_str = request.data.get('max_date') 
        companyid = request.data.get('company_id')

        if not (max_date_str and companyid):
            return Response({'status': 'false', 'message': 'All Fields Required'})

        try:
            max_date = datetime.strptime(max_date_str, "%Y-%m-%d").date()  
            min_date_prev_week = max_date - timedelta(days=13)  
            max_date_prev_week = max_date - timedelta(days=7)   
            min_date_curr_week = max_date - timedelta(days=6)   
            max_date_curr_week = max_date  
        except ValueError:
            return Response({'status': 'false', 'message': 'Invalid date format'})

        url = f"https://enyone-api2-f5gze2bpdfdwg8eh.southeastasia-01.azurewebsites.net/sales-data/?company_id={companyid}"
        headers = {
            'Authorization': 'Bearer Mye8MLyEHkcgbba2zfe94HTFwUQjr8Z5tr0FpE41Sb73OYWK3BYMqvxBdVkBzqpP'
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return Response({'status': 'false', 'message': 'Check Rest API'})

        try:
            response_data = response.json()
            customer_data = response_data.get('sales_data', [])
        except (json.JSONDecodeError, AttributeError):
            return Response({'status': 'false', 'message': 'Invalid data format received'})

        weekly_data = defaultdict(lambda: {'current_week': 0, 'previous_week': 0})

        for sale in customer_data:
            transaction_date_str = sale.get("FSLH_TRANSACTION_DATE_FSLH")

            try:
                transaction_date = datetime.strptime(transaction_date_str, "%Y-%m-%d %H:%M:%S").date()
                weekday_name = transaction_date.strftime("%A")  
            except ValueError:
                continue  

            if min_date_prev_week <= transaction_date <= max_date_prev_week:
                weekly_data[weekday_name]['previous_week'] += 1
            elif min_date_curr_week <= transaction_date <= max_date_curr_week:
                weekly_data[weekday_name]['current_week'] += 1

        customer_comparison_data = [
            {"Day": day, "CurrentWeek": data["current_week"], "PreviousWeek": data["previous_week"]}
            for day, data in weekly_data.items()
        ]

        return Response({'status': 'true', 'customers_per_day': customer_comparison_data})

class CustomerGraphForNumberOfCustomerPerMonthView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request, format=None):
        max_date_str = request.data.get('max_date') 
        companyid = request.data.get('company_id')

        if not (max_date_str and companyid):
            return Response({'status': 'false', 'message': 'All Fields Required'})

        try:
            max_date = datetime.strptime(max_date_str, "%Y-%m-%d").date()
            min_date_curr_month = max_date.replace(day=1)  
            max_date_curr_month = max_date  
            first_day_prev_month = (min_date_curr_month - timedelta(days=1)).replace(day=1)  
            last_day_prev_month = min_date_curr_month - timedelta(days=1)
        except ValueError:
            return Response({'status': 'false', 'message': 'Invalid date format'})

        url = f"https://enyone-api2-f5gze2bpdfdwg8eh.southeastasia-01.azurewebsites.net/sales-data/?company_id={companyid}"
        headers = {
            'Authorization': 'Bearer Mye8MLyEHkcgbba2zfe94HTFwUQjr8Z5tr0FpE41Sb73OYWK3BYMqvxBdVkBzqpP'
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return Response({'status': 'false', 'message': 'Check Rest API'})

        try:
            response_data = response.json()
            sales_data = response_data.get('sales_data', [])
        except (json.JSONDecodeError, AttributeError):
            return Response({'status': 'false', 'message': 'Invalid data format received'})

        sales_per_date = defaultdict(lambda: {'current_month': 0, 'previous_month': 0})

        for sale in sales_data:
            transaction_date_str = sale.get("FSLH_TRANSACTION_DATE_FSLH")

            try:
                transaction_date = datetime.strptime(transaction_date_str, "%Y-%m-%d %H:%M:%S").date()
                transactiondate=transaction_date.day
            except ValueError:
                continue  

            if first_day_prev_month <= transaction_date <= last_day_prev_month:
                sales_per_date[transactiondate]['previous_month'] += 1
            elif min_date_curr_month <= transaction_date <= max_date_curr_month:
                sales_per_date[transactiondate]['current_month'] += 1

        customer_comparison_data = [
            {"Date": date, "CurrentMonth": data["current_month"], "PreviousMonth": data["previous_month"]}
            for date, data in sorted(sales_per_date.items())
        ]

        return Response({'status': 'true', 'customers_per_month': customer_comparison_data})

class CustomerGraphForNumberOfCustomerPerYearView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request,format=None):
        max_date_str = request.data.get('max_date')
        companyid = request.data.get('company_id')

        if not (max_date_str and companyid):
            return Response({'status': 'false', 'message': 'All Fields Required'})

        try:
            max_date = datetime.strptime(max_date_str, "%Y-%m-%d")
            min_date_curr_year = datetime(max_date.year, 1, 1)
            max_date_curr_year = max_date
            min_date_prev_year = datetime(max_date.year - 1, 1, 1)
            max_date_prev_year = datetime(max_date.year - 1, 12, 31)
        except ValueError:
            return Response({'status': 'false', 'message': 'Invalid date format. Use YYYY-MM-DD'})

        url = f"https://enyone-api2-f5gze2bpdfdwg8eh.southeastasia-01.azurewebsites.net/sales-data/?company_id={companyid}"
        headers = {
            'Authorization': 'Bearer Mye8MLyEHkcgbba2zfe94HTFwUQjr8Z5tr0FpE41Sb73OYWK3BYMqvxBdVkBzqpP'
        }
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return Response({'status': 'false', 'message': 'Check Rest API'})

        try:
            response_data = response.json()
            sales_data = response_data.get('sales_data', [])
        except (json.JSONDecodeError, AttributeError):
            return Response({'status': 'false', 'message': 'Invalid data format received'})

        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        sales_per_month = defaultdict(lambda: {'current_year': 0, 'previous_year': 0})

        for sale in sales_data:
            transaction_date_str = sale.get("FSLH_TRANSACTION_DATE_FSLH")

            try:
                transaction_date = datetime.strptime(transaction_date_str, "%Y-%m-%d %H:%M:%S")
                transaction_month = transaction_date.month  
            except ValueError:
                continue  

            month_label = month_names[transaction_month - 1]  

            if min_date_prev_year <= transaction_date <= max_date_prev_year:
                sales_per_month[month_label]['previous_year'] += 1
            elif min_date_curr_year <= transaction_date <= max_date_curr_year:
                sales_per_month[month_label]['current_year'] += 1

        customer_comparison_data = [
            {"Month": month, "CurrentYear": data["current_year"], "PreviousYear": data["previous_year"]}
            for month, data in sorted(sales_per_month.items(), key=lambda x: month_names.index(x[0]))
        ]

        return Response({'status': 'true', 'customers_per_month': customer_comparison_data})
        

class ShowCompanyLogoView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request,format=None):
        try:
            user_id=request.user.id
            userdata=User.objects.filter(id=user_id).first()
            userdata.logoappearance = not userdata.logoappearance
            userdata.save()
            return Response({'status':'true','message':'Logo Status change successfully'})
        except User.DoesNotExist:
            return Response({'status':'false','message':'Check User ID'})
        
class ShowAllRaisedTicketFeedbackView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        userdata=request.user.id
        ticket_datas=TicketFeedback.objects.filter(user=userdata).order_by('-id')
        
        ticketdetails=[{
            "ticket_id":ticket_data.ticket_id.id,
            "ticket_type":ticket_data.ticket_id.ticket_type,
            "ticket_title":ticket_data.ticket_id.ticket_title,
            "ticket_number":ticket_data.ticket_id.ticket_number,
            "satisfaction_score":ticket_data.satisfaction_score,
            "feedback_desciption":ticket_data.feedback_desciption,
            "userid":ticket_data.user.id
        }
        for ticket_data in ticket_datas
        ]
        return Response({'status':'true','message':'Rised Ticket Feedback Data','ticketfeedback_details':ticketdetails})