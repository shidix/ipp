from django.conf import settings
from django.core.files.base import ContentFile
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import os, csv

from ipp.decorators import group_required
from ipp.commons import get_float, get_or_none, get_param, get_session, set_session, show_exc, generate_qr, csv_export
from .models import Employee, Client, Service, ServiceType, ServiceStatus, Note

ACCESS_PATH="https://ipp.shidix.es/gestion/services/client/"


def init_session_date(request, key):
    #if not key in request.session:
    set_session(request, key, datetime.now().strftime("%Y-%m-%d"))

def get_services(request):
    value = get_session(request, "s_name")
    i_date = datetime.strptime("{} 00:00".format(get_session(request, "s_idate")), "%Y-%m-%d %H:%M")
    e_date = datetime.strptime("{} 23:59".format(get_session(request, "s_edate")), "%Y-%m-%d %H:%M")

    kwargs = {"ini_date__gte": i_date, "ini_date__lte": e_date}
    if value != "":
        kwargs["employee__name__icontains"] = value

    return Service.objects.filter(**kwargs).order_by("-ini_date")

@group_required("admins",)
def index(request):
    init_session_date(request, "s_idate")
    init_session_date(request, "s_edate")
    print(get_services(request))
    print(get_notes(request))
    return render(request, "index.html", {"item_list": get_services(request), "notes": get_notes(request)})

@group_required("admins",)
def services_list(request):
    return render(request, "services-list.html", {"item_list": get_services(request)})

@group_required("admins",)
def services_search(request):
    set_session(request, "s_name", get_param(request.GET, "s_name"))
    set_session(request, "s_idate", get_param(request.GET, "s_idate"))
    set_session(request, "s_edate", get_param(request.GET, "s_edate"))
    return render(request, "services-list.html", {"item_list": get_services(request)})

@group_required("admins",)
def services_form(request):
    obj = get_or_none(Service, get_param(request.GET, "obj_id"))
    type_list = ServiceType.objects.all()
    status_list = ServiceStatus.objects.all()
    client_list = Client.objects.all()
    employee_list = Employee.objects.all()
    context = {'obj':obj, 'type_list':type_list, 'status_list':status_list, 'client_list':client_list, 'employee_list':employee_list}
    return render(request, "services-form.html", context)

@group_required("admins",)
def services_form_save(request):
    obj = get_or_none(Service, get_param(request.GET, "obj_id"))
    if obj == None:
        obj = Service.objects.create()
    s_type = get_or_none(ServiceType, get_param(request.GET, "service_type"))
    status = get_or_none(ServiceStatus, get_param(request.GET, "status"))
    client = get_or_none(Client, get_param(request.GET, "client"))
    emp = get_or_none(Employee, get_param(request.GET, "employee"))

    obj.service_type = s_type
    obj.status = status
    obj.client = client
    obj.employee = emp
    obj.notes = get_param(request.GET, "notes")
    obj.save()
    return render(request, "services-list.html", {"item_list": get_services(request)})

@group_required("admins",)
def services_remove(request):
    obj = get_or_none(Service, request.GET["obj_id"])
    if obj != None:
        obj.delete()
    return render(request, "services-list.html", {"item_list": get_services(request)})

'''
    NOTES
'''
def get_notes(request, deleted=False):
    return Note.objects.filter(deleted=deleted)

@group_required("admins",)
def notes_list(request):
    deleted = True if get_param(request.GET, "deleted") == "True" else False
    return render(request, "notes/notes-list.html", {"notes": get_notes(request, deleted)})

@group_required("admins",)
def notes_search(request):
    return render(request, "notes/notes-list.html", {"notes": get_notes(request)})

@group_required("admins",)
def notes_form(request):
    obj = get_or_none(Note, get_param(request.GET, "obj_id"))
    return render(request, "notes/notes-form.html", {'obj': obj})

@group_required("admins",)
def notes_form_save(request):
    obj = get_or_none(Note, get_param(request.GET, "obj_id"))
    if obj == None:
        obj = Note.objects.create()
    obj.concept = get_param(request.GET, "concept")
    obj.save()
    return render(request, "notes/notes-list.html", {"notes": get_notes(request)})

@group_required("admins",)
def notes_remove(request):
    obj = get_or_none(Note, request.GET["obj_id"]) if "obj_id" in request.GET else None
    if obj != None:
        obj.delete()
    return render(request, "notes/notes-list.html", {"notes": get_notes(request)})

@group_required("admins",)
def notes_remove_soft(request):
    obj = get_or_none(Note, request.GET["obj_id"]) if "obj_id" in request.GET else None
    if obj != None:
        obj.deleted = True
        obj.save()
    return render(request, "notes/notes-list.html", {"notes": get_notes(request)})


'''
    EMPLOYEES
'''
def get_employees(request):
    search_value = get_session(request, "s_emp_name")
    filters_to_search = ["name__icontains",]
    full_query = Q()
    if search_value != "":
        for myfilter in filters_to_search:
            full_query |= Q(**{myfilter: search_value})
    return Employee.objects.filter(full_query)

@group_required("admins",)
def employees(request):
    init_session_date(request, "s_emp_idate")
    init_session_date(request, "s_emp_edate")
    return render(request, "employees/employees.html", {"items": get_employees(request)})

