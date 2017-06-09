from django.contrib import auth
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View

from cars.models import Reregestration
from .models import Inspector, Inspection

class IndexView(View):
    def get(self, request):
        iin = request.GET.get('iin')
        inspections = []
        if iin:
            inspections = Reregestration.objects.filter(buyer='IIN' + iin, inspection__is_success=False)
        elif request.user.is_authenticated:
            inspector = Inspector.objects.get(user=request.user)
            inspections = Reregestration.objects.filter(inspection__center=inspector.center, inspection__is_success=False)
        return render(request, 'controller/index.html', {'inspections': inspections})

    def post(self, request):
        if not request.user:
            return HttpResponse(401)
        inspection = Inspection.objects.get(id=request.POST.get('id'))
        inspector = request.user.inspector
        inspection.inspector = request.user.inspector
        inspection.is_success = True
        inspection.save()
        inspection.reregestration.car.user = inspection.reregestration.buyer
        inspection.reregestration.car.save()
        inspection.reregestration.is_number_received = True
        inspection.reregestration.save()
        inspections = Reregestration.objects.filter(inspection__center=inspector.center, inspection__is_success=False)
        return render(request, 'controller/index.html', {'inspections': inspections})



def login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = auth.authenticate(request, username=username, password=password)
    if user is not None:
        auth.login(request, user)
    return redirect('/controller')


def logout(request):
    return redirect('/controller')
