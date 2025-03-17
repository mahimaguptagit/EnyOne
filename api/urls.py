from django.urls import path
from . import views

urlpatterns = [
    path('user-login/',views.UserLoginView.as_view(),name='UserLogin'),
    path('user-profile-detail/',views.UserProfileView.as_view(),name='UserProfile'),
    path('user-email-verification/',views.UserEmailVerificationView.as_view(),name='UserEmailVerification'),
    path('verify-send-otp-user/',views.UserVerifyOtpView.as_view(),name='UserVerifyOtp'),
    path('reset-user-password/',views.ResetUserPasswordView.as_view(),name='ResetUserPassword'),
    path('user-add-raise-ticket/',views.UserRaiseTicketView.as_view(),name='UserRaiseTicket'),
    path('show-raised-ticket/',views.ShowRaisedTicketDataView.as_view(),name='ShowRaisedTicketData'),
    path('show-particular-ticket-data/',views.ShowParticularTicketDetailsView.as_view(),name='ShowParticularTicketDetails'),
    path('add-satisfaction-score/',views.AddSatisfactionScoreView.as_view(),name='AddSatisfactionScore'),
    path('feedback-details/',views.ShowTicketFeedbackView.as_view(),name='ShowTicketFeedback'),
    path('show-receiver-niotification/',views.ShowNotificationView.as_view(),name='ShowReceiverNotification'),
    path('show-number-notification/',views.NotificationNumberView.as_view(),name='NotificationNumber'),
    path('particular-notification-delete/',views.ParticularNotificationDeleteView.as_view(),name='ParticularNotificationDelete'),
    path('delete-all-notification/',views.ClearAllNotificationView.as_view(),name='ClearAllNotification'),
    path('send-chat-ticket/',views.ChatTicketCreateView.as_view(),name='ChatTicketCreate'),
    path('show-chat-ticket/',views.ShowTicketChatView.as_view(),name='ShowTicketChat'),
    path('particular-chat-delete/',views.ParticularTicketChatDeleteView.as_view(),name='ParticularTicketChatDelete'),
    path('clear-all-chat/',views.ClearAllTicketChatView.as_view(),name='ClearAllTicketChat'),
    # path('check-access-token/',views.CheckAccessTokenView.as_view(),name='CheckAccessToken'),
    # path('check-report-list/',views.CheckReportsListView.as_view(),name='CheckReportsList')
    # Sales Data

    path('salesgraph-by-staff/',views.SalesGraphDataByStaffView.as_view(),name='SalesGraphDataByStaff'),
    path('salesgraph-by-saleschannel/',views.SalesGraphDataBySalesChannelView.as_view(),name='SalesGraphDataBySalesChannel'),
    path('salesgraph-by-category/',views.SalesGraphDataByCategoryView.as_view(),name='SalesGraphDataByCategory'),
    path('salesgraph-perhour-weekly/',views.SalesPerHourWeeklyView.as_view(),name='SalesPerHourWeekly'),
    path('salesgraph-perhour-monthly/',views.SalesPerHourMonthlyView.as_view(),name='SalesPerHourMonthly'),
    path('salesgraph-perhour-yearly/',views.SalesPerHourYearlyView.as_view(),name='SalesPerHourYearly'),
    path('salesgraph-comparison-weekly/',views.SalesWeeklyComparisonGraphView.as_view(),name='SalesWeeklyComparisonGraph'),
    path('salesgraph-comparison-monthly/',views.SalesMonthlyComparisonGraphView.as_view(),name='SalesMonthlyComparisonGraph'),
    path('salesgraph-comparison-yearly/',views.SalesYearlyComparisonGraphView.as_view(),name='SalesYearlyComparisonGraph'),
    path('salesgraph-total-sales-data/',views.SalesGraphTotalSalesDataView.as_view(),name='SalesGraphTotalSalesData'),
    path('salesgraph-todaytotal-sales-data/',views.SalesGraphTodayTotalSalesDataView.as_view(),name='SalesGraphTodayTotalSalesData'),

    path('last_refresheddate_data/',views.LastRefreshedDateDataView.as_view(),name='LastRefreshedDateData'),

    path('productgraph-today-productsold/',views.ProductGraphTodayProductSoldView.as_view(),name='ProductGraphTodayProductSold'),
    path('productgraph-average-productspercustomers/',views.ProductGraphTodayAverageNumberProductperCustomerView.as_view(),name='ProductGraphTodayAverageNumberProductperCustomer'),
    path('productgraph-topproductquantity/',views.ProductGraphDataByTopProductsByQuantityView.as_view(),name='ProductGraphDataByTopProductsByQuantity'),
    path('productgraph-salesandbeforemargin/',views.ProductGraphDataBySalesandBeforeMarginView.as_view(),name='ProductGraphDataBySalesandBeforeMargin'),
    path('productgraph-grossmargindata/',views.ProductGraphDataByTodayGrossMarginView.as_view(),name='ProductGraphDataByTodayGrossMargin'),
    path('productgraph-foodanddrinkcost/',views.ProductGraphByFoodCostAndDrinkCostView.as_view(),name='ProductGraphByFoodCostAndDrinkCost'),

    path('customergraph-averagecaperclient/',views.CustomerGraphByAverageCAPerCustomerView.as_view(),name='CustomerGraphByAverageCAPerCustomer'),
    path('today-number-customers/',views.CustomerGraphByNumberOfCustomerTodayView.as_view(),name='CustomerGraphByNumberOfCustomerToday'),
    path('customergraph-perhour-weekly/',views.CustomerGraphNumberOfCustomerPerHourWeeklyView.as_view(),name='CustomerGraphNumberOfCustomerPerHourWeekly'),
    path('customergraph-perhour-monthly/',views.CustomerGraphNumberOfCustomerPerHourMonthlyView.as_view(),name='CustomerGraphNumberOfCustomerPerHourMonthly'),
    path('customergraph-perhour-yearly/',views.CustomerGraphNumberOfCustomerPerHourYearlyView.as_view(),name='CustomerGraphNumberOfCustomerPerHourYearly'),
    path('customergraph-saleschannel/',views.CustomerGraphBySalesChannelView.as_view(),name='CustomerGraphBySalesChannel'),
    path('customergraph-comparisonweekly/',views.CustomerGraphForNumberOfCustomerPerWeekView.as_view(),name='CustomerGraphForNumberOfCustomerPerWeek'),
    path('customergraph-comparisonmonthly/',views.CustomerGraphForNumberOfCustomerPerMonthView.as_view(),name='CustomerGraphForNumberOfCustomerPerMonth'),
    path('customergraph-comparisonyearly/',views.CustomerGraphForNumberOfCustomerPerYearView.as_view(),name='CustomerGraphForNumberOfCustomerPerYear'),

    path('show-company-logo/',views.ShowCompanyLogoView.as_view(),name='ShowCompanyLogo'),
    path('show-allticket-feedbackdata/',views.ShowAllRaisedTicketFeedbackView.as_view(),name='ShowAllRaisedTicketFeedback')
]
