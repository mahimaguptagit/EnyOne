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

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

class UserLoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
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
            if response_data.get('message') == 'Test succesfully!':  # Fixing the message comparison
                
                url1 = f"https://enyone-api2-f5gze2bpdfdwg8eh.southeastasia-01.azurewebsites.net/validate-email/?email={username}"
                
                response2 = requests.get(url1, headers=headers)
                
                if response2.status_code == 200:
                    response_data2 = response2.json()
                    
                    if response_data2.get('is_exist'):
                            userdata = User.objects.filter(is_superuser=False, email=username).first()
                            
                            
                            if userdata.password == password:
                                login(request, userdata)
                                token = get_tokens_for_user(userdata)  
                                return Response({
                                    'status': 'true',
                                    'access_token': token,
                                    'message': 'LogIn Successfully',
                                    'data': response_data2
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
                "image":userdata.image.url if userdata.image else None,
                "phone_number":userdata.phone_number,}
        return Response({'status':'true','message':'User Profile Data','user_data':userdetail})
    
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
        }
        for ticket_data in ticket_datas
        ]
        return Response({'status':'true','message':'Rised Ticket Data','ticket_details':ticketdetails,'user_id':userdata})
    
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
                    'date': date_key,  # Assigning date separately
                    'chat': []  # List to hold messages for this date
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
    

# class TicketChatNumberView(APIView):
#     permission_classes = [IsAuthenticated]
#     def post(self, request, format=None):
#         ticket_id=request.data.get('ticket_id')
#         if not ticket_id :
#             return Response({'status':'false','message':'Please add required field !!'})
#         chat_count=0
#         chat_datas = ChatTicketDetails.objects.filter(ticket_number=ticket_id,is_delete=False,reader=False).order_by('-created_at')
#         for data in chat_datas:
#             if chat_datas.user == request.user:
#                 chat_count=chat_count
#             else:
#                 chat_count+=chat_count
#         return Response({'status':'true','msg':'Notification Count','count':notification_read})
    
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
    
# # api to get token of power bi rest api
# class CheckAccessTokenView(APIView):
#     def post(self, request):
#         try:
#             client = PowerBIClient()
#             return Response({'status':'True',"access_token": client.access_token})
#         except Exception as e:
#             return Response({'status':'False',"error": str(e)})
        
# # api to check workscope in token
# class CheckReportsListView(APIView):
#     def post(self,request):
#         try:
#             client = PowerBIClient()
#             group_id = '7b7c9b1a-8e3b-4612-bc74-a570efc83af0'
#             report_id = '3553e950-7fa5-4d8e-a13e-d62fce7c5d30'

#             report_data = client.get_report(report_id)
#             print("Report Data:", report_data)
#             return Response({'status':'True',"reports": 'reports'})
#         except Exception as e:
#             return Response({'status':'False',"error": str(e)})

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
            sale_quantity = sale.get("FSLL_QUANTITY_FSLL", 0) or 0  
            tax_amount = sale.get("FSLL_TAX_INC_AMNT_FSLL", 0) or 0  

            if sale_date_str and category:
                try:
                    sale_date = datetime.strptime(sale_date_str, "%Y-%m-%d %H:%M:%S")
                    if min_date <= sale_date <= max_date:
                        print(f"Including sale for {category}: {sale_quantity}, Date: {sale_date}")
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
            min_date=datetime.strptime(max_date_str, "%Y-%m-%d") - timedelta(days=7)
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
        pass

class SalesMonthlyComparisonGraphView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        pass

class SalesYearlyComparisonGraphView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        pass

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
