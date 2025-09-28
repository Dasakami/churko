
from django.contrib import admin
from .models import *

class DistrictAdmin(admin.ModelAdmin):
    list_filter = ['difficulty', 'status', 'is_active']
    search_fields = ['short_desc', 'name']

class TaskAdmin(admin.ModelAdmin):
    search_fields = ['title']

class LevelAdmin(admin.ModelAdmin):
    list_filter = ['difficulty', 'status', 'is_active', 'district']
    search_fields = ['name', 'description']

admin.site.register(District, DistrictAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Level, LevelAdmin)