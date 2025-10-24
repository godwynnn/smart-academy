from main.models import (Question,Questionnaire)
from rest_framework import serializers
from rest_framework import serializers
# from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from main.models import *
from django.conf import settings

User=MyUser
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=MyUser
        fields=['first_name','last_name','role','id','password','email','id','is_staff','is_superuser','is_active']

        extra_kwargs={'password':{'write_only':True},'is_staff':{'read_only':True},'is_superuser':{'read_only':True},'is_active':{'read_only':True}}

    def create(self,validated_data):
        print('validate data', validated_data)
        # username=str(validated_data['email']).split('@')[0]
        user = MyUser.objects.create(email=str(validated_data['email']).lower().strip(),
        username=str(validated_data['email']).lower(),
        first_name=str(validated_data['first_name']).lower().strip(),
        last_name=str(validated_data['last_name']).lower().strip(),
        is_active=True

        )
        user.set_password(validated_data['password'])
        
        user.save()

        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=Profile
        fields='__all__'


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Question
        fields='__all__'


class QuestionaireSerializer(serializers.ModelSerializer):
    class Meta:
        model=Questionnaire
        fields='__all__'