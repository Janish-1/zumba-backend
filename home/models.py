# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone




class Plan(models.Model):
    plantype = models.CharField(max_length=50)
    planvalidity = models.IntegerField() 
    price = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=False)
    
    def __str__(self):
        return self.plantype
    
class CustomUser(AbstractUser):
    
    email = models.EmailField(unique=True)
    mobile_no = models.CharField(max_length=15,null=True, blank=True)
    address = models.TextField( null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    user_plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True)
    otp = models.CharField(max_length=6, null=True, blank=True) 
    wallet_balance = models.PositiveIntegerField(default=0)
    aadharNo = models.CharField(max_length=12, null=True, blank=True)
    photo = models.FileField(upload_to='user')
    name = models.CharField(max_length=100,null=True,blank=True)
    fathername = models.CharField(max_length=100,null=True,blank=True)
    
    def __str__(self):
        return self.username


#------------------------------------models.py------------------------------------



class Category(models.Model):
    category_name = models.CharField(max_length=50)
    category_image = models.ImageField(upload_to='category_images/')

    def __str__(self):
        return self.category_name

class Blog(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='blogs')
    title = models.CharField(max_length=255)
    description = models.TextField()
    blog_photo = models.ImageField(upload_to='blog_photos/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='blogs')
    date_added = models.DateTimeField()
    video_link = models.CharField(max_length=255)
    time_duration = models.CharField(max_length=10)
    calories_burn = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        self.date_added = timezone.localtime(timezone.now())
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    
class tracker(models.Model):
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    blog_id= models.ForeignKey(Blog, on_delete=models.CASCADE)
    total_time=models.CharField(max_length=20)
    total_calories = models.CharField(max_length=20)
    watching_time = models.CharField(max_length=20,null=True,blank=True)
    calories_burn = models.CharField(max_length=255,null=True,blank=True)
    datetime = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return self.user.user_id




class LuckyDraw(models.Model):
    name = models.CharField(max_length=255)
    poster = models.ImageField(upload_to='lucky_draw_posters/')
    lucky_draw_startdate = models.DateField()
    lucky_draw_enddate = models.DateField()
    date_results = models.DateField()
    first_price = models.CharField(max_length=255)
    second_price = models.CharField(max_length=255)
    third_price = models.CharField(max_length=255)
    winner_candidates1 = models.CharField(max_length=255,default='?')
    winner_candidates2 = models.CharField(max_length=255,default='?')
    winner_candidates3 = models.CharField(max_length=255,default='?')

    def __str__(self):
        return self.name


class LiveSession(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField()
    poster = models.ImageField(upload_to='live_session_posters/')
    youtube_live_link = models.URLField()
    live_session_starttime = models.TimeField(null=True, blank=True)
    live_session_endtime = models.TimeField(null=True, blank=True)
    def __str__(self):
        start_time = self.live_session_starttime.strftime('%H:%M') if self.live_session_starttime else 'N/A'
        end_time = self.live_session_endtime.strftime('%H:%M') if self.live_session_endtime else 'N/A'
        return f"{self.name} (Start: {start_time}, End: {end_time})"
    
     



class UserAttendance(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    live_session = models.ForeignKey('LiveSession', on_delete=models.CASCADE)
    attendance_date = models.DateField(auto_now_add=True)
    last_viewed_date = models.DateField(null=True) 
    counter=models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.live_session.name}"



class luckyparticipate(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    luckydraw_name = models.ForeignKey(LuckyDraw, on_delete=models.CASCADE)
    participation_date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.luckydraw_name.name} - {self.user.username}"
    
    
    
    
#----------------------------------------------------payment




# class Payment(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     amount = models.PositiveIntegerField()
#     timestamp = models.DateTimeField(auto_now_add=True)
#     transaction_id = models.CharField(max_length=100,unique=True)
#     def __str__(self):
#         return f"{self.user.username}'s Payment - {self.id}"



from datetime import datetime, timedelta
class Payment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, default='Initiated')  # Status can be 'Initiated', 'Success', 'Failed'
    razorpay_order_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=100, null=True, blank=True)
    order_id = models.CharField(max_length=100, null=True, blank=True) 
    subscription_plan = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Payment - {self.id}"
 
 
    # def update_subscription_plan(self):
    #     if self.status == 'success':
    #         self.subscription_plan = 'active'
    #     elif self.timestamp + timedelta(days=30) < datetime.now():
    #         self.subscription_plan = 'expire'
    #     self.save()
    
    
    
    
    
    def update_subscription_plan(self):
        if self is not None:
            if self.status == 'success':
                self.subscription_plan = 'active'
            elif self.timestamp + timedelta(days=30) < datetime.now():
                self.subscription_plan = 'expire'
            self.save()
        else:
            print("No payment found for the user.")