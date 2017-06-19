from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from .api import set_owner
from .models import NumberPlate

from carbase.decorators import login_required


@method_decorator(login_required, name='dispatch')
class NumberPlatesView(View):
    def get(self, request):
        template_data = {
            'numberplates': NumberPlate.objects.filter(is_sold=False),
        }
        return render(request, 'numberplates/list.html', template_data)


@method_decorator(login_required, name='dispatch')
class PersonNumberPlatesView(View):
    def get(self, request):
        person_id = request.session.get('user_serialNumber')
        template_data = {
            'numberplates': NumberPlate.objects.filter(owner_id=person_id),
        }
        return render(request, 'numberplates/person-list.html', template_data)

    def post(self, request):
        number_id = request.POST.get('number_id')
        buyer_id = request.session.get('user_serialNumber')
        owner_id = request.POST.get('owner_id')
        number, msg = set_owner(number_id=number_id, buyer_id=buyer_id, owner_id=owner_id)
        if not number:
            return JsonResponse({
                'numberplate': number.id,
                'message': msg,
            })
        else:
            return JsonResponse({
                'numberplate': 0,
                'message': msg,
            })
