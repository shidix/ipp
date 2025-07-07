from django.conf import settings
from django.contrib.auth.models import User, Group
from django.db import models
from django.utils.translation import gettext_lazy as _ 

import datetime


'''
    EMPLOYEE
'''
class Employee(models.Model):
    pin = models.CharField(max_length=20, verbose_name = _('PIN'), default="")
    dni = models.CharField(max_length=20, verbose_name = _('DNI'), default="")
    name = models.CharField(max_length=200, verbose_name = _('Razón Social'), default="")
    phone = models.CharField(max_length=20, verbose_name = _('Teléfono de contacto'), null=True, default = '0000000000')
    email = models.EmailField(verbose_name = _('Email de contacto'), default="", null=True)
    user = models.OneToOneField(User, verbose_name='Usuario', on_delete=models.CASCADE, null=True, blank=True, related_name='employee')

    def __str__(self):
        return self.name

    def save_user(self):
        if self.user == None:
            self.user = User.objects.create_user(username=self.email, email=self.email)
            self.save()
            group = Group.objects.get(name='employees') 
            group.user_set.add(self.user)
        else:
            self.user.username = self.email
            self.user.save()

    def worked_time(self, ini_date, end_date):
        idate = "{} 00:00".format(ini_date)
        edate = "{} 23:59".format(end_date)
        item_list = self.assistances.filter(ini_date__gte=idate, end_date__lte=edate)
        #item_list = self.assistances.filter(ini_date__gte=ini_date, end_date__lte=end_date)
        hours = 0
        minutes = 0
        for item in item_list:
            if item.finish:
                diff = item.end_date - item.ini_date
                days, seconds = diff.days, diff.seconds
                hours += seconds // 3600
                minutes += (seconds % 3600) // 60
                #hours = days * 24 + seconds // 3600
                #seconds = seconds % 60
        if minutes > 59:
            hours += minutes // 60
            minutes = minutes % 60
        return hours, minutes
        #return "{}:{}".format(hours, minutes) 
        #return "{} horas y {}  minutos".format(hours, minutes) 

    def services_active(self):
        return self.services.filter(deleted=False)

    class Meta:
        verbose_name = _('Empleado')
        verbose_name_plural = _('Empleados')

'''
    CLIENTS
'''
def upload_form_qr(instance, filename):
    ascii_filename = str(filename.encode('ascii', 'ignore'))
    instance.filename = ascii_filename
    folder = "clients/qr/%s" % (instance.id)
    return '/'.join(['%s' % (folder), datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ascii_filename])

class Client(models.Model):
    inactive = models.BooleanField(default=False, verbose_name=_('Desactivado'));
    name = models.CharField(max_length=200, verbose_name = _('Razón Social'), default="")
    phone = models.CharField(max_length=12, verbose_name = _('Teléfono de contacto'), null=True, default='0000000000')
    email = models.EmailField(verbose_name = _('Email de contacto'), default="", null=True)
    address = models.TextField(verbose_name = _('Dirección'), null=True, default='')
    observations = models.TextField(verbose_name = _('Observaciones'), null=True, default='')
    qr = models.ImageField(upload_to=upload_form_qr, blank=True, verbose_name="QR", help_text="Select file to upload")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Empleado')
        verbose_name_plural = _('Empleados')

'''
    SERVICES
'''
class ServiceType(models.Model):
    code = models.CharField(max_length=50, verbose_name = _('Código'), default="")
    name = models.CharField(max_length=255, verbose_name = _('Nombre'), default="")

    class Meta:
        verbose_name = _('Tipo de servicio')
        verbose_name_plural = _('Tipos de servicios')

class ServiceStatus(models.Model):
    code = models.CharField(max_length=50, verbose_name = _('Código'), default="")
    name = models.CharField(max_length=255, verbose_name = _('Nombre'), default="")
    color = models.CharField(max_length=10, verbose_name = _('Color'), default="", blank=True)

    class Meta:
        verbose_name = _('Estado')
        verbose_name_plural = _('Estados')

class Service(models.Model):
    deleted = models.BooleanField(default=False, verbose_name=_('Desactivado'), null=True);
    charged = models.BooleanField(default=False, verbose_name=_('Cobrado'));
    ini_date = models.DateTimeField(default=datetime.datetime.now(), null=True, verbose_name=_('Inicio'))
    end_date = models.DateTimeField(default=datetime.datetime.now(), null=True, verbose_name=_('Fin'))
    notes = models.TextField(verbose_name = _('Notas'), null=True, default='')
    emp_notes = models.TextField(verbose_name = _('Notas del empleado'), null=True, default='')

    status = models.ForeignKey(ServiceStatus, verbose_name=_('Estado'), on_delete=models.SET_NULL, null=True)
    service_type = models.ForeignKey(ServiceType, verbose_name=_('Tipo de servicio'), on_delete=models.SET_NULL, null=True)
    client = models.ForeignKey(Client, verbose_name=_('Cliente'), on_delete=models.SET_NULL, null=True, related_name="services")
    employee = models.ForeignKey(Employee,verbose_name=_('Empleado'),on_delete=models.SET_NULL,null=True,related_name="services")

    class Meta:
        verbose_name = _('Servicio')
        verbose_name_plural = _('Servicios')

def upload_service_img(instance, filename):
    ascii_filename = str(filename.encode('ascii', 'ignore'))
    instance.filename = ascii_filename
    folder = "services/%s" % (instance.service.id)
    return '/'.join(['%s' % (folder), datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ascii_filename])


class ServiceImage(models.Model):
    image = models.ImageField(upload_to=upload_service_img, blank=True, verbose_name="Image", help_text="Select file to upload")
    service = models.ForeignKey(Service, verbose_name=_('Servicio'), on_delete=models.CASCADE, null=True, related_name="images")

    class Meta:
        verbose_name = _('Imagen del Servicio')
        verbose_name_plural = _('Imagenes de los Servicios')

'''
    NOTES
'''
def upload_note_audio(instance, filename):
    ascii_filename = str(filename.encode('ascii', 'ignore'))
    instance.filename = ascii_filename
    #folder = "notes/%s" % (instance.id)
    folder = "notes"
    return '/'.join(['%s' % (folder), datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ascii_filename])

class Note(models.Model):
    deleted = models.BooleanField(default=False, verbose_name=_('Desactivado'));
    date = models.DateTimeField(default=datetime.datetime.now(), null=True, verbose_name=_('Fecha'))
    concept = models.TextField(verbose_name = _('Notas'), null=True, default='')
    audio = models.FileField(upload_to=upload_note_audio, blank=True, verbose_name="Audio", help_text="Select file to upload")

    class Meta:
        verbose_name = _('Nota')
        verbose_name_plural = _('Notas')


