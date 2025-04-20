from django.contrib import admin

from .models import Users
from .models import Courses
from .models import Categories
from .models import Lessons

admin.site.register(Users)
admin.site.register(Courses)
admin.site.register(Categories)
admin.site.register(Lessons)
