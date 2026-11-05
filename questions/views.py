from django.shortcuts import render
from .utils import paginate

def index(request):
    questions = []
    for i in range(1, 26):
        questions.append({
            'id': i,
            'title': f'Заголовок вопроса {i}',
            'text': f'Текст описания для вопроса {i}',
            'tags': ['python', 'django'],
            'answers_count': i * 2,
            'rating': i * 5
        })

    page = paginate(questions, request, per_page=10)

    return render(request, 'questions/index.html', {'questions': page})

def hot(request):
    questions = []
    for i in range(1, 16):
        questions.append({
            'id': i,
            'title': f'Лучший вопрос {i}',
            'text': f'Текст лучшего вопроса {i}',
            'tags': ['python', 'django'],
            'answers_count': i * 3,
            'rating': i * 10
        })
    page = paginate(questions, request, per_page=10)
    return render(request, 'questions/hot.html', {'questions': page})

def tag(request, tag_name):
    questions = []
    for i in range(1, 13):
        questions.append({
            'id': i,
            'title': f'Вопрос {i} по тегу {tag_name}',
            'text': f'Текст вопроса {i}',
            'tags': [tag_name],
            'answers_count': i,
            'rating': i * 2
        })
    page = paginate(questions, request, per_page=10)
    return render(request, 'questions/tag.html', {'questions': page, 'tag_name': tag_name})

def question(request, question_id):
    question_data = {
        'id': question_id,
        'title': f'Как работает Django? (вопрос ID: {question_id})',
        'text': 'Не понимаю ничего?',
        'tags': ['django', 'python', 'orm'],
        'rating': 24,
    }
    
    answers = []
    for i in range(1, 4):
        answers.append({
            'id': i,
            'text': f'Это текст ответа номер {i}. Используй документацию.',
            'rating': i * 5,
            'is_correct': (i == 2)
        })
        
    return render(request, 'questions/question.html', {
        'question': question_data,
        'answers': answers })

def ask(request):
    return render(request, 'questions/ask.html')