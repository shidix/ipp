from django.urls import path
from pwa import views


urlpatterns = [
    path('', views.index, name="pwa-home"),
    path('home/', views.index, name="pwa-home"),
    path('login/', views.pin_login, name="pwa-login"),
    path('logoff/', views.pin_logout, name="pwa-logout"),

    # EMPLOYEES
    path('employee/', views.employee_home, name="pwa-employee"),
    path('employee/service/<int:obj_id>/', views.employee_service, name="pwa-employee-service"),
    path('employee/service/save/', views.employee_service_save, name="pwa-employee-service-save"),
]

