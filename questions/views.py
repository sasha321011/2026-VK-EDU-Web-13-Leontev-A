from django.shortcuts import render, get_object_or_404
from .models import Question, Tag
from .utils import paginate


def index(request):
    page = paginate(Question.objects.new(), request, 10)
    return render(request, 'questions/index.html', {
        'page': page,
        'questions': page.object_list,
        'popular_tags': Tag.objects.all()[:10],
    })


def hot(request):
    page = paginate(Question.objects.hot(), request, 10)
    return render(request, 'questions/hot.html', {
        'page': page,
        'questions': page.object_list,
        'popular_tags': Tag.objects.all()[:10],
    })


def tag(request, tag_name):
    tag_obj = get_object_or_404(Tag, name=tag_name)
    page = paginate(Question.objects.by_tag(tag_name), request, 10)
    return render(request, 'questions/tag.html', {
        'page': page,
        'questions': page.object_list,
        'tag': tag_obj,
        'popular_tags': Tag.objects.all()[:10],
    })


def question(request, question_id):
    q = get_object_or_404(Question, id=question_id)
    answers = q.answers.select_related('author').all()
    page = paginate(answers, request, 5)
    return render(request, 'questions/question.html', {
        'question': q,
        'page': page,
        'answers': page.object_list,
        'popular_tags': Tag.objects.all()[:10],
    })


def ask(request):
    return render(request, 'core/ask.html')
