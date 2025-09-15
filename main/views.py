from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
import uuid
import simplejson
# import anthropic
import google.generativeai as genai
from main.models import *
from django.core.exceptions import ObjectDoesNotExist
import json
import re
from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools
from django.conf import settings
from google_auth_oauthlib.flow import InstalledAppFlow
import pandas as pd
from main.consumers import normalize_quiz_data
from django.conf import settings



User=MyUser
genai.configure(api_key="AIzaSyC89NegDIk0xmGLfTOKLzC7s1O5UrxGfsI")
# Create your views here.



def generate_id():
    generate_id = uuid.uuid4()
    try:
        Questionnaire.objects.get(id_tag=generate_id)

    except ObjectDoesNotExist:

        return generate_id


def IndexView(request):
    return render(request, 'main/index.html', {})

def SmartAcademyView(request):
    return render(request, 'main/smart_academy.html', {})

def EntryView(request):
    request.session['question'] = None
    q = request.GET.get('q')
    if request.method == 'POST':

        request.session['question'] = str(request.POST.get('question')).strip()
        questionaire = Questionnaire.objects.create(
            id_tag=generate_id()
        )
        question = Question.objects.create(
            question=str(request.POST.get('question')).strip(),

        )
        questionaire.questions.add(question)

        return HttpResponseRedirect(reverse('question_chat', kwargs={'id': questionaire.id_tag})+f'?q={q}')
    context = {'query': q}
    return render(request, 'main/entry.html', context)


def LessonPlanEntryView(request, entry):
    request.session['question'] = None
    request.session['class'] = None
    q = request.GET.get('q')
    if request.method == 'POST':

        request.session['question'] = str(request.POST.get('question')).strip()
        request.session['class'] = str(request.POST.get('class')).strip()
        questionaire = Questionnaire.objects.create(
            id_tag=generate_id()
        )
        # question=Question.objects.create(
        #     question=str(request.POST.get('question')).strip(),

        # )
        # questionaire.questions.add(question)

        return HttpResponseRedirect(reverse('lesson_chat', kwargs={'id': questionaire.id_tag}))
    context = {'query': q, 'entry': entry}
    return render(request, 'main/lesson_plan.html', context)


def QuestionEntryView(request, entry):
    request.session['question'] = None
    request.session['class'] = None
    request.session['no_of_questions'] = None

    q = request.GET.get('q')
    if request.method == 'POST':

        request.session['question'] = str(request.POST.get('question')).strip()
        request.session['class'] = str(request.POST.get('class')).strip()
        request.session['no_of_questions'] = str(
            request.POST.get('number_of_questions')).strip()
        questionaire = Questionnaire.objects.create(
            id_tag=generate_id()
        )
        # question=Question.objects.create(
        #     question=str(request.POST.get('question')).strip(),

        # )
        # questionaire.questions.add(question)

        return HttpResponseRedirect(reverse('question_chat', kwargs={'id': questionaire.id_tag}))
    context = {'query': q, 'entry': entry}
    return render(request, 'main/question.html', context)


def QuestionChatView(request, id):
    questionaires = Questionnaire.objects.all().order_by('-date_created')

    # quiz=Questionnaire.objects.get(id_tag=id).questions.all()[0].answer
    # # questions_section = quiz.split("**Questions:**")[1].split("**Answers:**")[0].strip()
    # print(quiz)

    question = request.session['question']
    no_of_questions=request.session['no_of_questions']
    student_class=request.session['class']
    q = str(request.GET.get('q')).strip()
    # print(question)
    context = {'generate_id': id, 'question': question,'no_of_questions':no_of_questions,
               'student_class':student_class,
               'q': 'question', 'questionaires': questionaires}
    request.session['question'] = None
    return render(request, 'main/question_chat.html', context)


def LessonChatView(request, id):
    questionaires = Questionnaire.objects.all().order_by('-date_created')

    # quiz=Questionnaire.objects.get(id_tag=id).questions.all()[0].answer
    # # questions_section = quiz.split("**Questions:**")[1].split("**Answers:**")[0].strip()
    # print(quiz)

    question = request.session['question']
    no_of_questions=request.session['no_of_questions']
    student_class=request.session['class']
    q = str(request.GET.get('q')).strip()
    # print(question)
    context = {'generate_id': id, 'question': question,'no_of_questions':no_of_questions,
               'student_class':student_class,
               'q': 'lesson', 'questionaires': questionaires}
    request.session['question'] = None
    return render(request, 'main/lesson_chat.html', context)







SCOPES = "https://www.googleapis.com/auth/forms.body"
DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"
flags = tools.argparser.parse_args(args=[])


def ExportToGoogleForm(request, id):
    quiz = Questionnaire.objects.get(id_tag=id)
    answer = quiz.questions.all()[0].raw_answer
    q = str(request.GET.get('q')).strip()
    
    cleaned_json = re.sub(r"```(?:json)?\s*|\s*```", "", str(answer).replace("**","").replace("*",".")).strip()
  
    # # questions_section = quiz.split("**Questions:**")[1].split("**Answers:**")[0].strip()
    # print('JSON ANSWER %s' %(json.loads(cleaned_json)))
    quiz_data = []    


    
    try:
        json_question = normalize_quiz_data(raw_data=json.loads(cleaned_json))
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

    # creds = store.get()
    creds = None
    if not creds or creds.invalid:
        print(True)
        flow = client.flow_from_clientsecrets("client_secret.json", SCOPES)
        print(flow)
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
        print('quest ',ques)

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
                                    "answers": [{"value":ques['answer'] }]
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
        return redirect(get_result['responderUri'])

    return HttpResponseRedirect(reverse('question_chat', kwargs={'id': quiz.id_tag})+f'?q={q}')
