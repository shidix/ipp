from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from datetime import datetime

import subprocess
import threading

from ipp.decorators import group_required_pwa
from ipp.commons import user_in_group, get_or_none, get_param
from gestion.models import Employee, Client, Service, ServiceStatus, ServiceType, ServiceImage, Note


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
    #context = {"obj": request.user.employee}
    #if user_in_group(request.user, "admins"):
    #    context["notes_list"] = Note.objects.filter(deleted=False)
    return render(request, "pwa/employees/home.html", {"obj": request.user.employee})

@group_required_pwa("employees")
def employee_service(request, obj_id):
    service = get_or_none(Service, obj_id)
    return render(request, "pwa/employees/service.html", {"obj": service, "status_list": ServiceStatus.objects.all()})

@group_required_pwa("employees")
def employee_service_new(request, obj_id=""):
    obj = get_or_none(Service, obj_id)
    type_list = ServiceType.objects.all()
    status_list = ServiceStatus.objects.all()
    client_list = Client.objects.all()
    employee_list = Employee.objects.all()
    context = {'obj':obj, 'type_list':type_list, 'status_list':status_list, 'client_list':client_list, 'employee_list':employee_list}
    return render(request, "pwa/employees/service_new.html", context)

@group_required_pwa("employees")
def employee_service_new_save(request):
    s_type = get_or_none(ServiceType, get_param(request.POST, "service_type"))
    status = get_or_none(ServiceStatus, get_param(request.POST, "status"))
    client = get_or_none(Client, get_param(request.POST, "client"))
    emp = get_or_none(Employee, get_param(request.POST, "employee"))
    notes = get_param(request.POST, "notes")
    #charged = get_param(request.GET, "charged")

    obj = get_or_none(Service, get_param(request.POST, "obj_id"))
    if obj == None:
        obj = Service.objects.create()
    obj.service_type = s_type
    obj.status = status
    obj.client = client
    obj.employee = emp
    obj.notes = notes
    obj.save()
    if "img" in request.FILES and request.FILES["img"] != "":
        ServiceImage.objects.create(service=obj, image=request.FILES["img"])
    #obj.charged = True if charged != "" else False
    return redirect(reverse("pwa-employee-service-new", kwargs={'obj_id': obj.id}))

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
def employee_notes(request):
    context = {"obj": request.user.employee}
    if user_in_group(request.user, "admins"):
        context["notes_list"] = Note.objects.filter(deleted=False)
    return render(request, "pwa/employees/notes.html", context)

@group_required_pwa("employees")
def employee_note(request):
    return render(request, "pwa/employees/note.html", {})

def transcribe_audio(file):
    subprocess.run(["python", "transcribir.py", file])

@group_required_pwa("employees")
def employee_note_save(request):
    concept = get_param(request.POST, "concept")
    audio = None
    if "audio" in request.FILES and request.FILES["audio"] != "":
        audio = request.FILES["audio"]
        concept = "Esperando traducción de audio..."
    if concept != "" or audio != None:
        note = Note.objects.create(concept=concept, audio=audio)
        if "audio" in request.FILES and request.FILES["audio"] != "":
            t = threading.Thread(target=transcribe_audio, args=[note.audio.url], daemon=True)
            t.start()
    return redirect(reverse('pwa-employee'))

