from django.core.exceptions import ObjectDoesNotExist

from .models import NumberPlate


def set_owner(number_id, buyer_id):
    try:
        number = NumberPlate.objects.get(id=number_id)
        number.set_owner(buyer_id)
        number.save()
        return number, 'success'
    except ObjectDoesNotExist:
        msg = 'invalid id: {0}'.format(number_id)
        return False, msg
