import api


def get_number_plates(owner_id=None, center_id=None, limit=None, offset=None, search_pattern=None):
    if owner_id is not None:
        return api.get_owner_number_plates(owner_id=owner_id)

    return api.get_number_plates(center_id=center_id, limit=limit, offset=offset,
                             search_pattern=search_pattern)


def set_number_plate_owner(plate_number, user_id):
    return api.set_owner(plate_number=plate_number, user_id=user_id)
