from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  # Основные пути
                  path('', views.index, name='home'),
                  path('login/', views.login, name='login'),
                  path('logout/', LogoutView.as_view(next_page='home'), name='logout'),

                  # Пути для работы с категориями
                  path('categories/', views.categories, name='categories'),
                  path('category/<int:category_id>/', views.category_detail, name='category_detail'),
                  path('category/add/', views.add_category, name='add_category'),
                  path('category/edit/<int:category_id>/', views.edit_category, name='edit_category'),
                  path('category/delete/<int:category_id>/', views.delete_category, name='delete_category'),

                  # Пути для работы с курсами
                  path('courses/', views.courses, name='courses'),
                  path('course/<int:course_id>/', views.course_detail, name='course_detail'),
                  path('add_course/<int:course_id>/', login_required(views.add_course), name='add_course'),
                  path('delete_course/<int:course_id>/', login_required(views.delete_course), name='delete_course'),

                  # Пути для работы с уроками
                  path('add_lesson/<int:lesson_id>/', login_required(views.add_lesson), name='add_lesson'),
                  path('delete_lesson/<int:lesson_id>/', login_required(views.delete_lesson), name='delete_lesson'),

                  # Пути для отчетов
                  path('reports/', login_required(views.reports), name='reports'),
                  path('reports/category/<int:category_id>/', login_required(views.category_report),
                       name='category_report'),
                  path('reports/period/<str:start_date>/<str:end_date>/', login_required(views.period_report),
                       name='period_report'),

                  # Дополнительные пути
                  path('registration_email/', views.registration_email, name='registration_email'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)