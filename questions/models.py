from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.db.models import Sum, Count


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class QuestionManager(models.Manager):
    def new(self):
        return (self.select_related('author')
                    .prefetch_related('tags')
                    .annotate(
                        answers_count=Count('answers'),
                        rating=Sum('likes__value'),   # ← добавить
                    )
                    .order_by('-created_at'))

    def hot(self):
        return (self.select_related('author')
                    .prefetch_related('tags')
                    .annotate(
                        answers_count=Count('answers'),
                        rating=Sum('likes__value'),
                    )
                    .order_by('-rating', '-created_at'))

    def by_tag(self, tag_name):
        return (self.select_related('author')
                    .prefetch_related('tags')
                    .annotate(
                        answers_count=Count('answers'),
                        rating=Sum('likes__value'),
                    )
                    .filter(tags__name=tag_name)
                    .order_by('-created_at'))

class Question(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    title = models.CharField(max_length=255)
    text = models.TextField()
    tags = models.ManyToManyField(Tag, related_name='questions', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = QuestionManager()

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('question', args=[self.id])


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'

    def __str__(self):
        return f'Ответ #{self.id}'


class QuestionLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_likes')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='likes')
    value = models.SmallIntegerField(choices=[(1, 'Лайк'), (-1, 'Дизлайк')])

    class Meta:
        verbose_name = 'Лайк вопроса'
        verbose_name_plural = 'Лайки вопросов'
        unique_together = ('user', 'question')


class AnswerLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answer_likes')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='likes')
    value = models.SmallIntegerField(choices=[(1, 'Лайк'), (-1, 'Дизлайк')])

    class Meta:
        verbose_name = 'Лайк ответа'
        verbose_name_plural = 'Лайки ответов'
        unique_together = ('user', 'answer')