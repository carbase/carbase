from django.contrib import auth
from django.db.models import Q
from django.http import JsonResponse, QueryDict
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from .models import Inspector, Inspection


class IndexView(View):
    def get(self, request):
        template_data = {
            'is_allower': request.user.username.startswith('all'),
            'is_revisor': request.user.username.startswith('rev'),
        }
        inspections = []
        if request.user.is_authenticated:
            inspector = Inspector.objects.get(user=request.user)
            q = request.GET.get('q')
            if q:
                inspections = Inspection.objects.filter(
                    Q(reregistration__buyer__icontains=q) |
                    Q(reregistration__seller__icontains=q) |
                    Q(reregistration__car__number__icontains=q) |
                    Q(reregistration__car__vin_code__icontains=q) |
                    Q(reregistration__car__manufacturer__icontains=q) |
                    Q(reregistration__car__model__icontains=q) |
                    Q(deregistration__car__user__icontains=q) |
                    Q(deregistration__car__number__icontains=q) |
                    Q(deregistration__car__vin_code__icontains=q) |
                    Q(deregistration__car__manufacturer__icontains=q) |
                    Q(deregistration__car__model__icontains=q)
                )
            else:
                inspections = Inspection.objects.filter(center=inspector.center).exclude(is_success=True)
        template_data['inspections'] = inspections
        return render(request, 'controller/index.html', template_data)


def login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = auth.authenticate(request, username=username, password=password)
    if user is not None:
        auth.login(request, user)
    return redirect('/controller')


def logout(request):
    auth.logout(request)
    return redirect('/controller')


@method_decorator(csrf_exempt, name='dispatch')
class InspectionView(View):
    def put(self, request):
        request.PUT = QueryDict(request.body)
        inspection = Inspection.objects.get(id=request.PUT.get('id'))
        if request.PUT.get('is_prelimenary_success'):
            inspection.is_prelimenary_success = bool(int(request.PUT.get('is_prelimenary_success')))
            inspection.allower = request.user.inspector
        if request.PUT.get('prelimenary_result'):
            inspection.prelimenary_result = request.PUT.get('prelimenary_result')
        if request.PUT.get('is_revision_success'):
            inspection.is_revision_success = bool(int(request.PUT.get('is_revision_success')))
            inspection.revisor = request.user.inspector
        if request.PUT.get('revision_result'):
            inspection.revision_result = request.PUT.get('revision_result')
        if request.PUT.get('is_success'):
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
            inspection.is_success = bool(int(request.PUT.get('is_success')))
        if request.PUT.get('result'):
            inspection.result = request.PUT.get('result')

        inspection.save()
        return JsonResponse({'result': 'success'})
