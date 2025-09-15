from django.shortcuts import render
from django.conf import settings
# Create your views here.
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from main.models import *
from django.core.exceptions import ObjectDoesNotExist
from main.serializers import *

import os
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
import requests
from django.conf import settings

User=MyUser
from datetime import datetime

def convert_24_to_12_hour(time_24hr_str):
    """
    Converts a 24-hour time string (e.g., "14:30") to a 12-hour format (e.g., "02:30 PM").

    Args:
        time_24hr_str (str): The time in 24-hour format (e.g., "HH:MM").

    Returns:
        str: The time in 12-hour format with AM/PM indicator.
    """
    try:
        # Parse the 24-hour time string into a datetime object
        time_obj = datetime.strptime(time_24hr_str, "%H:%M")

        # Format the datetime object into a 12-hour string with AM/PM
        time_12hr_str = time_obj.strftime("%I:%M")
        return time_12hr_str
    except ValueError:
        return "Invalid time format. Please use HH:MM."
 

class StudentsView(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    def get(self,request):
        student_mail=request.GET.get('q',None)
        
        try:
            user=Profile.objects.get(user=request.user.id,user__role='teacher')
            
            if student_mail not in [None,'']:
                
                for student in user.students.all():
                    if str(student_mail).strip() == student.email:
                        return Response({
                            'data':UserSerializer(student,many=False).data
                        }, status=status.HTTP_200_OK)
                    else:
                        return Response({
                            'message':'mail not assigned to any of your student'
                        },status=status.HTTP_404_NOT_FOUND)
            else:

                return Response({
                            'data':UserSerializer(user.students,many=True).data
                        }, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({
                'message':'teacher don\'t exist'

            },status=status.HTTP_404_NOT_FOUND)

   
        

    def post(self,request):
        mail=str(request.data.get('mail')).strip().lower()
        action=str(request.data.get('action')).upper()
        teacher=Profile.objects.get(user=request.user.id,user__role='teacher')
        try:
            
            student=Profile.objects.get(user__email=mail,user__role='student')
             
            # students_mail=[student.email for student in teacher.students.all()]

            if action=='ADD':
                if student.user in teacher.students.all():
                    return Response({
                    'message':'student already added',
                        
                    },status=status.HTTP_302_FOUND)
                else:
                    teacher.students.add(student.user)
                    teacher.save()
                    return Response({
                        'data':UserProfileSerializer(student).data,
                        'message':"student successfully added"
                    },status=status.HTTP_200_OK)



            elif action == 'DELETE':
                if student.user in teacher.students.all():
                    teacher.students.remove(student.user)
                    teacher.save()
                    return Response({
                        'data':UserProfileSerializer(student).data,
                        'message':"student successfully removed"
                    },status=status.HTTP_200_OK)
                else:
                    return Response({
                    'message':'student not found',
                        
                    },status=status.HTTP_404_NOT_FOUND)


            else:
                return Response({
                    'message':'invalid action'
                },status=status.HTTP_406_NOT_ACCEPTABLE)
            

        except ObjectDoesNotExist:
            return Response({
                'message':'invalid student email'

            },status=status.HTTP_404_NOT_FOUND)
        


class CalendlyWebHookView(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    
    def get(self,request):
        print('REQUEST', request)

        return Response('ok')
    

    def post(self,request):
        payload={
            'url':'https://ln7c3tgm-8000.uks1.devtunnels.ms/teacher/calendly/webhook/',
            "events":["invitee.created","invitee.canceled"],
            "organization":"https://api.calendly.com/organizations/8c22ac18-42f0-4cae-b127-09d1e60d3a13",
            "scope": "organization"
        }
        headers={
            "Authorization": f"Bearer eyJraWQiOiIxY2UxZTEzNjE3ZGNmNzY2YjNjZWJjY2Y4ZGM1YmFmYThhNjVlNjg0MDIzZjdjMzJiZTgzNDliMjM4MDEzNWI0IiwidHlwIjoiUEFUIiwiYWxnIjoiRVMyNTYifQ.eyJpc3MiOiJodHRwczovL2F1dGguY2FsZW5kbHkuY29tIiwiaWF0IjoxNzU3MzY5MTI0LCJqdGkiOiI5YzgyZDgyMC1jMjlhLTRkMDAtOWIxZC0wOTIxY2QxNGM5M2IiLCJ1c2VyX3V1aWQiOiI4Yzc5MTFmMi1lNWEwLTRkM2MtOGQ2ZC05MmQzYzEyNTgyNDIifQ.WSHckmBGYIkg0kZVxAViezlPsnkF7X-Ew0xYU848sAZzsLXIQNi7ClnEV_hjkCNA_6sAJf7w6p8SegkVX6frmw",
            "Content-Type": "application/json"
        }
        res=requests.post(url='https://api.calendly.com/webhook_subscriptions',json=payload, headers=headers)
        print(res.json())
        return Response('ok')



# Google Calendar Scopes
# SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",  # read/write events
    "https://www.googleapis.com/auth/calendar.readonly" # optional (still can fetch)
]


class ScheduleClassView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        """Fetch upcoming 10 events"""
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "client_secret.json", SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save the credentials for next use
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        try:
            service = build("calendar", "v3", credentials=creds)
            now = datetime.datetime.utcnow().isoformat() + "Z"

            events_result = (
                service.events()
                .list(
                    calendarId="primary",
                    timeMin=now,
                    maxResults=10,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events_result.get("items", [])

            data = []
            for event in events:
                data.append({
                    "id": event["id"],
                    "summary": event.get("summary"),
                    "start": event["start"].get("dateTime", event["start"].get("date")),
                    "end": event["end"].get("dateTime", event["end"].get("date")),
                })

            return Response({"events": data})

        except HttpError as error:
            return Response({"error": str(error)}, status=500)


class CreateEventView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        """Create a new event with guests and custom duration"""
        # Example payload from request
        summary = request.data.get("title", "Test Meeting")
        date=request.data.get("date", None)
        start=request.data.get("start", None)
        end=request.data.get("end", None)
        
        attendees = request.data.get("attendees", [{"email": "supersmartbuilders@gmail.com"}])

        if None in [date,start,end]:

            return Response({
                'message':'Value can\'t be empty',
                'data':{}
            },status=status.HTTP_406_NOT_ACCEPTABLE)
        
        else:
            
            creds = None
            start_time = f"{date}T{convert_24_to_12_hour(start)}:00+01:00"
            end_time = f"{date}T{convert_24_to_12_hour(end)}:00+01:00"
            if os.path.exists("token.json"):
                creds = Credentials.from_authorized_user_file("token.json", SCOPES)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        "client_secret.json", SCOPES
                    )
                    creds = flow.run_local_server(port=0)

                # Save the credentials for next use
                with open("token.json", "w") as token:
                    token.write(creds.to_json())

            try:

                service = build("calendar", "v3", credentials=creds)
                

                event = {
                    "summary": summary,
                    "start": {"dateTime": start_time, "timeZone": "UTC"},
                    "end": {"dateTime": end_time, "timeZone": "UTC"},
                    "attendees": attendees,
                }

                created_event = service.events().insert(
                    calendarId="primary", body=event
                ).execute()

                return Response({
                    "id": created_event["id"],
                    "link": created_event["htmlLink"]
                })
            except HttpError as error:
                return Response({"error": str(error)}, status=500)
