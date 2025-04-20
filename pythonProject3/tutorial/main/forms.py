from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Courses, Categories, Lessons, Users


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={'placeholder': 'Логин'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'})
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError('Неверный логин или пароль')
        return cleaned_data


class UserForm(UserCreationForm):
    class Meta:
        model = Users
        fields = ['login', 'user_name', 'user_email', 'password1', 'password2']
        labels = {
            'login': 'Логин',
            'user_name': 'Имя пользователя',
            'user_email': 'Email',
            'password1': 'Пароль',
            'password2': 'Подтверждение пароля',
        }
        widgets = {
            'login': forms.TextInput(attrs={'placeholder': 'Логин'}),
            'user_name': forms.TextInput(attrs={'placeholder': 'Имя пользователя'}),
            'user_email': forms.EmailInput(attrs={'placeholder': 'Email'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Установка плейсхолдеров для password1 и password2 вручную
        self.fields['password1'].widget.attrs.update({'placeholder': 'Пароль'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Подтверждение пароля'})


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Categories
        fields = ['category_name', 'description']
        labels = {
            'category_name': 'Название категории',
            'description': 'Описание'
        }
        widgets = {
            'category_name': forms.TextInput(attrs={'placeholder': 'Название'}),
            'description': forms.Textarea(attrs={'placeholder': 'Описание'}),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Courses
        fields = ['course_name', 'start_date', 'end_date', 'category_id', 'image']  # Добавляем image в поля
        labels = {
            'course_name': 'Название курса',
            'start_date': 'Дата начала',
            'end_date': 'Дата окончания',
            'category_id': 'Категория',
            'image': 'Изображение курса',
        }
        widgets = {
            'course_name': forms.TextInput(attrs={'class': 'input-field'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'category_id': forms.Select(attrs={'class': 'input-field'}),
        }
    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        self.fields['category_id'].empty_label = "Выберите категорию"

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lessons
        fields = ['course_id', 'lesson_num', 'description']
        labels = {
            'course_id': 'Курс',
            'lesson_num': 'Номер урока',
            'description': 'Описание',
        }
        widgets = {
            'course_id': forms.Select(attrs={'class': 'input-field'}),
            'lesson_num': forms.NumberInput(attrs={'class': 'input-field'}),
            'description': forms.Textarea(attrs={'placeholder': 'Описание урока'}),
        }

    def __init__(self, *args, **kwargs):
        super(LessonForm, self).__init__(*args, **kwargs)
        self.fields['course_id'].empty_label = "Выберите курс"


class PeriodReportForm(forms.Form):
    start_date = forms.DateField(
        label=_('Дата начала'),
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'input-field',
            'placeholder': 'Выберите дату начала'
        })
    )
    end_date = forms.DateField(
        label=_('Дата окончания'),
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'input-field',
            'placeholder': 'Выберите дату окончания'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError(
                "Дата начала не может быть позже даты окончания"
            )

        return cleaned_data

class CategoryReportForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Categories.objects.all(),
        label=_('Категория'),
        widget=forms.Select(attrs={
            'class': 'input-field',
            'placeholder': 'Выберите категорию'
        }),
        empty_label="Выберите категорию"
    )