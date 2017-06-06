from django.shortcuts import render, redirect
from django.views import View
from .api import get_cars_by_iin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, QueryDict

from .models import Reregestration, Car

class CarsView(View):
    def get(self, request):
        print(not request.session.get('user_serialNumber'))
        if not request.session.get('user_serialNumber'):
            return redirect('/')
        cars = get_cars_by_iin(request.session.get('user_serialNumber'))
        reregistrations = Reregestration.objects.filter(buyer=request.session.get('user_serialNumber'))
        return render(request, 'cars/list.html', {'cars': cars, 'reregistrations': reregistrations})


@method_decorator(csrf_exempt, name='dispatch')
class AgreementView(View):
    def post(self, request):
        car_id = request.POST.get('car_id')
        car = Car.objects.get(id=car_id)
        seller = request.session.get('user_serialNumber')
        buyer = request.POST.get('buyer')
        exist_registrations = Reregestration.objects.filter(car=car, buyer=buyer, seller=seller)
        if (exist_registrations):
           reregestration = exist_registrations[0]
        else:
           reregestration = Reregestration.objects.create(car=car, buyer=buyer, seller=seller)
        return JsonResponse({'reregistration_id': reregestration.id})

    def put(self, request):
        request.PUT = QueryDict(request.body)
        reregistration_id = request.PUT.get('reregistrationId')
        reregistration = Reregestration.objects.get(id=reregistration_id)
        if request.PUT.get('seller_sign'):
            reregistration.seller_sign = request.PUT.get('seller_sign')
            reregistration.amount = request.PUT.get('amount')
        if request.PUT.get('buyer_sign'):
            reregistration.buyer_sign = request.PUT.get('buyer_sign')
        if request.PUT.get('is_tax_paid'):
            reregistration.is_tax_paid = True
        reregistration.save()
        return JsonResponse({'reregistration_id': reregistration.id})
