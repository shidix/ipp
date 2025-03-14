from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from datetime import datetime

#import whisper

from ipp.decorators import group_required_pwa
from ipp.commons import user_in_group, get_or_none, get_param
from gestion.models import Employee, Client, Service, ServiceStatus, ServiceImage, Note


@group_required_pwa("employees")
def index(request):
    try:
        return redirect(reverse('pwa-employee'))
    except:
        return redirect(reverse('pwa-login'))

def pin_login(request):
    CONTROL_KEY = "SZRf2QMpIfZHPEh0ib7YoDlnnDp5HtjDqbAw"
    msg = ""  
    if request.method == "POST":
        context =  {}
        msg = "Operación no permitida"
        pin = request.POST.get('pin', None)
        control_key = request.POST.get('control_key', None)
        if pin != None and control_key != None:
            if control_key == CONTROL_KEY:
                try:
                    emp = get_or_none(Employee, pin, "pin")
                    login(request, emp.user)
                    request.session['pwa_app_session'] = True
                    return redirect(reverse('pwa-employee'))
                except Exception as e:
                    msg = "Pin no válido"
                    print(e)
            else:
                msg = "Bad control"
    return render(request, "pwa-login.html", {'msg': msg})

def pin_logout(request):
    logout(request)
    return redirect(reverse('pwa-login'))

'''
    EMPLOYEES
'''
@group_required_pwa("employees")
def employee_home(request):
    context = {"obj": request.user.employee}
    if user_in_group(request.user, "admins"):
        context["notes_list"] = Note.objects.filter(deleted=False)
    return render(request, "pwa/employees/home.html", context)

@group_required_pwa("employees")
def employee_service(request, obj_id):
    service = get_or_none(Service, obj_id)
    return render(request, "pwa/employees/service.html", {"obj": service, "status_list": ServiceStatus.objects.all()})

@group_required_pwa("employees")
def employee_service_save(request):
    service = get_or_none(Service, get_param(request.POST, "service"))
    status = get_or_none(ServiceStatus, get_param(request.POST, "status"))
    service.status = status
    service.emp_notes = get_param(request.POST, "emp_notes")
    service.save()
    if "img" in request.FILES and request.FILES["img"] != "":
        ServiceImage.objects.create(service=service, image=request.FILES["img"])
    return redirect(reverse("pwa-employee-service", kwargs={'obj_id': service.id}))

@group_required_pwa("employees")
def employee_note(request):
    return render(request, "pwa/employees/note.html", {})

@group_required_pwa("employees")
def employee_note_save(request):
    concept = get_param(request.POST, "concept")
    audio = None
    if "audio" in request.FILES and request.FILES["audio"] != "":
        audio = request.FILES["audio"]
        #model = whisper.load_model("base")
        #concept = model.transcribe(audio, language="es")
    if concept != "" or audio != None:
        note = Note.objects.create(concept=concept, audio=audio)
    return redirect(reverse('pwa-employee'))

