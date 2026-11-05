from django.shortcuts import render

def index(request):
    questions = []
    for i in range(1, 6):
        questions.append({
            'id': i,
            'title': f'Заголовок вопроса {i}',
            'text': f'Текст описания для вопроса {i}',
            'tags': ['python', 'django'],
            'answers_count': i * 2,
            'rating': i * 5
        })
    return render(request, 'questions/index.html', {'questions': questions})

def hot(request):
    return render(request, 'questions/hot.html')

def tag(request, tag_name):
    return render(request, 'questions/tag.html', {'tag_name': tag_name})

def question(request, question_id):
    return render(request, 'questions/question.html', {'question_id': question_id})

def ask(request):
    return render(request, 'questions/ask.html')