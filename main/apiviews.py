from rest_framework.views import APIView
import uuid
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from .serializers import *
from .models import *
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework.pagination import LimitOffsetPagination
from .paginator import CustomPagination
from oauth2client import client, file, tools
from apiclient import discovery
import json
# from main.consumers import normalize_quiz_data
import re
from httplib2 import Http
from rest_framework_simplejwt.authentication import JWTAuthentication
from .AiUtils import generate_from_prompt


class EntryView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes=[JWTAuthentication]


    def get(self, request):
        print(request.user)
        return Response({
            'room_name': uuid.uuid4()
        }, status=status.HTTP_200_OK)


class CreateQuestionsByAiView(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    def post(self, request,id):
        try:
            message=request.data.get('message',None)
            username=request.data.get('username')
            generate_id=request.data.get('generate_id')
            prompt_type=request.data.get('prompt_type')

            if message is not None:

                prompt=None
                if prompt_type == 'question':
                    prompt=f'Generate {message['no_questions']} {message['subject']}  quiz question for {message['class']} students'
                else:
                    prompt=f'Generate a lesson plan on {message['subject']} for {message['class']} students'
                
                res,raw_reponse=generate_from_prompt(prompt)
                Question.objects.create(
                    user=request.user,
                    question=str(message['class'] +' '+message['subject']+' '+ prompt_type).strip(),
                    category=str(prompt_type).strip().lower(),
                    raw_answer=res
                )

        except Exception as e:
            return Response({
                'error':f"error occured at {e}"
            }, status=status.HTTP_400_BAD_REQUEST)
        


class QuestionsView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes=[JWTAuthentication]

    def get(self, request):
        q = request.GET.get('q', None)
        paginator = CustomPagination()
            
        print(q)
        try:

            obj = Questionnaire.objects.filter(user=request.user).order_by('-date_created')
            

            if q is not None:
                # obj=[data.entry_type == Questionnaire.objects.get(id_tag=q).entry_type
                #      for data in Questionnaire.objects.all().order_by('-date_created')]

                obj = Questionnaire.objects.filter(user=request.user,
                    entry_type=q).order_by('-date_created')
            

            result = paginator.paginate_queryset(queryset=obj, request=request)
            serializer = QuestionaireSerializer(result, many=True).data
            for data in serializer:
                data['questions'] = QuestionSerializer(
                    Question.objects.filter(id__in=data['questions']), many=True).data

            return Response({
                'data': serializer
            }, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({
                'data': []
            }, status=status.HTTP_204_NO_CONTENT)







SCOPES = "https://www.googleapis.com/auth/forms.body"
DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"
flags = tools.argparser.parse_args(args=[])


class ExportToGoogleFormView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    def get(self, request, id):
        quiz = Questionnaire.objects.get(id_tag=id)
        answer = quiz.questions.all()[0].raw_answer
        q = str(request.GET.get('q')).strip()

        cleaned_json = re.sub(r"```(?:json)?\s*|\s*```", "",
                            str(answer).replace("**", "").replace("*", ".")).strip()

        # # questions_section = quiz.split("**Questions:**")[1].split("**Answers:**")[0].strip()
        # print('JSON ANSWER %s' %(json.loads(cleaned_json)))
        quiz_data = []

        try:
            # json_question = normalize_quiz_data(raw_data=json.loads(cleaned_json))
            json_question = json.loads(cleaned_json)
            print('Parsed JSON:', json_question)
        except json.JSONDecodeError as e:
            print('JSON decode error:', e)

        # try:
        #     json_question = json.loads(answer)
        #     title=json.loads(answer)
        # except:
        #     json_question = json.loads(answer)
        #     title=json.loads(answer)
        # print(json_question)

        for i in range(0, len(json_question['quiz'])):
            questions = {}
            questions['question'] = json_question['quiz'][i]['question']

            questions['option'] = []
            print(i)

            for option in json_question['quiz'][i]['options']:
                questions['option'].append(option)
            questions['answer'] = json_question['quiz'][i]['answer']
            quiz_data.append(questions)
        print('OUTSIDE LOOP', quiz_data)

        store = file.Storage("token.json")
        print(store)

        creds = store.get()
        # creds = None
        if not creds or creds.invalid:
            print(True)
            flow = client.flow_from_clientsecrets("client_secret.json", SCOPES)
            creds = tools.run_flow(flow, store, flags)
            # print(creds)

        form_service = discovery.build(
            "forms",
            "v1",
            http=creds.authorize(Http()),
            discoveryServiceUrl=DISCOVERY_DOC,
            static_discovery=False,
        )

        # Request body for creating a form
        NEW_FORM = {
            "info": {
                "title": quiz.questions.all()[0].question,
            }
        }

        # JSON to convert the form into a quiz
        update = {
            "requests": [
                {
                    "updateSettings": {
                        "settings": {"quizSettings": {"isQuiz": True}},
                        "updateMask": "quizSettings.isQuiz",
                    }
                }
            ]
        }

        # Request body to add a multiple-choice question
        requests = []
        for ques in quiz_data:
            print('quest ', ques)

            obj = {
                "createItem": {
                    "item": {
                        "title": (
                            ques['question']
                        ),

                        "questionItem": {
                            "question": {
                                "required": True,
                                "grading": {
                                    "pointValue": 2,
                                    "correctAnswers": {
                                        "answers": [{"value": ques['answer']}]
                                    },
                                    "whenRight": {"text": "You got it!"},
                                    "whenWrong": {"text": "Sorry, that's wrong"}
                                },
                                "choiceQuestion": {
                                    "type": "RADIO",
                                    "options": [
                                        {"value": ques['option'][0]},
                                        {"value": ques['option'][1]},
                                        {"value": ques['option'][2]},
                                        {"value": ques['option'][3]},
                                    ],
                                    "shuffle": True,
                                },
                            }
                        },
                    },
                    "location": {"index": 0},
                },

            }
            requests.append(obj)

        NEW_QUESTION = {
            "requests": requests
        }
        print(NEW_QUESTION)

        # Creates the initial form
        result = form_service.forms().create(body=NEW_FORM).execute()

        # Converts the form into a quiz
        question_setting_update = (
            form_service.forms()
            .batchUpdate(formId=result["formId"], body=update)
            .execute()
        )

        # Adds the question to the form
        question_setting = (
            form_service.forms()
            .batchUpdate(formId=result["formId"], body=NEW_QUESTION)
            .execute()
        )

        # Prints the result to show the question has been added
        get_result = form_service.forms().get(formId=result["formId"]).execute()
        if get_result != {}:
            return Response({
                'status':status.HTTP_200_OK,
                'url':get_result['responderUri']
                })

        return Response('ok')
