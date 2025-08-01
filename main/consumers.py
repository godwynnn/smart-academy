import json
from openai import OpenAI
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer,AsyncWebsocketConsumer
import google.generativeai as genai
from .models import Question,Questionnaire
import re
import typing_extensions as typing
from asgiref.sync import sync_to_async
import pandas as pd
from urllib.parse import parse_qs


class Answer(typing.TypedDict):
    title:str
    options:list[str]
    answer:str

genai.configure(api_key="AIzaSyBC2fxSmEO5NzNGxGUV9djbENKIyWTtl3Q")


client = OpenAI(
    api_key="sk-7a8697c73fd24b02a79682d6025f3f37",
    base_url="https://api.deepseek.com",
)




class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        user=self.scope['user']
        
        

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )

        await self.accept()
       
        
        questions=await self.get_chat_log(self.room_name)
        # print(questions)

       
        await self.send(text_data=json.dumps({
            'type': "chat_history",
            'messages': questions,
            'sent_by':'user'
        }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
       
        text_data_json = json.loads(text_data)
        print(text_data_json)
        user=self.scope['user']
        subject=text_data_json['message']['subject']
        username=text_data_json['username']
        no_questions=''
        class_no=text_data_json['message']['class']
        generate_id=text_data_json['generate_id']
        prompt_type=text_data_json["prompt_type"]

        

        message=''
        if prompt_type == 'question':
            no_questions=text_data_json['message']['no_questions']
            message=f'Generate {no_questions} {subject} quiz question for {class_no} students'
        else:
            message=f'Generate a lesson plan on {subject} for {class_no} students'
        

        await self.send(text_data=json.dumps({"type": "chat_message","message": message,'sent_by':'user','relayed':True}))
        question=await sync_to_async(Question.objects.create)(
            user=user,
            question=str(class_no +' '+subject+' '+ prompt_type).strip(),
            category=str(prompt_type).strip().lower()
        )
        
        # Get the Questionnaire instance asynchronously
        # questionnaire = await sync_to_async(Questionnaire.objects.get)(id_tag=generate_id)
        questionnaire,_ = await sync_to_async(Questionnaire.objects.get_or_create)(user=user,id_tag=generate_id,
                                                                                   entry_type=str(prompt_type).strip().lower())

        # Then, add the question (this is a DB operation too, so wrap it)
        await sync_to_async(questionnaire.questions.add)(question)

                # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", 
                                   "message": message,
                                   'id':question.pk,
                                   "prompt_type":prompt_type,
                                   'sent_by':'user'
                                   
                                   }
        )
        

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        id=event["id"]
        prompt_type=event['prompt_type']
        # print(prompt_type)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        
        
        chat = model.start_chat() 
        response=''
        if prompt_type == 'question':
            response = chat.send_message(f'{message} with options and answers in JSON format ')
        else:
            response = chat.send_message(f'{message} ')
        print(response)
        question= await self.get_question_by_id(id)
        await self.save_question_answer(question=question,response_text=response.text)
        cleaned_json = re.sub(r"```(?:json)?", "", str(response.text)).strip()
        data=cleaned_json
        if prompt_type == 'question': 
            data=normalize_quiz_data(raw_data=cleaned_json)
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"type": "chat_message","message": data,'sent_by':'ai'}))



    @sync_to_async
    def get_question_by_id(self,id):
        return Question.objects.get(id=id)

    @sync_to_async
    def save_question_answer(self,question, response_text):
        cleaned_json = re.sub(r"```(?:json)?", "", str(response_text)).strip()
        question.answer = cleaned_json
        question.raw_answer = response_text
        question.save()
        
    @sync_to_async
    def get_chat_log(self, id):
        try:
            questionaire=Questionnaire.objects.get(id_tag=id)

            if questionaire.entry_type == 'lesson':
                return [{"question":question.question,"answer":question.answer} for question in questionaire.questions.all()]
            else:
        
                return [{"question":question.question,"answer":normalize_quiz_data(raw_data=question.answer)} for question in questionaire.questions.all()]
        except Questionnaire.DoesNotExist:
            return []



def normalize_quiz_data(raw_data):
    """
    Applies ETL to ensure the data is always wrapped with a 'quiz' key.
    """

    # --------- Extract ---------
    if isinstance(raw_data, str):
        try:
            data = json.loads(raw_data)
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON input") from e
    else:
        data = raw_data

    # --------- Transform ---------
    if isinstance(data, list):
        # Wrap the list in a 'quiz' key
        normalized_data = { "quiz": data }
    elif isinstance(data, dict) and "quizzes" in data:
        data['quiz']=data.pop('quizzes')
        normalized_data=data
    elif isinstance(data, dict) and "questions" in data:
        data['quiz']=data.pop('questions')
        normalized_data=data
    elif isinstance(data, dict) and "quizQuestions" in data:
        data['quiz']=data.pop('quizQuestions')
        normalized_data=data

    elif isinstance(data, dict) and "quiz" in data:
        normalized_data = data
    else:
        raise ValueError("Data zformat not recognized: must be a list or dict with 'quiz' key.")

    # print('DATA ',normalized_data)
    # --------- Load (e.g. return, store, or export) ---------
    return normalized_data
