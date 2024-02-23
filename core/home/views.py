
#registrations
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *
from datetime import datetime,date

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

                # Check if there is a referrer
                try:
                    referrer = CustomUser.objects.get(referral_code=referral_code)
                except CustomUser.DoesNotExist:
                    # Referrer not found
                    referrer = None

                if referrer:
                    # Update wallet balance for the referrer only
                    referral_bonus = 40  # Change to the desired bonus amount
                    referrer.wallet_balance += referral_bonus
                    referrer.save()

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
        
        
#----------edit profile 
class EditProfileView(APIView):
    def patch(self,request,pk):
        user=CustomUser.objects.get(pk=pk)
        serializers = UserRegistrationSerializer(user,data=request.data,partial=True)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


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

            # Send OTP to user's email
            send_mail(
                'OTP Verification',
                f'Your OTP for login is: {otp}',
                'FOR LOGIN',  # Replace with your email
                [user.email],
                fail_silently=False,
            )

            return Response({'message':'verification code send to your email', 'user_id':user.id},status=status.HTTP_200_OK)
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
        print(user_id, otp_entered)

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




class luckydrawbtn(APIView):
    def post(self, request):
        serializer = liveSessionparticipatebtn(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            main = UserAttendance.objects.get(user=user)
            print(main.counter)
            if main.counter >= 30:
                print("ookk")
                serializer.save()
            return Response({"msg":"Participation Success"}, status=status.HTTP_200_OK)
        return Response({"msg":"You Are Not Eligible For Lucky Draw your live session attendence is less than 30 days"}, status=status.HTTP_400_BAD_REQUEST)
    
    
    
#-------------------------------------------------------------------------