@group_required("admins",)
def employees_list(request):
    return render(request, "employees/employees-list.html", {"items": get_employees(request)})

@group_required("admins",)
def employees_search(request):
    set_session(request, "s_emp_name", get_param(request.GET, "s_emp_name"))
    set_session(request, "s_emp_idate", get_param(request.GET, "s_emp_idate"))
    set_session(request, "s_emp_edate", get_param(request.GET, "s_emp_edate"))
    return render(request, "employees/employees-list.html", {"items": get_employees(request)})

@group_required("admins",)
def employees_form(request):
    obj_id = get_param(request.GET, "obj_id")
    obj = get_or_none(Employee, obj_id)
    if obj == None:
        obj = Employee.objects.create()
    return render(request, "employees/employees-form.html", {'obj': obj})

@group_required("admins",)
def employees_remove(request):
    obj = get_or_none(Employee, request.GET["obj_id"]) if "obj_id" in request.GET else None
    if obj != None:
        if obj.user != None:
            obj.user.delete()
        obj.delete()
    return render(request, "employees/employees-list.html", {"items": get_employees(request)})

@group_required("admins",)
def employees_save_email(request):
    try:
        obj = get_or_none(Employee, get_param(request.GET, "obj_id"))
        obj.email = get_param(request.GET, "value")
        obj.save()
        obj.save_user()
        return HttpResponse("Saved!")
    except Exception as e:
        return HttpResponse("Error: {}".format(e))

@group_required("admins",)
def employees_export(request):
    header = ['Nombre', 'Teléfono', 'Email', 'PIN', 'DNI', 'Horas trabajadas', 'Minutos trabajados']
    values = []
    items = get_employees(request)
    for item in items:
        hours, minutes = item.worked_time(request.session["s_emp_idate"], request.session["s_emp_edate"])
        row = [item.name, item.phone, item.email, item.pin, item.dni, hours, minutes]
        values.append(row)
    return csv_export(header, values, "empleados")

@group_required("admins",)
def employees_import(request):
    f = request.FILES["file"]
    lines = f.read().decode('latin-1').splitlines()
    i = 0
    for line in lines:
        if i > 0:
            l = line.split(";")
            #print(l)
            name = "{} {}".format(l[1], l[0])
            phone = l[2]
            email = l[7]
            dni = l[6]
            obj, created = Employee.objects.get_or_create(pin=dni, dni=dni, name=name, phone=phone, email=email)
            obj.save_user()
        i += 1
    return redirect("employees")

'''
    CLIENTS
'''
def get_clients(request):
    search_value = get_session(request, "s_cli_name")
    filters_to_search = ["name__icontains",]
    full_query = Q()
    if search_value != "":
        for myfilter in filters_to_search:
            full_query |= Q(**{myfilter: search_value})
    return Client.objects.filter(full_query).order_by("-id")[:50]

@group_required("admins",)
def clients(request):
    return render(request, "clients/clients.html", {"items": get_clients(request)})

@group_required("admins",)
def clients_list(request):
    return render(request, "clients/clients-list.html", {"items": get_clients(request)})

@group_required("admins",)
def clients_search(request):
    set_session(request, "s_cli_name", get_param(request.GET, "s_cli_name"))
    return render(request, "clients/clients-list.html", {"items": get_clients(request)})

@group_required("admins",)
def clients_form(request):
    obj_id = get_param(request.GET, "obj_id")
    obj = get_or_none(Client, obj_id)
    new = False
    if obj == None:
        obj = Client.objects.create()
        url = "{}{}".format(ACCESS_PATH, obj.id)
        path = os.path.join(settings.BASE_DIR, "static", "images", "logo-asistencia-canaria.jpg")
        img_data = ContentFile(generate_qr(url, path))
        obj.qr.save('qr_{}.png'.format(obj.id), img_data, save=True)
        new = True
    return render(request, "clients/clients-form.html", {'obj': obj, 'new': new})

@group_required("admins",)
def clients_remove(request):
    obj = get_or_none(Client, request.GET["obj_id"]) if "obj_id" in request.GET else None
    if obj != None:
        obj.qr.delete(save=True)
        obj.delete()
    return render(request, "clients/clients-list.html", {"items": get_clients(request)})

@group_required("admins",)
def clients_print_all_qr(request):
    return render(request, "clients/clients-print-all-qr.html", {"item_list": Client.objects.filter(inactive=False)})

@group_required("admins",)
def clients_print_qr(request, obj_id):
    return render(request, "clients/clients-print-qr.html", {"obj": get_or_none(Client, obj_id)})

@group_required("admins",)
def clients_services(request, obj_id):
    return render(request, "clients/clients-services.html", {"obj": get_or_none(Client, obj_id)})

'''
    Speech to text
'''
@csrf_exempt
def set_note_concept(request):
    #print("--1--")
    #print(request.POST)
    token = get_param(request.POST, "token")
    text = get_param(request.POST, "text")
    note = get_or_none(Note, get_param(request.POST, "note"))
    if token == "1234":
        #print("--2--")
        #print(text)
        note.concept = text
        note.save()
    return HttpResponse("")

