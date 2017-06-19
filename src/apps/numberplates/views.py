from .api import get_owner_number_plates, get_number_plates, set_owner


def get_number_plates(owner_id=None, center_id=None, limit=None, offset=None, search_pattern=None):
    if owner_id is not None:
        return get_owner_number_plates(owner_id=owner_id)

    return get_number_plates(center_id=center_id, limit=limit, offset=offset,
                             search_pattern=search_pattern)


def set_number_plate_owner(plate_number, user_id):
    return set_owner(plate_number=plate_number, user_id=user_id)
