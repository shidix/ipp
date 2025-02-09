from django.contrib import admin
from .models import *

class ServiceStatusAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'color')
admin.site.register(ServiceStatus, ServiceStatusAdmin)

class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
admin.site.register(ServiceType, ServiceTypeAdmin)

class ServiceImageAdmin(admin.ModelAdmin):
    list_display = ('service', 'image')
admin.site.register(ServiceImage, ServiceImageAdmin)

