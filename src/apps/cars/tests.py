import os
import time

from django.test import Client
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from cars.models import Car, Fine, Tax


class CarsTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        car1 = {'user': 'IIN123456789011', 'manufacturer': 'Toyota', 'model': 'Camry', 'number': 'A166BDA'}
        car2 = {'user': 'IIN123456789011', 'manufacturer': 'BMW', 'model': 'X1', 'number': '156ASM01'}
        super(CarsTestCase, cls).setUpClass()
        cls.test_xml_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_xmls')
        signed_xml = open(os.path.join(cls.test_xml_dir, 'login.xml'), 'r').read()
        c = Client()
        response = c.post('/pki/login/', {'signedXml': signed_xml})
        sessionid = response.client.cookies["sessionid"].value
        cls.selenium = WebDriver()
        cls.selenium.get('%s%s' % (cls.live_server_url, '/'))
        cls.selenium.implicitly_wait(10)
        cls.selenium.add_cookie({'name': 'sessionid', 'value': sessionid, 'path': '/'})
        cls.car1 = Car.objects.create(**car1)
        cls.car2 = Car.objects.create(**car2)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(CarsTestCase, cls).tearDownClass()

    def test_car_page(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/cars/'))
        find_by_css = self.selenium.find_element_by_css_selector
        navbar_right_username = find_by_css('.navbar-right .dropdown-toggle')
        self.assertEqual(navbar_right_username.text, 'ТЕСТОВ ТЕСТ')
        car1_panel = find_by_css('#carPanel' + str(self.car1.id))
        car2_panel = find_by_css('#carPanel' + str(self.car2.id))
        car1_title = '{} {}\n{}'.format(self.car1.manufacturer, self.car1.model, self.car1.number)
        car2_title = '{} {}\n{}'.format(self.car2.manufacturer, self.car2.model, self.car2.number)
        self.assertEqual(car1_panel.find_elements_by_class_name('panel-heading')[0].text, car1_title)
        self.assertEqual(car2_panel.find_elements_by_class_name('panel-heading')[0].text, car2_title)

        car1_fines_action = find_by_css('[data-target="#carFine' + self.car1.number + '"]').find_element_by_xpath('..')
        car2_fines_action = find_by_css('[data-target="#carFine' + self.car2.number + '"]').find_element_by_xpath('..')
        self.assertIn('panel-success', car1_fines_action.get_attribute('class'))
        self.assertIn('panel-success', car2_fines_action.get_attribute('class'))
        self.assertNotIn('panel-danger', car1_fines_action.get_attribute('class'))
        self.assertNotIn('panel-danger', car2_fines_action.get_attribute('class'))

        car1_taxes_action = find_by_css('[data-target="#carTax' + self.car1.number + '"]').find_element_by_xpath('..')
        car2_taxes_action = find_by_css('[data-target="#carTax' + self.car2.number + '"]').find_element_by_xpath('..')
        self.assertIn('panel-success', car1_taxes_action.get_attribute('class'))
        self.assertIn('panel-success', car2_taxes_action.get_attribute('class'))
        self.assertNotIn('panel-danger', car1_taxes_action.get_attribute('class'))
        self.assertNotIn('panel-danger', car2_taxes_action.get_attribute('class'))

        car1_dereg_button = car1_panel.find_elements_by_class_name('deregistration-button')[0]
        car1_rereg_button = car1_panel.find_elements_by_class_name('reregistration-button')[0]
        car2_dereg_button = car2_panel.find_elements_by_class_name('deregistration-button')[0]
        car2_rereg_button = car2_panel.find_elements_by_class_name('reregistration-button')[0]
        self.assertNotIn('disabled', car1_dereg_button.get_attribute('class'))
        self.assertNotIn('disabled', car2_dereg_button.get_attribute('class'))
        self.assertNotIn('disabled', car1_rereg_button.get_attribute('class'))
        self.assertNotIn('disabled', car2_rereg_button.get_attribute('class'))

        car1Fine = Fine.objects.create(car=self.car1, amount=10000, info="ASDF", is_paid=False)
        car2Tax = Tax.objects.create(car=self.car2, amount=10000, info="ASDF ASDF", is_paid=False)

        self.selenium.get('%s%s' % (self.live_server_url, '/cars/'))

        car1_fines_action = find_by_css('[data-target="#carFine' + self.car1.number + '"]').find_element_by_xpath('..')
        car2_fines_action = find_by_css('[data-target="#carFine' + self.car2.number + '"]').find_element_by_xpath('..')
        self.assertIn('panel-danger', car1_fines_action.get_attribute('class'))
        self.assertNotIn('panel-success', car1_fines_action.get_attribute('class'))
        self.assertIn('panel-success', car2_fines_action.get_attribute('class'))
        self.assertNotIn('panel-danger', car2_fines_action.get_attribute('class'))

        car1_taxes_action = find_by_css('[data-target="#carTax' + self.car1.number + '"]').find_element_by_xpath('..')
        car2_taxes_action = find_by_css('[data-target="#carTax' + self.car2.number + '"]').find_element_by_xpath('..')
        self.assertIn('panel-success', car1_taxes_action.get_attribute('class'))
        self.assertNotIn('panel-danger', car1_taxes_action.get_attribute('class'))
        self.assertIn('panel-danger', car2_taxes_action.get_attribute('class'))
        self.assertNotIn('panel-success', car2_taxes_action.get_attribute('class'))

        car1_panel = find_by_css('#carPanel' + str(self.car1.id))
        car2_panel = find_by_css('#carPanel' + str(self.car2.id))
        car1_dereg_button = car1_panel.find_elements_by_class_name('deregistration-button')[0]
        car1_rereg_button = car1_panel.find_elements_by_class_name('reregistration-button')[0]
        car2_dereg_button = car2_panel.find_elements_by_class_name('deregistration-button')[0]
        car2_rereg_button = car2_panel.find_elements_by_class_name('reregistration-button')[0]
        self.assertIn('disabled', car1_dereg_button.get_attribute('class'))
        self.assertIn('disabled', car2_dereg_button.get_attribute('class'))
        self.assertIn('disabled', car1_rereg_button.get_attribute('class'))
        self.assertIn('disabled', car2_rereg_button.get_attribute('class'))

        car1Fine.is_paid = True
        car1Fine.save()
        car2Tax.is_paid = True
        car2Tax.save()

        self.selenium.get('%s%s' % (self.live_server_url, '/cars/'))

        car1_fines_action = find_by_css('[data-target="#carFine' + self.car1.number + '"]').find_element_by_xpath('..')
        car2_fines_action = find_by_css('[data-target="#carFine' + self.car2.number + '"]').find_element_by_xpath('..')
        self.assertIn('panel-success', car1_fines_action.get_attribute('class'))
        self.assertIn('panel-success', car2_fines_action.get_attribute('class'))
        self.assertNotIn('panel-danger', car1_fines_action.get_attribute('class'))
        self.assertNotIn('panel-danger', car2_fines_action.get_attribute('class'))

        car1_taxes_action = find_by_css('[data-target="#carTax' + self.car1.number + '"]').find_element_by_xpath('..')
        car2_taxes_action = find_by_css('[data-target="#carTax' + self.car2.number + '"]').find_element_by_xpath('..')
        self.assertIn('panel-success', car1_taxes_action.get_attribute('class'))
        self.assertIn('panel-success', car2_taxes_action.get_attribute('class'))
        self.assertNotIn('panel-danger', car1_taxes_action.get_attribute('class'))
        self.assertNotIn('panel-danger', car2_taxes_action.get_attribute('class'))

        car1_panel = find_by_css('#carPanel' + str(self.car1.id))
        car2_panel = find_by_css('#carPanel' + str(self.car2.id))
        car1_dereg_button = car1_panel.find_elements_by_class_name('deregistration-button')[0]
        car1_rereg_button = car1_panel.find_elements_by_class_name('reregistration-button')[0]
        car2_dereg_button = car2_panel.find_elements_by_class_name('deregistration-button')[0]
        car2_rereg_button = car2_panel.find_elements_by_class_name('reregistration-button')[0]
        self.assertNotIn('disabled', car1_dereg_button.get_attribute('class'))
        self.assertNotIn('disabled', car2_dereg_button.get_attribute('class'))
        self.assertNotIn('disabled', car1_rereg_button.get_attribute('class'))
        self.assertNotIn('disabled', car2_rereg_button.get_attribute('class'))

    def test_reregistration_page(self):
        pass

    def test_deregistration_page(self):
        pass
