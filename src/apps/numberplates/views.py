from django.contrib.humanize.templatetags.humanize import intcomma
from django.http import JsonResponse

from carbase.decorators import login_required

from . import api


def get_number_plates(owner_id=None, center_id=None, limit=None, offset=None, search_pattern=None):
    if owner_id is not None:
        return api.get_owner_number_plates(owner_id=owner_id)

    return api.get_number_plates(
        center_id=center_id,
        limit=limit,
        offset=offset,
        search_pattern=search_pattern
    )


def set_number_plate_owner(plate_number, user_id):
    return api.set_owner(plate_number=plate_number, user_id=user_id)


@login_required
def get_numbers(request):
    numbers = get_number_plates(search_pattern=request.GET.get('q'))
    numbers_list = []
    for number in numbers:
        numbers_list.append({
            'id': number.id,
            'digits': number.digits,
            'characters': number.characters,
            'region': number.region,
            'price': intcomma(number.get_price())
        })
    return JsonResponse(numbers_list, safe=False)
