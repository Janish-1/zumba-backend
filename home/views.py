
#registrations
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *
from datetime import datetime,date

# Importing the SMTP Libraries
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from django.core.mail import EmailMessage


# class RegisterUserView(APIView):
#     def post(self, request, *args, **kwargs):
#         serializer = UserRegistrationSerializer(data=request.data)
#         if serializer.is_valid():
#             referral_code = request.data.get('referral_code')

#             # Continue with user registration
#             user = serializer.save()

#             # Check if there is a referrer
#             try:
#                 referrer = CustomUser.objects.get(referral_code=referral_code)
#             except CustomUser.DoesNotExist:
#                 # Referrer not found
#                 referrer = None

#             if referrer:
#                 # Update wallet balance for the referrer only
#                 referral_bonus = 40  
#                 referrer.wallet_balance += referral_bonus
#                 referrer.save()

#                 return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)

#             return Response({'error': 'Invalid referral code'}, status=status.HTTP_400_BAD_REQUEST)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#------------------------------------------------------------------------------------

class RegisterUserView(APIView):
    def is_duplicate_value(self, field_name, value):
        return CustomUser.objects.filter(**{field_name: value}).exists()

    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        password1 = request.data.get('confirmPassword')
        username = request.data.get('username')
        email = request.data.get('email')
        referral_code = request.data.get('referral_code')

        # Check for duplicate username and email
        if self.is_duplicate_value('username', username):
            return Response({"msg": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
        elif self.is_duplicate_value('email', email):
            return Response({"msg": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            password = serializer.validated_data['password']
            if password == password1:
                serializer.save()
                try:
                    referrer = CustomUser.objects.get(referral_code=referral_code)
                except CustomUser.DoesNotExist:
                    referrer = None
                if referrer:
                    print(referrer.wallet_balance)
                    # Update wallet balance for the referrer only
                    referral_bonus = 50  # Change to the desired bonus amount
                    referrer.wallet_balance += referral_bonus
                    referrer.save()
                    print(referrer.wallet_balance)

                return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)

            return Response({"message": "Password fields do not match"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class UserRegistrationView(APIView):
#     def is_duplicate_value(self,field_name,value):
#         return CustomUser.objects.filter(**{field_name:value}).exists()
    
#     def post(self, request, *args, **kwargs):
#         serializer = UserRegistrationSerializer(data=request.data)
#         password1 = request.data.get('confirmPassword')
#         username=request.data.get('username')
#         email = request.data.get('email')
#         if self.is_duplicate_value('username', username):
            
#             return Response({"msg": "username already exists"}, status=status.HTTP_400_BAD_REQUEST)
#         elif self.is_duplicate_value('email', email):
            
#             return Response({"msg": "email already exists"}, status=status.HTTP_400_BAD_REQUEST)
#         if serializer.is_valid():
#             password = serializer.validated_data['password']
#             if password == password1:
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             return Response({"message":"password fields do not match"}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class UserDetailView(APIView):
    def get(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            serializer = UserRegistrationSerializer(user)
            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
# #----------edit profile 
# class EditProfileView(APIView):
#     def patch(self,request,pk):
#         user=CustomUser.objects.get(pk=pk)
#         serializers = UserRegistrationSerializer(user,data=request.data,partial=True)
#         if serializers.is_valid():
#             serializers.save()
#             return Response(serializers.data)
#         return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

class EditProfileView(APIView):
    def patch(self, request, pk):
        user = CustomUser.objects.get(pk=pk)
        serializer = UserRegistrationSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            # Check if the error is related to the 'dob' field
            if 'dob' in serializer.errors:
                error_msg = {"dob": "Invalid date of birth format. Please use YYYY-MM-DD."}
                return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#--------logins

from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from .models import CustomUser

class UserLoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        # Validate email and password
        if email is None or password is None:
            return JsonResponse({'error': 'Both email and password are required'}, status=400)

        # Retrieve user by email
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'User does not exist'}, status=404)

        # Authenticate user using the default authentication backend
        authenticated_user = authenticate(request, username=user.username, password=password)

        if authenticated_user is not None:
            # Generate and send OTP
            otp = get_random_string(length=6, allowed_chars='0123456789')
            user.otp = otp
            user.save()

            # # Send OTP to user's email
            # send_mail(
            #     'OTP Verification',
            #     f'Your OTP for login is: {otp}',
            #     'FOR LOGIN',  # Replace with your email
            #     [user.email],
            #     fail_silently=False,
            # )
            
            # Email sending logic
            subject = "YOUR OTP"
            message = f"Your OTP is: {otp}\nUse this OTP to Login."
        
            sender = 'noreply@ramo.co.in'
            recipient = email
            
            try:
                # Using Django's EmailMessage
                email = EmailMessage(subject, message, sender, [recipient])
                email.send()
        
            except Exception as e:
                # Handle email sending failure
                return Response({'success': False, 'message': 'Error sending email', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
            # tab=Payment.objects.filter(user=user.id).last()
            # return Response({'message':'verification code send to your email', 'user_id':user.id,'status':tab.subscription_plan},status=status.HTTP_200_OK)
            tab = Payment.objects.filter(user=user.id).last()

            status_value = tab.subscription_plan if tab and hasattr(tab, 'subscription_plan') else 'inactive'
            return Response({'message': 'verification code sent to your email', 'user_id': user.id, 'status': status_value}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)


#--------otp verified

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404


class otpverify(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('id')
        otp_entered = request.data.get('otp')
        

        # Validate user_id and otp are provided
        if not user_id or not otp_entered:
            return Response({'error': 'User ID and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get the user by user_id
            user = CustomUser.objects.get(id=user_id)

            # Validate if the user has an OTP set
            if not user.otp:
                return Response({'error': 'OTP not generated for this user'}, status=status.HTTP_400_BAD_REQUEST)

            # Validate the entered OTP
            if otp_entered != user.otp:
                return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

            # If OTP is valid, remove the OTP from the user model
            user.otp = None
            user.save()

            return Response({'message': 'OTP verified successfully'}, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class Trackerview(APIView):
    def post(self, request,pk):
        blog = Blog.objects.get(pk=pk)
        serializer = TrackerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(blog_id=blog,total_calories=blog.calories_burn,total_time=blog.time_duration)
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request,pk):
        blog = Blog.objects.get(pk=pk)
        serializer = TrackerSerializer(blog,request.data,partial = True)
        tt = request.data.get('watching_time')
        if serializer.is_valid():
            def fn(a):
                time_delta = datetime.strptime(a, "%H:%M:%S") - datetime(1900, 1, 1)
                seconds = time_delta.total_seconds()
                return int(seconds)
            def calculate_calories_burn_rate(total_calories, total_time):
                total_time_seconds = float(total_time)     
                calories_burn_rate = total_calories / total_time_seconds
                return calories_burn_rate
            l1 = calculate_calories_burn_rate(int(blog.calories_burn),int(fn(blog.time_duration)))
            mt = fn(tt)
            serializer.save(watching_time=tt,calories_burn=mt*l1)            
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



#-------------------live session-----------------------


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import LiveSession
from .serializers import LiveSessionSerializer
from django.utils import timezone


class LiveSessionManagement(APIView):
    def get(self, request, *args, **kwargs):
        current_date = timezone.now().date()

        
        upcoming_sessions = LiveSession.objects.filter(date__gt=current_date)
        upcoming_sessions_serialized = LiveSessionSerializer(upcoming_sessions, many=True).data
        
        # Filter previous sessions (sessions with a date less than today)
        previous_sessions = LiveSession.objects.filter(date__lt=current_date)
        previous_sessions_serialized = LiveSessionSerializer(previous_sessions, many=True).data

        # Filter live sessions (sessions with a date equal to today)
        live_sessions = LiveSession.objects.filter(date=current_date)
        live_sessions_serialized = LiveSessionSerializer(live_sessions, many=True).data

        response_data = {
            'upcoming_sessions': upcoming_sessions_serialized,
            'previous_sessions': previous_sessions_serialized,
            'live_sessions': live_sessions_serialized,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    
    #-------------blog api -----------------

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination


class BlogListView(APIView):
    def get(self, request, *args, **kwargs):
        # Retrieve all blog posts
        blogs = Blog.objects.all()

        # Paginate the queryset manually
        page = self.request.GET.get('page', 1)
        paginator = PageNumberPagination()
        paginator.page_size = 10  # Set the desired number of items per page
        paginated_blogs = paginator.paginate_queryset(blogs, request)

        serialized_blogs = BlogSerializer(paginated_blogs, many=True).data

        return paginator.get_paginated_response(serialized_blogs)
    
class Blogcatogory(APIView):
    def get(self, request,pk):
        cat = Category.objects.get(pk=pk)
        blogs = Blog.objects.filter(category_id=cat.id)
        serializers = BlogSerializer(blogs, many=True)        
        return Response({"msg":serializers.data}, status=status.HTTP_200_OK)
    
class CatogoryView(APIView):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        serialized_categories = CategorySerializer(categories, many=True)
        return Response(serialized_categories.data, status=status.HTTP_200_OK)

#---------------------------live sesssion view



class LiveSessionView(APIView):
    def get(self, request, *args, **kwargs):
        live_sessions = LiveSession.objects.all()
        serialized_live_sessions = LiveSessionSerializer(live_sessions, many=True).data
        return Response(serialized_live_sessions, status=status.HTTP_200_OK)
    
   
#---------------------------lucky draw view
   
class LuckyDrawView(APIView):
    def get(self, request, *args, **kwargs):
        lucky_draws = LuckyDraw.objects.all()
        serialized_lucky_draws = LuckyDrawSerializer(lucky_draws, many=True).data
        return Response(serialized_lucky_draws, status=status.HTTP_200_OK)
   
   
   #---------------------------draw_dashboard view
from datetime import datetime   
class DashboardDataView(APIView):
    def get(self, request, *args, **kwargs):
        # Filter upcoming draws
        upcoming_draws = LuckyDraw.objects.filter(date_results__gt=datetime.now().date())
        serialized_upcoming_draws = LuckyDrawSerializer(upcoming_draws, many=True).data

        # Filter previous draws
        previous_draws = LuckyDraw.objects.filter(date_results__lt=datetime.now().date())
        serialized_previous_draws = LuckyDrawSerializer(previous_draws, many=True).data

        # Retrieve the latest draw with results
        latest_draw = LuckyDraw.objects.filter(date_results__lte=datetime.now().date()).exclude(
            winner_candidates1='?', winner_candidates2='?', winner_candidates3='?'
        ).order_by('-date_results').first()

        if latest_draw:
            # If there is a latest draw, retrieve winner candidates
            winner_candidates_data = {
                'winner_candidates1': latest_draw.winner_candidates1,
                'winner_candidates2': latest_draw.winner_candidates2,
                'winner_candidates3': latest_draw.winner_candidates3,
            }
        else:
            # If there is no latest draw, set default values for winner candidates
            winner_candidates_data = {
                'winner_candidates1': '?',
                'winner_candidates2': '?',
                'winner_candidates3': '?',
            }

        winner_candidates_serializer = WinnerCandidatesSerializer(data=winner_candidates_data)
        winner_candidates_serializer.is_valid(raise_exception=True)

        response_data = {
            'upcoming_draws': serialized_upcoming_draws,
            'previous_draws': serialized_previous_draws,
            'latest_winner_list': winner_candidates_serializer.data,
            'latest_draw_name': latest_draw.name if latest_draw else None,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    
    
    #---------------------------forget password

import random
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser
from .serializers import ForgetPasswordSerializer

class ForgetPasswordView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ForgetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Generate OTP
        otp = str(random.randint(100000, 999999))
        # Save OTP to the user model
        user.otp = otp
        user.save()

        # Send OTP to the user's email
        subject = 'Forgot Password OTP'
        message = f'Your OTP for resetting the password is: {otp}'
        from_email = 'update password'  # Replace with your email
        recipient_list = [email]

        send_mail(subject, message, from_email, recipient_list)
        return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)


#---------------------------new password set

from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser
from .serializers import NewPasswordSetSerializer
import logging

class NewPasswordSetView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = NewPasswordSetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']
        try:
            user = CustomUser.objects.get(otp=otp)
        except CustomUser.DoesNotExist:
            return Response({'error': 'invalid OTP'}, status=status.HTTP_404_NOT_FOUND)
        # Update user password
        user.set_password(new_password)  # Use set_password instead of make_password
        user.otp = None  # Clear the OTP after the password is set
        user.save()
        return Response({'message': 'Password set successfully'}, status=status.HTTP_200_OK)






class livesessionattendence(APIView):
    def post(self, request):
        serializer = liveSessionparticipate(data=request.data)
        user = request.data.get('user')
        if serializer.is_valid():
            ls = serializer.validated_data['live_session']
            try:
                tab = UserAttendance.objects.get(user=user)
            except:
                tab = None
                print(tab)
            if tab == None:
                print("hhhhhhhh")
                serializer.save(counter=1,last_viewed_date=date.today())    
                return Response(serializer.data, status=status.HTTP_200_OK)               
            else:
                print("asdasdasdasd")
                new = UserAttendance.objects.get(id=tab.id)
                print(new)
                if new.last_viewed_date != date.today():
                    new.counter += 1
                    print("fasdfagsfygasudyfgausydfgasdfgaysf")
                    new.last_viewed_date = date.today()
                    new.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    print("11111111111111")
                    return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class luckydrawbtn(APIView):
#     def post(self, request):
#         user_id = request.data.get('user')
#         lucky_id = request.data.get('luckydraw')
#         print(user_id,lucky_id)
#         try:
#             user = CustomUser.objects.get(id=user_id)
#             tab = UserAttendance.objects.get(user=user)
#         except:
#             return Response({"msg":"this user does not exist"}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             lucky = LuckyDraw.objects.get(id=lucky_id) 
#         except:
#             return Response({"msg":"this lucky draw does not exist"}, status=status.HTTP_400_BAD_REQUEST) 
#         try:
#             check = luckyparticipate.objects.filter(user=user,luckydraw_name=lucky)
#         except:
#             pass
#             # check = None
#         print(check)
#         if not check: 
#             print("fhjdfsdfadsfadsf") 
#             print(check)
#             if tab.counter >= 30:
#                 print("ookk")
#                 main = luckyparticipate.objects.create(user=user,luckydraw_name=lucky)
#                 main.save()
#                 return Response({"msg":"Participation Success"}, status=status.HTTP_200_OK)
#         else: 
#             return Response({"msg":"You already participated for this lucky draw"}, status=status.HTTP_400_BAD_REQUEST)
#         return Response({"msg":"You Are Not Eligible For Lucky Draw your live session attendence is less than 30 days"}, status=status.HTTP_400_BAD_REQUEST)


class luckydrawbtn(APIView):
    def post(self, request):
        user_id = request.data.get('user')
        lucky_id = request.data.get('luckydraw')
        print(user_id, lucky_id)
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"msg": "This user does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            tab = UserAttendance.objects.get(user=user)
        except UserAttendance.DoesNotExist:
            return Response({"msg": "You need to attend live session to participate in this lucky draw."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            lucky = LuckyDraw.objects.get(id=lucky_id)
        except LuckyDraw.DoesNotExist:
            return Response({"msg": "This lucky draw does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        existing_participations = luckyparticipate.objects.filter(user=user, luckydraw_name=lucky)

        if existing_participations.exists():
            return Response({"msg": "You already participated in this lucky draw"}, status=status.HTTP_400_BAD_REQUEST)
        if tab.counter >= 30:
            new_participation = luckyparticipate.objects.create(user=user, luckydraw_name=lucky)
            new_participation.save()
            return Response({"msg": "Participation Success"}, status=status.HTTP_200_OK)
        else:
            return Response({"msg": "You Are Not Eligible For Lucky Draw, your live session attendance is less than 30 days"},
                            status=status.HTTP_400_BAD_REQUEST)

    
#-------------------------------------------------------------------------payment gateway methods


from decimal import Decimal
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from .models import Payment
from datetime import datetime
from rest_framework import status
from rest_framework.views import APIView
from home.models import CustomUser 
import razorpay

class SubscriptionPaymentView(APIView):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')  
        user = self.get_user_by_id(user_id)
        if not user:
            return JsonResponse({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        subscription_amount_paisa = 10000 
        subscription_amount_inr = Decimal(subscription_amount_paisa) / 100  
        if user.wallet_balance > 0:
            redeemed_amount = min(user.wallet_balance, subscription_amount_inr)
            if redeemed_amount > 50:
                redeemed_amount = 50

            remaining_amount_for_payment = subscription_amount_inr - redeemed_amount

            user.wallet_balance -= redeemed_amount
            user.save()
        else:
            remaining_amount_for_payment = subscription_amount_inr
            redeemed_amount = 0
        unique_transaction_id = str(uuid.uuid4())[:-2]

        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
            order_params = {
                'amount': int(remaining_amount_for_payment * 100),
                'currency': 'INR',
                'payment_capture': 1,
                'notes': {
                    'transaction_id': unique_transaction_id,
                }
            }
            order = client.order.create(data=order_params)
            order_id = order['id']
            payment = Payment.objects.create(
            user=user,
            amount=remaining_amount_for_payment,
            status='Initiated',
            timestamp=datetime.now(),
            transaction_id=unique_transaction_id,
            razorpay_order_id=order_id,
            order_id=order_id  
            )
            return JsonResponse({'order_id': order_id,'amount': remaining_amount_for_payment}, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'error': f'Failed to initiate payment. {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def get_user_by_id(self, user_id):
        try:
            return CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return None


   
# class paymentview(APIView):
#     def post(self, request):
#         try:
#             razorpay_payment_id = request.data.get('razorpay_payment_id')
#             razorpay_signature = request.data.get('razorpay_signature')
#             razorpay_order_id = request.data.get('razorpay_order_id')
#             payment = Payment.objects.get(
#                 razorpay_order_id=razorpay_order_id
#             )
#             payment.status = 'success'
#             payment.razorpay_payment_id = razorpay_payment_id
#             payment.razorpay_signature = razorpay_signature
#             payment.save()
            
#             return JsonResponse({
#                 'message': 'Payment successful',
#                 'order_id': razorpay_order_id,
#                 'payment_id': payment.id, 
#                 'razorpay_payment_id': razorpay_payment_id,
#                 'razorpay_signature': razorpay_signature
#             })
#         except Payment.DoesNotExist:
#             return JsonResponse({'error': 'Payment not found'}, status=404)
#         except Payment.MultipleObjectsReturned:
#             return JsonResponse({'error': 'Multiple payments found for the same razorpay_order_id'}, status=400)





# views.py

from decimal import Decimal
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from .models import Payment
from datetime import datetime
from rest_framework import status
from rest_framework.views import APIView
from home.models import CustomUser 
import razorpay

class paymentview(APIView):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            razorpay_payment_id = request.data.get('razorpay_payment_id')
            razorpay_signature = request.data.get('razorpay_signature')
            razorpay_order_id = request.data.get('razorpay_order_id')
            
            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
            
            user = payment.user
            
            payment.status = 'success'
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.save()
            
            # Call the update_subscription_plan method
            payment.update_subscription_plan()
            
            return JsonResponse({
                'message': 'Payment successful',
                'order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature,
                'subscription_plan': payment.subscription_plan,  
            })
        except Payment.DoesNotExist:
            return JsonResponse({'error': 'Payment not found'}, status=404)
        except Payment.MultipleObjectsReturned:
            return JsonResponse({'error': 'Multiple payments found for the same razorpay_order_id'}, status=400)




class TransactionPerPersonView(APIView):
    def get(self, request, user_id):
        try:
            transactions = Payment.objects.filter(user__id=user_id)
            serializer = PaymentSerializer(transactions, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   