from django.test import TestCase
from django.conf import settings

from .models import NumberPlate
from .api import get_owner_number_plates, get_number_plates, set_owner

from controller.models import Center


class NumberPlatesTestCase(TestCase):

    def test_owner_numbers(self):
        owner_id = '123456789100'
        row = NumberPlate.objects.create(digits='001', characters='KAZ', region='01',
                                         owner_id=owner_id)
        fetched = get_owner_number_plates(owner_id)[0]
        self.assertEqual(row, fetched)

    def test_number_list_on_center(self):
        center = Center.objects.create(city='Almaty', address='Dostyk')
        row = NumberPlate.objects.create(digits='001', characters='KAZ', region='01',
                                         owner_id='123456789100', center=center)
        fetched = get_number_plates(center_id=row.id)[0]
        self.assertEqual(row, fetched)

    def test_number_list_on_limit(self):
        limit = 5
        for i in range(limit):
            NumberPlate.objects.create(digits='001', characters='KAZ', region='01',
                                       owner_id='123456789100')
        fetched = get_number_plates(limit=limit)
        self.assertEqual(limit, len(fetched))

    def test_number_list_on_pattern(self):
        rows = 9
        pattern = '00 77'
        for i in range(rows):
            # first pattern
            NumberPlate.objects.create(
                digits='00{}'.format(i+1),
                characters='KAZ',
                region='01',
                owner_id='123456789100'
            )
            # second pattern
            NumberPlate.objects.create(
                digits='77{}'.format(i+1),
                characters='KAZ',
                region='01',
                owner_id='123456789100'
            )
        fetched = get_number_plates(search_pattern=pattern)
        self.assertEqual(rows*2, len(fetched))

    def test_set_owner(self):
        plate_number = '001KAZ01'
        owner_id = '123456789100'
        NumberPlate.objects.create(digits=plate_number[0:3], characters=plate_number[3:6],
                                   region=plate_number[6:8])
        result = set_owner(plate_number=plate_number, user_id=owner_id)
        self.assertNotEquals(result, False)

    def test_price_vip1(self):
        series = '100ABC01'
        number = NumberPlate.objects.create(
            digits=series[0:3],
            characters=series[3:6],
            region=series[6:8]
        )
        price = settings.MCI * settings.VIP1_TAX
        self.assertEqual(number.get_price(), price)

    def test_price_vip2(self):
        series = '001ABC01'
        number = NumberPlate.objects.create(
            digits=series[0:3],
            characters=series[3:6],
            region=series[6:8]
        )
        price = settings.MCI * settings.VIP2_TAX
        self.assertEqual(number.get_price(), price)

    def test_price_vip3(self):
        series = '010AAA01'
        number = NumberPlate.objects.create(
            digits=series[0:3],
            characters=series[3:6],
            region=series[6:8]
        )
        price = settings.MCI * settings.VIP3_TAX
        self.assertEqual(number.get_price(), price)

    def test_price_vip1_extra(self):
        series = '100AAA01'
        number = NumberPlate.objects.create(
            digits=series[0:3],
            characters=series[3:6],
            region=series[6:8]
        )
        price = settings.MCI * settings.VIP1_EXTRA_TAX
        self.assertEqual(number.get_price(), price)

    def test_price_vip2_extra(self):
        series = '001BBB01'
        number = NumberPlate.objects.create(
            digits=series[0:3],
            characters=series[3:6],
            region=series[6:8]
        )
        price = settings.MCI * settings.VIP2_EXTRA_TAX
        self.assertEqual(number.get_price(), price)