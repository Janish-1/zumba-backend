# urls.py
from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('register/',RegisterUserView.as_view(), name='user-register'),
    path('login/', UserLoginAPIView.as_view(), name='user-login'),
    path('otpverify/', otpverify.as_view(), name='otp-verify'),
    path('forget-password/', ForgetPasswordView.as_view(), name='forget_password'),
    path('new-password-set/', NewPasswordSetView.as_view(), name='new_password_set'),
    path('live_session_management/', LiveSessionManagement.as_view(), name='live_session_management'),
    path('blog-list/', BlogListView.as_view(), name='blog-list'),
    path('live-sessions/', LiveSessionView.as_view(), name='live-sessions'),
    path('lucky-draw', LuckyDrawView.as_view(), name='lucky-draw'),
    path('draw_dashboard-data/', DashboardDataView.as_view(), name='draw_dashboard_data'),
    path('edit-profile/<int:pk>/', EditProfileView.as_view(), name='edit-profile'),
    path('Blog-Catogory/<int:pk>/', Blogcatogory.as_view(), name='Blog-Catogory'),
    path('Catogory/', CatogoryView.as_view(), name='Blog-Catogory'),
    path('trackerview/<int:pk>/', Trackerview.as_view(), name='trackerview'),
    # path('calculate_calories/<int:pk>/', CalorieCalculationView.as_view(), name='calculate_calories'),
    path('attendence/', livesessionattendence.as_view(), name='calculate_calories'),
    path('luckydrawbtn/', luckydrawbtn.as_view(), name='calculate_calories'),
    # path('phonepe-payment/', PhonePePaymentView.as_view(), name='phonepe-payment'),
    path('users/<int:user_id>/', UserDetailView.as_view(), name='user-detail'),
   
    # path('subscribe/', SubscriptionPaymentView.as_view(), name='subscription_payment'),
    path('subscribe/', SubscriptionPaymentView.as_view(), name='subscription-payment'),
    path('paymentview/', paymentview.as_view(), name='paymentview'),
    # path('razorpay-callback/', RazorpayCallbackView.as_view(), name='razorpay-callback'),
    path('transactions/<int:user_id>/', TransactionPerPersonView.as_view(), name='transaction-detail'),
   
   
]
    

