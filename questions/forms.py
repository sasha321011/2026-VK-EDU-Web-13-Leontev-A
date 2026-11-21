from django import forms
from django.core.exceptions import ValidationError

from .models import Question, Answer, Tag, QuestionLike, AnswerLike


class AskForm(forms.ModelForm):
    tags = forms.CharField(
        label='Теги',
        help_text='Через запятую, не более 5 тегов. Например: python, django',
        required=False,
    )

    class Meta:
        model = Question
        fields = ('title', 'text')

    def clean_tags(self):
        raw = self.cleaned_data.get('tags', '')
        names = [n.strip() for n in raw.split(',') if n.strip()]
        if len(names) > 5:
            raise ValidationError('Не более 5 тегов.')
        return names

    def save(self, commit=True):
        question = super().save(commit=False)
        if commit:
            question.save()
            for name in self.cleaned_data.get('tags', []):
                tag, _ = Tag.objects.get_or_create(name=name)
                question.tags.add(tag)
        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('text',)


class QuestionLikeForm(forms.Form):
    LIKE = 'like'
    DISLIKE = 'dislike'
    TYPE_CHOICES = [(LIKE, 'Like'), (DISLIKE, 'Dislike')]

    object_id = forms.IntegerField(min_value=1)
    type = forms.ChoiceField(choices=TYPE_CHOICES)

    def clean_object_id(self):
        obj_id = self.cleaned_data['object_id']
        if not Question.objects.filter(id=obj_id).exists():
            raise ValidationError('Вопрос не найден.')
        return obj_id

    def save(self, user):
        obj_id = self.cleaned_data['object_id']
        value = 1 if self.cleaned_data['type'] == self.LIKE else -1
        like, _ = QuestionLike.objects.update_or_create(
            user=user,
            question_id=obj_id,
            defaults={'value': value},
        )
        return like


class AnswerLikeForm(forms.Form):
    LIKE = 'like'
    DISLIKE = 'dislike'
    TYPE_CHOICES = [(LIKE, 'Like'), (DISLIKE, 'Dislike')]

    object_id = forms.IntegerField(min_value=1)
    type = forms.ChoiceField(choices=TYPE_CHOICES)

    def clean_object_id(self):
        obj_id = self.cleaned_data['object_id']
        if not Answer.objects.filter(id=obj_id).exists():
            raise ValidationError('Ответ не найден.')
        return obj_id

    def save(self, user):
        obj_id = self.cleaned_data['object_id']
        value = 1 if self.cleaned_data['type'] == self.LIKE else -1
        like, _ = AnswerLike.objects.update_or_create(
            user=user,
            answer_id=obj_id,
            defaults={'value': value},
        )
        return like


class CorrectAnswerForm(forms.Form):
    answer_id = forms.IntegerField(min_value=1)

    def clean_answer_id(self):
        answer_id = self.cleaned_data['answer_id']
        if not Answer.objects.filter(id=answer_id).exists():
            raise ValidationError('Ответ не найден.')
        return answer_id

    def clean(self):
        cleaned = super().clean()
        answer_id = cleaned.get('answer_id')
        if answer_id:
            answer = Answer.objects.select_related('question').get(id=answer_id)
            cleaned['answer'] = answer
        return cleaned
    