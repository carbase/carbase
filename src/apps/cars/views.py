from django.shortcuts import render, redirect
from django.views import View
from .api import get_cars_by_iin

class CarsView(View):
    def get(self, request):
        print(not request.session.get('user_serialNumber'))
        if not request.session.get('user_serialNumber'):
            return redirect('/')
        cars = get_cars_by_iin(request.session.get('user_serialNumber'))
        return render(request, 'cars/list.html', {'cars': cars})
