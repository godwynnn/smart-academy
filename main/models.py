from django.db import models
import datetime
# from student.models import Student
from django.utils import timezone
import random
# from userauth.views import generateidentifier
import string
import json
import hashlib
from django.contrib.auth.models import User,AbstractUser


def generate_otp(length):
    """Generates a 6-digit numeric OTP"""
    return ''.join(random.choices(string.digits, k=length))

def hash_otp(otp):
    """Hashes the OTP using SHA256"""
    return hashlib.sha256(otp.encode()).hexdigest()

def generateinviteID(length) ->str:
    val=''
    while len(val)<=length:
        val+=str(random.randint(0,9))
    return val


class MyUser(AbstractUser):
    ROLE=(
        ('student','student'),
        ('teacher','teacher')
    )
    
    role=models.CharField(max_length=100,choices=ROLE,null=True,blank=True)
    email=models.CharField(max_length=100,null=True,blank=True,unique=True)
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username','password','first_name','last_name']





class Profile(models.Model):
    ROLE=(
        ('student','student'),
        ('teacher','teacher')
    )
    user=models.OneToOneField(MyUser,null=True,blank=True,on_delete=models.CASCADE,unique=True)
    device = models.CharField(max_length=200, null=True, blank=True)
    security_token=models.CharField(max_length=1000, null=True, blank=True)
    phone_no=models.PositiveIntegerField(null=True,blank=True)
    students=models.ManyToManyField(MyUser,blank=True,related_name='students')
    tutors=models.ManyToManyField(MyUser,blank=True,related_name='tutors')
    image=models.ImageField(null=True,blank=True,upload_to='image/users_img',default='')
    activation_token=models.CharField(max_length=200,null=True, blank=True)
    date_joined=models.DateTimeField(auto_now=True)


    def __str__(self):
        return f'{self.user}'
    # def save(self,*args,**kwargs):
    #     pass

    class Meta:
        ordering= ['-date_joined']

class Course(models.Model):
   
   course_name = models.CharField(max_length=50)
   question_number = models.PositiveIntegerField()
   total_marks = models.PositiveIntegerField()
   hr_duration=models.IntegerField(null=True,blank=True,default=0)
   min_duration=models.IntegerField(null=True,blank=True,default=0)
   ref_id=models.CharField(max_length=500,null=True,blank=True)
   

   def __str__(self):
        return self.course_name
   def save(self,*args,**Kwargs):
        if self.hr_duration is None:
           self.hr_duration=0
        if self.min_duration is None:
           self.min_duration=0

        super().save(*args,**Kwargs)

# class Timer(models.Model):
#     student = models.ForeignKey(Student,on_delete=models.CASCADE,null=True,blank=True)
#     course=models.ForeignKey(Course,on_delete=models.CASCADE)
#     end_time_date=models.DateTimeField(null=True,blank=True)

#     def save(self,*args,**Kwargs):
#         if self.end_time_date is None:
#             self.end_time_date=datetime.datetime.now()+datetime.timedelta(minutes=self.course.min_duration,hours=self.course.hr_duration)
        

#         super().save(*args,**Kwargs)

class Question(models.Model):
    TYPE=(
            ('question','question'),
             ('lesson','lesson')
             )
   
    question=models.CharField(max_length=600)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE,
                             null=True,blank=True,
                               related_name="user_questions")
    quiz_title=models.TextField(max_length=50000,null=True,blank=True)
    answer=models.TextField(max_length=50000,null=True,blank=True)
    quiz_answer=models.TextField(max_length=5000,null=True,blank=True)
    raw_answer=models.JSONField(max_length=50000,null=True,blank=True)

    
    category=models.CharField(null=True,blank=True,max_length=200,choices=TYPE)

    def __str__(self):
        return f'{self.question} '


class Questionnaire(models.Model):
    TYPE=(
            ('question','question'),
             ('lesson','lesson')
             )
    id_tag=models.CharField(max_length=200,null=True,blank=True)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE,null=True,blank=True, related_name="user_questionaires")
    questions=models.ManyToManyField(Question, related_name='questionaires')
    entry_type=models.CharField(null=True,blank=True,max_length=200,choices=TYPE)
    date_created=models.DateTimeField(null=True,blank=True,auto_now_add=True)




class  OTP(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="otps")
    otp_hash = models.CharField(max_length=64, unique=True)  # Store hashed OTP
    # expiry_duration=models.IntegerField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True,null=True)

    class Meta:
        ordering=['-created_at']