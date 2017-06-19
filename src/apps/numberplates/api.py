from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from .models import NumberPlate


def get_owner_number_plates(owner_id):
    return NumberPlate.objects.filter(owner_id=owner_id)


def get_number_plates(center_id=None, limit=None, offset=None, search_pattern=None):

    # default vars
    lim = 50 if limit is None else limit
    off = 0 if offset is None else offset

    # query set filters
    filters = []

    # center specified
    if center_id is not None:
        filters.append(Q(center__id=center_id))

    # search pattern specified
    if search_pattern is not None:
        filters.append(Q(digits__startswith=search_pattern))

    return NumberPlate.objects.filter(*filters)[off:(off+lim)]


def set_owner(plate_number, user_id):
    try:
        digits = plate_number[0:3]
        characters = plate_number[3:6]
        region = plate_number[6:8]
        number = NumberPlate.objects.get(digits=digits, characters=characters, region=region)
        number.set_owner(user_id=user_id)
        number.save()
        return number, 'success'
    except ObjectDoesNotExist:
        msg = 'invalid number: {0}'.format(plate_number)
        return False, msg
