# # from flask import Blueprint, render_template,request, redirect

# # home = Blueprint("home", __name__)


# # @home.before_request
# # def redirect_to_https():
# #     """Redirect www and HTTP requests to https://salimtv.com"""
# #     url = request.url
# #     if url.startswith("http://www.salimtv.com"):
# #         return redirect(url.replace("http://www.salimtv.com", "https://salimtv.com"), code=301)
# #     elif url.startswith("http://"):
# #         return redirect(url.replace("http://", "https://"), code=301)

# # @home.route('/')
# # @home.route('/home/')
# # def index():
# # 	return render_template('index.html')


# import logging
# from flask import request, redirect

# # Configure logging
# logging.basicConfig(level=logging.DEBUG)

# @home.before_request
# def redirect_to_https():
#     """Redirect www and HTTP requests to https://salimtv.com"""
#     url = request.url
#     logging.debug(f"Incoming request URL: {url}")  # Log the request URL

#     if url.startswith("http://www.salimtv.com"):
#         new_url = url.replace("http://www.salimtv.com", "https://salimtv.com")
#         logging.debug(f"Redirecting to: {new_url}")  # Log the redirection
#         return redirect(new_url, code=301)

#     elif url.startswith("http://"):
#         new_url = url.replace("http://", "https://")
#         logging.debug(f"Redirecting to: {new_url}")  # Log the redirection
#         return redirect(new_url, code=301)

#     logging.debug("No redirection applied")  # Log if no redirection happens we need if we hit http://www.salimtv.com/ then it will redirect to https://salimtv.com/


class PowerBILogoView(APIView):
    def get(self,request,format=None):
        logoget=request.data.get('logo')
        User.objects.create(username=username,logo=logo,firstname=firstname,lastname=lastname)



        

class TicketFeedback(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    ticket_id=models.ForeignKey(Ticket,on_delete=models.CASCADE)
    satisfaction_score=models.PositiveIntegerField(null=True,blank=True) 
    feedback_desciption=models.CharField(max_length=225,null=True,blank=True)












class SalesWeeklyComparisonGraphView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        max_date_str = request.data.get('max_date') 
        companyid = request.data.get('company_id')
        if not (max_date_str and companyid):
            return Response({'status': 'false', 'message': 'All Fields Required'})
        try:
            max_date = datetime.strptime(max_date_str, "%Y-%m-%d")
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
                sale_datetime = datetime.strptime(sale["FSLH_TRANSACTION_DATE_FSLH"], "%Y-%m-%d %H:%M:%S")
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
            max_date = datetime.strptime(max_date_str, "%Y-%m-%d")
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
                sale_datetime = datetime.strptime(sale["FSLH_TRANSACTION_DATE_FSLH"], "%Y-%m-%d %H:%M:%S")
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