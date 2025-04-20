from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

urlpatterns = [


    path('categories', views.categories, name='categories'),
    path('add_category', login_required(views.add_category), name='add_category'),
    path('reports/category/<int:category_id>', login_required(views.category_report), name='category_report'),
    path('logout', views.logout, name='logout'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('', views.index, name='home'),
    path('courses/', views.courses, name='courses'),
    path('reports', login_required(views.reports), name='reports'),
    path('reports/period/<str:start_date>&<str:end_date>', login_required(views.period_report), name='period_report'),
    path('registration_email', views.registration_email, name='registration_email'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('add_course/<int:course_id>', login_required(views.add_course), name='add_course'),
    path('add_lesson/<int:lesson_id>', login_required(views.add_lesson), name='add_lesson'),
    path('delete_course/<int:course_id>', login_required(views.delete_course), name='delete_course'),
    path('delete_lesson/<int:lesson_id>', login_required(views.delete_lesson), name='delete_lesson'),
    path('login', views.login, name='login')
]