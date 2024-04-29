from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *
from .utility import generate_unique_referral_code
CustomUser = get_user_model()

# class UserRegistrationSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)

#     class Meta:
#         model = CustomUser
#         # fields = ['id', 'email', 'username', 'mobile_no', 'address', 'city', 'dob', 'gender', 'password']
#         fields = '__all__' 

#     def create(self, validated_data):
#         password = validated_data.pop('password', None)
#         user = CustomUser(**validated_data)
#         if password:
#             user.set_password(password)
#         user.save()

#         return user



class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser  # Using Django's dynamic user model reference
        fields = '__all__'
        
        
    def create(self, validated_data):
        """
        Create and return a new user, without setting a password.
        """
        user = CustomUser(**validated_data)
        user.save()
        return user

#----------------manage live session 

class LiveSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveSession
        fields = '__all__'

#----------blog data 

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class TrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = tracker
        fields = ['user_id']

class track_view(serializers.ModelSerializer):
    class Meta:
        models = tracker
        fields = '__all__'


class track_view_all(serializers.ModelSerializer):
    class Meta:
        models = tracker
        fields = ['user_id','watching_time',]


class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = '__all__'

#------------------live session view

class LiveSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveSession
        fields = '__all__'
        
        
#------------------lucky draw
class LuckyDrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = LuckyDraw
        fields = '__all__'
        
        


class WinnerCandidatesSerializer(serializers.Serializer):
    winner_candidates1 = serializers.CharField()
    winner_candidates2 = serializers.CharField()
    winner_candidates3 = serializers.CharField()

#------------forget password logic --------------------

class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    


class NewPasswordSetSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)



class liveSessionparticipate(serializers.ModelSerializer):
    class Meta:
        model = UserAttendance
        fields = ['user','live_session']
class liveSessionparticipatebtn(serializers.ModelSerializer):
    class Meta:
        model = luckyparticipate
        fields = ['user','luckydraw_name']
   
        

class ReferralCodeSerializer(serializers.Serializer):
    referral_code = serializers.CharField(max_length=20)
    
    
    
    
class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'
        
        
        

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'