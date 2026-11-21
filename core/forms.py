from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Profile
from questions.models import Question, Answer, Tag, QuestionLike, AnswerLike


class LoginForm(forms.Form):
    username = forms.CharField(label='Логин', max_length=150)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        username = cleaned.get('username')
        password = cleaned.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise ValidationError('Неверный логин или пароль.')
            cleaned['user'] = user
        return cleaned


class SignupForm(forms.ModelForm):
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password_confirm = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput)
    avatar = forms.ImageField(label='Аватар', required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name')

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким логином уже существует.')
        return username

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password')
        p2 = cleaned.get('password_confirm')
        if p1 and p2 and p1 != p2:
            raise ValidationError('Пароли не совпадают.')
        if p1:
            try:
                validate_password(p1)
            except ValidationError as e:
                self.add_error('password', e)
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                avatar=self.cleaned_data.get('avatar')
            )
        return user


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'first_name')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar',)

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            if avatar.size > 2 * 1024 * 1024:
                raise ValidationError('Файл больше 2 МБ.')
            if not avatar.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                raise ValidationError('Только JPG, PNG, GIF.')
        return avatar
