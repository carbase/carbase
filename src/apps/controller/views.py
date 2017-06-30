from django.contrib import auth
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View

from cars.models import Reregistration, Deregistration
from .models import Inspector, Inspection


class IndexView(View):
    def get(self, request):
        iin = request.GET.get('iin')
        reregistrations = []
        deregistrations = []
        if iin:
            reregistrations = Reregistration.objects.filter(buyer='IIN' + iin, inspection__is_success=False)
            deregistrations = Deregistration.objects.filter(car__owner='IIN' + iin, inspection__is_success=False)
        elif request.user.is_authenticated:
            inspector = Inspector.objects.get(user=request.user)
            reregistrations = Reregistration.objects.exclude(inspection__is_success=True)
            reregistrations.filter(inspection__center=inspector.center)
            deregistrations = Deregistration.objects.exclude(inspection__is_success=True)
            deregistrations.filter(inspection__center=inspector.center)
        template_data = {'reregistrations': reregistrations, 'deregistrations': deregistrations}
        return render(request, 'controller/index.html', template_data)

    def post(self, request):
        if not request.user.username.startswith('mvd'):
            return HttpResponse(401)
        inspection = Inspection.objects.get(id=request.POST.get('id'))
        inspector = request.user.inspector
        inspection.inspector = request.user.inspector
        inspection.is_success = True
        inspection.save()
        if inspection.reregistration:
            inspection.reregistration.car.user = inspection.reregistration.buyer
            inspection.reregistration.car.number = inspection.reregistration.number
            inspection.reregistration.car.is_registred = True
            inspection.reregistration.car.save()
            inspection.reregistration.is_number_received = True
            inspection.reregistration.save()
        if inspection.deregistration:
            inspection.deregistration.car.is_registred = False
            inspection.deregistration.car.save()
            inspection.deregistration.is_success = True
            inspection.deregistration.save()

        reregistrations = Reregistration.objects.exclude(inspection__is_success=True)
        reregistrations.filter(inspection__center=inspector.center)
        deregistrations = Deregistration.objects.exclude(inspection__is_success=True)
        deregistrations.filter(inspection__center=inspector.center)
        template_data = {'reregistrations': reregistrations, 'deregistrations': deregistrations}
        return render(request, 'controller/index.html', template_data)


def login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = auth.authenticate(request, username=username, password=password)
    if user is not None:
        auth.login(request, user)
    return redirect('/controller')


def logout(request):
    return redirect('/controller')
