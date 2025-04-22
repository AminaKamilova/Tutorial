from datetime import datetime

from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models import F, ExpressionWrapper, fields
from django.forms import fields
from django.utils.translation import gettext_lazy as _
from .forms import LoginForm, UserForm, CategoryForm
from .models import Courses, Categories, Lessons
from .forms import CourseForm, LessonForm
from django.db.models import DurationField
from django.http import HttpResponse
from openpyxl import Workbook
from io import BytesIO
from reportlab.pdfgen import canvas
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.db.models import Count, F, DurationField
from django.db.models.functions import ExtractDay


def courses(request):
    courses_list = Courses.objects.all()
    return render(request, "main/courses.html", {'courses': courses_list})


@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, 'Категория успешно добавлена!')
            return redirect('category_detail', category_id=category.id)
    else:
        form = CategoryForm()
    return render(request, "main/add_categories.html", {'form': form})

@login_required
def edit_category(request, category_id):
    category = get_object_or_404(Categories, pk=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            updated_category = form.save()
            messages.success(request, 'Категория успешно обновлена!')
            return redirect('category_detail', category_id=category.id)
    else:
        form = CategoryForm(instance=category)
    return render(request, 'main/add_categories.html', {
        'form': form,
        'category': category
    })
@login_required
def delete_category(request, category_id):
    category = get_object_or_404(Categories, pk=category_id)
    category.delete()
    messages.success(request, 'Категория успешно удалена!')
    return redirect('categories')


def category_detail(request, category_id):
    category = get_object_or_404(Categories, pk=category_id)
    courses_in_category = Courses.objects.filter(category_id=category_id)
    return render(request, 'main/category_detail.html', {
        'category': category,
        'courses': courses_in_category
    })


def categories(request):
    all_categories = Categories.objects.annotate(
        course_count=Count('courses')
    ).order_by('category_name')
    return render(request, 'main/categories.html', {
        'categories': all_categories
    })


def index(request):
    courses_list = Courses.objects.all().order_by('-start_date')[:8]
    popular_categories = Categories.objects.annotate(
        course_count=Count('courses')
    ).order_by('-course_count')[:5]
    return render(request, "main/index.html", {
        'courses': courses_list,
        'popular_categories': popular_categories
    })


@login_required
def reports(request):
    global period_form, category_form
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


@login_required
def add_course(request, course_id):
    if course_id == 0:
        if request.method == 'POST':
            form = CourseForm(request.POST, request.FILES)  # Добавьте request.FILES для обработки изображений
            if form.is_valid():
                course = form.save(commit=False)
                course.user_id = request.user
                course.save()
                messages.success(request, 'Курс успешно добавлен!')
                return redirect('course_detail', course_id=course.id)  # Перенаправляем на страницу курса
        else:
            form = CourseForm()
    else:
        course = get_object_or_404(Courses, id=course_id)
        if request.method == 'POST':
            form = CourseForm(request.POST, request.FILES, instance=course)  # Добавьте request.FILES
            if form.is_valid():
                course = form.save()
                messages.success(request, 'Курс успешно изменён!')
                return redirect('course_detail', course_id=course.id)  # Перенаправляем на страницу курса
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
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()

    report_data = Courses.objects.filter(
        start_date__range=(start_date_obj, end_date_obj)
    ).annotate(
        lessons_count=Count('lessons')
    ).select_related('user_id').order_by('start_date')

    for course in report_data:
        course.duration_days = (course.end_date - course.start_date).days

    return render(request, 'main/period_report_result.html', {
        'report_data': report_data,
        'start_date': start_date,
        'end_date': end_date,
        'title': _('Отчет за выбранный период')
    })


def category_report(request, category_id):
    category = Categories.objects.get(id=category_id)
    report_data = Courses.objects.filter(
        category_id=category
    ).annotate(
        duration=ExpressionWrapper(
            F('end_date') - F('start_date'),
            output_field=DurationField()
        ),
        lessons_count=Count('lessons')
    ).select_related('user_id').order_by('start_date')

    return render(request, 'main/category_report_result.html', {
        'report_data': report_data,
        'category': category,
        'title': _('Отчет по категории')
    })


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
    print("Удаление курса:", course_id)  # Проверка
    course = get_object_or_404(Courses, id=course_id)
    course.delete()
    print("Курс удалён!")  # Проверка
    return redirect('courses')


@login_required
def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lessons, pk=lesson_id)
    course_id = lesson.course_id.id
    lesson.delete()
    messages.success(request, 'Урок успешно удален!')
    return redirect('course_detail', course_id=course_id)


from django.db.models import Count


def home(request):
    courses = Courses.objects.all().order_by('-start_date')

    popular_categories = Categories.objects.annotate(
        course_count=Count('courses')
    ).order_by('-course_count')[:5]

    return render(request, 'main/index.html', {
        'courses': courses,
        'popular_categories': popular_categories
    })


def export_category_report(request, category_id, format):
    category = Categories.objects.get(id=category_id)
    report_data = Courses.objects.filter(
        category_id=category
    ).annotate(
        lessons_count=Count('lessons')
    ).select_related('user_id', 'category_id').order_by('start_date')

    for course in report_data:
        course.duration_days = (course.end_date - course.start_date).days

    if format == 'xlsx':
        return export_to_excel(report_data, f'report_category_{category_id}')
    elif format == 'pdf':
        return export_to_pdf(request, 'main/category_report_result.html',
                             {'report_data': report_data, 'category': category},
                             f'report_category_{category_id}.pdf')


def export_period_report(request, start_date, end_date, format):
    report_data = Courses.objects.filter(
        start_date__gte=start_date,
        end_date__lte=end_date
    ).annotate(
        lessons_count=Count('lessons')
    ).select_related('user_id', 'category_id').order_by('start_date')

    # Add duration calculation manually
    for course in report_data:
        course.duration_days = (course.end_date - course.start_date).days

    if format == 'xlsx':
        return export_to_excel(report_data, f'report_period_{start_date}_{end_date}')
    elif format == 'pdf':
        return export_to_pdf(request, 'main/period_report_result.html',
                             {'report_data': report_data,
                              'start_date': start_date,
                              'end_date': end_date},
                             f'report_period_{start_date}_{end_date}.pdf')


def export_to_excel(queryset, filename):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'

    wb = Workbook()
    ws = wb.active
    ws.title = "Report"

    # Заголовки
    headers = ['Курс', 'Категория', 'Дата начала', 'Дата окончания', 'Длительность (дни)', 'Уроков']
    ws.append(headers)

    # Данные
    for item in queryset:
        ws.append([
            item.course_name,
            item.category_id.category_name,
            item.start_date.strftime('%d.%m.%Y'),
            item.end_date.strftime('%d.%m.%Y'),
            (item.end_date - item.start_date).days,  # Calculate duration directly
            item.lessons_count
        ])

    wb.save(response)
    return response


def export_to_pdf(request, template_name, context, filename):
    template = get_template(template_name)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Указываем кодировку UTF-8 и дополнительные параметры для корректного отображения кириллицы
    pisa_status = pisa.CreatePDF(
        html,
        dest=response,
        encoding='UTF-8',
        link_callback=None,
        show_error_as_pdf=True
    )

    if pisa_status.err:
        return HttpResponse('Ошибка при создании PDF: ' + str(pisa_status.err))
    return response
