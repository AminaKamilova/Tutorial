from django.contrib.auth.decorators import login_required
from django.forms import fields
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from .models import Courses
from .forms import LoginForm, UserForm
from django.db.models import Count, F, ExpressionWrapper, fields
from django.utils.translation import gettext_lazy as _
from datetime import datetime


def index(request):
    courses_list = Courses.objects.all()
    return render(request, "main/index.html", {'courses': courses_list})


def courses(request):
    courses_list = Courses.objects.all()
    return render(request, "main/courses.html", {'courses': courses_list})

from .forms import CategoryForm
from django.shortcuts import redirect


@login_required
def categories(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Категория успешно добавлена!')
            return redirect('categories')
    else:
        form = CategoryForm()

    return render(request, "main/categories.html", {'form': form})


@login_required
def reports(request):
    if request.method == 'POST':
        if 'category' in request.POST:
            category_form = CategoryReportForm(request.POST)
            if category_form.is_valid():
                category = category_form.cleaned_data['category']
                return redirect('category_report', category_id=category.id)
        elif 'start_date' in request.POST:
            period_form = PeriodReportForm(request.POST)
            if period_form.is_valid():
                start_date = period_form.cleaned_data['start_date']
                end_date = period_form.cleaned_data['end_date']
                return redirect('period_report', start_date=start_date.isoformat(), end_date=end_date.isoformat())
    else:
        category_form = CategoryReportForm()
        period_form = PeriodReportForm()

    return render(request, "main/reports.html", {
        'category_form': category_form,
        'period_form': period_form,
    })


def registration_email(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, 'Вы успешно зарегистрировались!')
            return redirect('home')
    else:
        form = UserForm()
    return render(request, "main/registration_email.html", {'form': form})


def course(request):
    return render(request, "main/course.html")


from .forms import CategoryReportForm, PeriodReportForm


def add_course(request, course_id):
    if course_id == 0:
        if request.method == 'POST':
            form = CourseForm(request.POST)
            if form.is_valid():
                course = form.save(commit=False)
                course.user_id = request.user
                course.save()
                messages.success(request, 'Курс успешно добавлен!')
                return redirect('categories')
        else:
            form = CourseForm()
    else:
        course = Courses.objects.get(id=course_id)
        if request.method == 'POST':
            form = CourseForm(request.POST, instance=course)
            if form.is_valid():
                course = form.save()
                messages.success(request, 'Курс успешно изменён!')
                return redirect('categories')
        else:
            form = CourseForm(instance=course)
    return render(request, "main/add_course.html", {'form': form, 'course_id': course_id})

def add_lesson(request, lesson_id):
    if lesson_id == 0:
        if request.method == 'POST':
            form = LessonForm(request.POST)
            if form.is_valid():
                lesson = form.save(commit=False)
                lesson.user_id = request.user
                lesson.save()
                messages.success(request, 'Урок успешно добавлен!')
                course_id = lesson.course_id.id
                return redirect('course_detail', course_id=course_id)
        else:
            form = LessonForm()
    else:
        lesson = Lessons.objects.get(id=lesson_id)
        if request.method == 'POST':
            form = LessonForm(request.POST, instance=lesson)
            if form.is_valid():
                form.save()
                messages.success(request, 'Урок успешно изменён!')
                course_id = lesson.course_id.id
                return redirect('course_detail', course_id=course_id)
        else:
            form = LessonForm(instance=lesson)
    return render(request, "main/add_lesson.html", {'form': form, 'lesson_id': lesson_id})

def login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f'Добро пожаловать, {user.user_name}!')
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, "main/login.html", {'form': form})


def logout(request):
    auth_logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('home')


@login_required
def period_report(request, start_date, end_date):
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    report_data = Courses.objects.filter(
        start_date__range=(start_date, end_date)
    ).annotate(
        duration=ExpressionWrapper(
            F('end_date') - F('start_date'),
            output_field=fields.DurationField()
        ),
        lessons_count=Count('lessons')
    ).select_related('user_id').order_by('start_date')

    return render(request, 'main/period_report_result.html', {
        'report_data': report_data,
        'title': _('Отчет за выбранный период')
    })


def category_report(request, category_id):
    category = Categories.objects.get(id=category_id)
    report_data = Courses.objects.filter(
        category_id=category
    ).annotate(
        duration=ExpressionWrapper(
            F('end_date') - F('start_date'),
            output_field=fields.DurationField()
        ),
        lessons_count=Count('lessons')
    ).select_related('user_id').order_by('start_date')

    return render(request, 'main/category_report_result.html', {
        'report_data': report_data,
        'category': category,
        'title': _('Отчет по категории')
    })

    # return render(request, 'main/category_report_result .html', {
    #     'form': form,
    #     'title': _('Отчет по категории')
    # })


from django.shortcuts import render, redirect, get_object_or_404
from .models import Courses, Categories, Lessons
from .forms import CourseForm, LessonForm


def course_detail(request, course_id):
    course = Courses.objects.get(id=course_id)
    lessons = Lessons.objects.filter(course_id=course_id)
    return render(request, 'main/course_detail.html', {
        'course': course,
        'lessons': lessons,
    })


@login_required
def edit_course(request, course_id):
    course = get_object_or_404(Courses, pk=course_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Курс успешно обновлен!')
            return redirect('course_detail', course_id=course_id)
    else:
        form = CourseForm(instance=course)
    return render(request, 'main/add_course.html', {
        'form': form,
        'course': course,
        'categories': Categories.objects.all(),
    })


@login_required
def delete_course(request, course_id):
    course = get_object_or_404(Courses, pk=course_id)
    course.delete()
    messages.success(request, 'Курс успешно удален!')
    return redirect('courses')

@login_required
def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lessons, pk=lesson_id)
    course_id = lesson.course_id.id
    lesson.delete()
    messages.success(request, 'Курс успешно удален!')
    return redirect('course_detail', course_id=course_id)

def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categories')
    else:
        form = CategoryForm()
    return render(request, "main/add_categories.html", {'form': form})
