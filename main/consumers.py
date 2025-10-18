import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
import re
import typing_extensions as typing
from asgiref.sync import sync_to_async
import pandas as pd
from urllib.parse import parse_qs
from pydantic import BaseModel
from google import genai
from django.conf import settings
from .AiUtils import generate_from_prompt
from .models import *

client = genai.Client(api_key='AIzaSyBC2fxSmEO5NzNGxGUV9djbENKIyWTtl3Q')
aichat = client.chats.create(model='gemini-2.5-flash')


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query_string = parse_qs(self.scope['query_string'].decode())
        chat_history = query_string.get('chat_history', False)[0]
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        user = None

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )

        await self.accept()

        if chat_history in ['true', True]:
            data = await self.get_chat_log(id=self.room_name,user=user)
            await self.send(text_data=json.dumps(data))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)



    # Receive message from WebSocket
    async def receive(self, text_data):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]

        text_data_json = json.loads(text_data)

        message = text_data_json["message"]
        text_data_json = json.loads(text_data)
        print(text_data_json)
        
        # user = self.scope['user']

        await self.send(text_data=json.dumps({'prompt': message, 'type': 'chat_message'}))

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message",
                                   "message": message,
                                   'room_name':self.room_name

                                   }
        )




    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        room_name = event["room_name"]
        user=None
        

        response = aichat.send_message(f'{message}')
        # http = response.sdk_http_response
        # print(http.body)
        # print("Available attributes:", dir(http))


        chat = await sync_to_async(Question.objects.create)(
            user=user,
            prompt=message,
        )

        all_chats, _ = await sync_to_async(Questionnaire.objects.get_or_create)(
            user=user,
            id_tag=room_name
        )
        await sync_to_async(all_chats.chats.add)(chat)
        # Send message to WebSocket

        await self.send(text_data=json.dumps({"message": response.text, 'prompt': message}))

        await self.save_chat_answer(chat=chat, response_text=response.text)






    @sync_to_async
    def get_chat_log(self, id,user):
        try:
            allchats = Questionnaire.objects.get(user=user,id_tag=id)
            messages = []

            for chat in allchats.chats.all():
                messages.append({'message': chat.raw_response,
                                'prompt': chat.prompt, 'type': 'chat_history'})
            return messages
        except Questionnaire.DoesNotExist:
            return []

    @sync_to_async
    def save_chat_answer(self, chat, response_text):
        cleaned_json = re.sub(r"```(?:json)?", "", str(response_text)).strip()
        chat.raw_response = response_text
        chat.answer = cleaned_json
        
        chat.save()
