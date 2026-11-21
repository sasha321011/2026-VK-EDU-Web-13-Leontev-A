from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum

from .models import Question, Tag, QuestionLike, AnswerLike
from .forms import AskForm, AnswerForm, QuestionLikeForm, AnswerLikeForm, CorrectAnswerForm
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
    q.rating = q.likes.aggregate(s=Sum('value'))['s'] or 0

    answers = (q.answers
               .select_related('author')
               .annotate(rating=Sum('likes__value'))
               .all())
    page = paginate(answers, request, 5)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login' + '?next=' + request.path)
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author = request.user
            answer.question = q
            answer.save()
            last_page = page.paginator.num_pages
            return redirect(f"{q.get_absolute_url()}?page={last_page}#answer-{answer.id}")
    else:
        form = AnswerForm()

    return render(request, 'questions/question.html', {
        'question': q,
        'page': page,
        'answers': page.object_list,
        'form': form,
        'popular_tags': Tag.objects.all()[:10],
    })


@login_required
def ask(request):
    if request.method == 'POST':
        form = AskForm(request.POST)
        if form.is_valid():
            form.instance.author = request.user
            question = form.save()
            return redirect('question', question_id=question.id)
    else:
        form = AskForm()

    return render(request, 'questions/ask.html', {
        'form': form,
        'popular_tags': Tag.objects.all()[:10],
    })


# ============ AJAX ============

@require_POST
def question_like(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'auth_required'}, status=403)

    form = QuestionLikeForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': form.errors}, status=400)

    form.save(request.user)
    rating = (QuestionLike.objects
              .filter(question_id=form.cleaned_data['object_id'])
              .aggregate(s=Sum('value'))['s'] or 0)
    return JsonResponse({'rating': rating})


@require_POST
def answer_like(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'auth_required'}, status=403)

    form = AnswerLikeForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': form.errors}, status=400)

    form.save(request.user)
    rating = (AnswerLike.objects
              .filter(answer_id=form.cleaned_data['object_id'])
              .aggregate(s=Sum('value'))['s'] or 0)
    return JsonResponse({'rating': rating})


@require_POST
def mark_correct(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'auth_required'}, status=403)

    form = CorrectAnswerForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': form.errors}, status=400)

    answer = form.cleaned_data['answer']
    question = answer.question

    if question.author != request.user:
        return JsonResponse({'error': 'not_author'}, status=403)

    question.answers.update(is_correct=False)
    answer.is_correct = True
    answer.save()
    return JsonResponse({'ok': True, 'answer_id': answer.id})
