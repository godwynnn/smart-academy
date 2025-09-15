from django.shortcuts import render
from django.conf import settings
# Create your views here.
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from main.models import *
from django.core.exceptions import ObjectDoesNotExist
from main.serializers import *
User=MyUser



class TutorsClassView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self, request):
        teacher_mail=request.GET.get('q',None)
        
        tutors=[x for x in Profile.objects.filter(user__role='teacher')  if request.user in x.students.all()]
        
        # if teacher_mail not in [None,'']:
        #     data=filter(lambda x: x.user.email == teacher_mail,list(tutors))
        #     return Response({
        #         'data':UserProfileSerializer(data,many=True).data
        #     },status=status.HTTP_200_OK)
        serializer=UserProfileSerializer(tutors,many=True).data
        for serialized_data in serializer:
            serialized_data['user']=UserSerializer(User.objects.get(id=serialized_data['user']),many=False).data

        return Response({
            'data':serializer
        },status=status.HTTP_200_OK)

    def post(self,request):
        teacher_mail=str(request.data.get('mail')).strip().lower()
        action=str(request.data.get('action')).upper()
        user=request.user

        try:
            teacher=Profile.objects.get(user__email=teacher_mail,user__role='teacher')

            if action == 'JOIN':
                if user in teacher.students.all():
                    return Response({
                    'message':'You\'re already added to this class',
                        
                    },status=status.HTTP_302_FOUND)
                else:
                    teacher.students.add(user)
                    teacher.save()
                    return Response({
                        'data':UserSerializer(user).data,'message':"successfully Joined the class"},
                        status=status.HTTP_200_OK)
                
                
            elif action == 'EXIT':
                if user in teacher.students.all():
                    teacher.students.remove(user)
                    teacher.save()
                    return Response({
                        'data':UserSerializer(user).data,
                        'message':"student successfully removed"
                    },status=status.HTTP_200_OK)
                else:
                    return Response({
                    'message':'not a member of this class',
                        
                    },status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({
                    'message':'invalid action'
                },status=status.HTTP_406_NOT_ACCEPTABLE)

        except ObjectDoesNotExist:
            return Response({
                'message':'teacher don\'t exist'

            },status=status.HTTP_404_NOT_FOUND)

