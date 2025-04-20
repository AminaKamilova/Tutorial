from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, login, password=None, **extra_fields):
        if not login:
            raise TypeError('Users must have a login.')

        user = self.model(login=login, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        return self.create_user(login, password, **extra_fields)


class Users(AbstractBaseUser, PermissionsMixin):
    user_name = models.CharField(max_length=45)
    login = models.CharField(max_length=45, unique=True)
    password = models.CharField(max_length=45)
    user_email = models.CharField(max_length=45, unique=True)

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['user-name', 'user_email']

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Categories(models.Model):
    category_name = models.CharField(max_length=45)
    description = models.TextField()

    REQUIRED_FIELDS = ['category_name']

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.category_name


class Courses(models.Model):
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    course_name = models.CharField(max_length=45)
    start_date = models.DateField()
    end_date = models.DateField()
    category_id = models.ForeignKey(Categories, on_delete=models.CASCADE)

    REQUIRED_FIELDS = ['user_id', 'course_name', 'start_date',
                       'end_date', 'category_id']

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
    
    def __str__(self):
        return self.course_name


class Lessons(models.Model):
    course_id = models.ForeignKey(Courses, on_delete=models.CASCADE, related_name='lessons')
    course_name = models.CharField(max_length=45)
    lesson_num = models.IntegerField()
    description = models.TextField()

    REQUIRED_FIELDS = ['course_id', 'course_name', 'lesson_num']

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'




