from django.contrib import admin

from .models import *

# Register your models here.
admin.site.register(Goal)
admin.site.register(Tag)
admin.site.register(ActivityTag)
admin.site.register(AchievementReport)