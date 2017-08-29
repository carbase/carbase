import os
import time

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from controller.models import Inspection


class ControllerTestCase(StaticLiveServerTestCase):
    fixtures = [
        os.path.join(settings.BASE_DIR, 'fixtures', 'AgreementTemplate.json'),
        os.path.join(settings.BASE_DIR, 'fixtures', 'NumberPlate.json'),
        os.path.join(settings.BASE_DIR, 'fixtures', 'Center.json'),
    ]

    def test_inspection_queue(self):
        inspection1 = Inspection.objects.create(center_id=1, time_range='9:00-12:00', date='2017-08-10')
        Inspection.objects.create(center_id=1, time_range='9:00-12:00', date='2017-08-10')
        Inspection.objects.create(center_id=1, time_range='9:00-12:00', date='2017-08-10')
        Inspection.objects.create(center_id=1, time_range='9:00-12:00', date='2017-08-10')

        inspection1.time_range = '12:00-15:00'
        inspection1.save()
        Inspection.objects.create(center_id=1, time_range='12:00-15:00', date='2017-08-10')
        Inspection.objects.create(center_id=1, time_range='12:00-15:00', date='2017-08-10')
        Inspection.objects.create(center_id=1, time_range='12:00-15:00', date='2017-08-10')
        Inspection.objects.create(center_id=1, time_range='12:00-15:00', date='2017-08-10')
        Inspection.objects.create(center_id=1, time_range='12:00-15:00', date='2017-08-10')
        Inspection.objects.create(center_id=1, time_range='12:00-15:00', date='2017-08-10')
        Inspection.objects.create(center_id=1, time_range='12:00-15:00', date='2017-08-10')
        Inspection.objects.create(center_id=1, time_range='12:00-15:00', date='2017-08-10')
        with self.assertRaises(ValueError):
            Inspection.objects.create(center_id=1, time_range='12:00-15:00', date='2017-08-10')
