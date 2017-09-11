import os
import time
import json
from urllib.parse import urlencode

# from django.core.serializers import serialize
from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.http.cookie import SimpleCookie
from django.test import Client
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from cars.models import Car, Fine, Tax, Reregistration, Registration
from controller.models import Center, Inspector
from django.contrib.auth import get_user_model

User = get_user_model()


class CarsTestCase(StaticLiveServerTestCase):
    fixtures = [
        os.path.join(settings.BASE_DIR, 'fixtures', 'AgreementTemplate.json'),
        os.path.join(settings.BASE_DIR, 'fixtures', 'NumberPlate.json'),
        os.path.join(settings.BASE_DIR, 'fixtures', 'Center.json'),
    ]

    @classmethod
    def setUpClass(cls):
        car1 = {'user': 'IIN123456789011', 'manufacturer': 'Toyota', 'model': 'Camry', 'number': 'A166BDA'}
        car2 = {'user': 'IIN123456789011', 'manufacturer': 'BMW', 'model': 'X1', 'number': '156ASM01'}
        super(CarsTestCase, cls).setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)
        cls.car1 = Car.objects.create(**car1)
        cls.car2 = Car.objects.create(**car2)

    def get_seller_sessionid(self):
        test_xml_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_xmls')
        signed_xml = open(os.path.join(test_xml_dir, 'login.xml'), 'r').read()
        c = Client()
        response = c.post('/pki/login/', {'signedXml': signed_xml})
        return response.client.cookies["sessionid"].value

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(CarsTestCase, cls).tearDownClass()

    def test_car_page(self):
        self.car1.save()
        self.car2.save()
        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        self.selenium.add_cookie({'name': 'sessionid', 'value': self.get_seller_sessionid(), 'path': '/'})
        self.selenium.add_cookie({'name': 'enjoyhint_cars', 'value': '1', 'path': '/'})
        self.selenium.add_cookie({'name': 'djdt', 'value': 'hide', 'path': '/'})
        self.selenium.get('%s%s' % (self.live_server_url, '/cars/'))
        find_by_css = self.selenium.find_element_by_css_selector
        navbar_right_username = find_by_css('.navbar-right .dropdown-toggle')
        self.assertEqual(navbar_right_username.text, 'ТЕСТОВ ТЕСТ')
        car1_panel = find_by_css('#carPanel' + str(self.car1.id))
        car2_panel = find_by_css('#carPanel' + str(self.car2.id))
        car1_rereg_modal = find_by_css('#reregistrationModal' + str(self.car1.id))
        car2_rereg_modal = find_by_css('#reregistrationModal' + str(self.car2.id))
        car1_dereg_modal = find_by_css('#deregistrationModal' + str(self.car1.id))
        car2_dereg_modal = find_by_css('#deregistrationModal' + str(self.car2.id))
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

        self.assertFalse(car1_rereg_modal.is_displayed())
        self.assertFalse(car2_rereg_modal.is_displayed())
        car1_rereg_button.click()
        self.assertTrue(car1_rereg_modal.is_displayed())
        self.assertFalse(car2_rereg_modal.is_displayed())
        car1_rereg_modal.send_keys(Keys.ESCAPE)
        time.sleep(1)
        self.assertFalse(car1_rereg_modal.is_displayed())
        self.assertFalse(car2_rereg_modal.is_displayed())
        car2_rereg_button.click()
        self.assertFalse(car1_rereg_modal.is_displayed())
        self.assertTrue(car2_rereg_modal.is_displayed())
        car2_rereg_modal.send_keys(Keys.ESCAPE)
        time.sleep(1)

        self.assertFalse(car1_dereg_modal.is_displayed())
        self.assertFalse(car2_dereg_modal.is_displayed())
        car1_dereg_button.click()
        time.sleep(1)
        self.assertTrue(car1_dereg_modal.is_displayed())
        self.assertFalse(car2_dereg_modal.is_displayed())
        car1_dereg_modal.send_keys(Keys.ESCAPE)
        time.sleep(1)
        self.assertFalse(car1_dereg_modal.is_displayed())
        self.assertFalse(car2_dereg_modal.is_displayed())
        car2_dereg_button.click()
        time.sleep(1)
        self.assertFalse(car1_dereg_modal.is_displayed())
        self.assertTrue(car2_dereg_modal.is_displayed())
        car2_dereg_modal.send_keys(Keys.ESCAPE)
        time.sleep(1)

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
        car1_rereg_modal = find_by_css('#reregistrationModal' + str(self.car1.id))
        car2_rereg_modal = find_by_css('#reregistrationModal' + str(self.car2.id))
        car1_dereg_modal = find_by_css('#deregistrationModal' + str(self.car1.id))
        car2_dereg_modal = find_by_css('#deregistrationModal' + str(self.car2.id))
        car1_dereg_button = car1_panel.find_elements_by_class_name('deregistration-button')[0]
        car1_rereg_button = car1_panel.find_elements_by_class_name('reregistration-button')[0]
        car2_dereg_button = car2_panel.find_elements_by_class_name('deregistration-button')[0]
        car2_rereg_button = car2_panel.find_elements_by_class_name('reregistration-button')[0]
        self.assertIn('disabled', car1_dereg_button.get_attribute('class'))
        self.assertIn('disabled', car2_dereg_button.get_attribute('class'))
        self.assertIn('disabled', car1_rereg_button.get_attribute('class'))
        self.assertIn('disabled', car2_rereg_button.get_attribute('class'))

        self.assertFalse(car1_rereg_modal.is_displayed())
        self.assertFalse(car2_rereg_modal.is_displayed())
        car1_rereg_button.click()
        time.sleep(1)
        self.assertFalse(car1_rereg_modal.is_displayed())
        self.assertFalse(car2_rereg_modal.is_displayed())
        car2_rereg_button.click()
        time.sleep(1)
        self.assertFalse(car1_rereg_modal.is_displayed())
        self.assertFalse(car2_rereg_modal.is_displayed())

        self.assertFalse(car1_dereg_modal.is_displayed())
        self.assertFalse(car2_dereg_modal.is_displayed())
        car1_dereg_button.click()
        time.sleep(1)
        self.assertFalse(car1_dereg_modal.is_displayed())
        self.assertFalse(car2_dereg_modal.is_displayed())
        car2_dereg_button.click()
        time.sleep(1)
        self.assertFalse(car1_dereg_modal.is_displayed())
        self.assertFalse(car2_dereg_modal.is_displayed())

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
        car1_rereg_modal = find_by_css('#reregistrationModal' + str(self.car1.id))
        car2_rereg_modal = find_by_css('#reregistrationModal' + str(self.car2.id))
        car1_dereg_modal = find_by_css('#deregistrationModal' + str(self.car1.id))
        car2_dereg_modal = find_by_css('#deregistrationModal' + str(self.car2.id))
        car1_dereg_button = car1_panel.find_elements_by_class_name('deregistration-button')[0]
        car1_rereg_button = car1_panel.find_elements_by_class_name('reregistration-button')[0]
        car2_dereg_button = car2_panel.find_elements_by_class_name('deregistration-button')[0]
        car2_rereg_button = car2_panel.find_elements_by_class_name('reregistration-button')[0]
        self.assertNotIn('disabled', car1_dereg_button.get_attribute('class'))
        self.assertNotIn('disabled', car2_dereg_button.get_attribute('class'))
        self.assertNotIn('disabled', car1_rereg_button.get_attribute('class'))
        self.assertNotIn('disabled', car2_rereg_button.get_attribute('class'))

        self.assertFalse(car1_rereg_modal.is_displayed())
        self.assertFalse(car2_rereg_modal.is_displayed())
        car1_rereg_button.click()
        time.sleep(1)
        self.assertTrue(car1_rereg_modal.is_displayed())
        self.assertFalse(car2_rereg_modal.is_displayed())
        car1_rereg_modal.send_keys(Keys.ESCAPE)
        time.sleep(1)
        self.assertFalse(car1_rereg_modal.is_displayed())
        self.assertFalse(car2_rereg_modal.is_displayed())
        car2_rereg_button.click()
        time.sleep(1)
        self.assertFalse(car1_rereg_modal.is_displayed())
        self.assertTrue(car2_rereg_modal.is_displayed())
        car2_rereg_modal.send_keys(Keys.ESCAPE)
        time.sleep(1)

        self.assertFalse(car1_dereg_modal.is_displayed())
        self.assertFalse(car2_dereg_modal.is_displayed())
        car1_dereg_button.click()
        time.sleep(1)
        self.assertTrue(car1_dereg_modal.is_displayed())
        self.assertFalse(car2_dereg_modal.is_displayed())
        car1_dereg_modal.send_keys(Keys.ESCAPE)
        time.sleep(1)
        self.assertFalse(car1_dereg_modal.is_displayed())
        self.assertFalse(car2_dereg_modal.is_displayed())
        car2_dereg_button.click()
        time.sleep(1)
        self.assertFalse(car1_dereg_modal.is_displayed())
        self.assertTrue(car2_dereg_modal.is_displayed())
        car2_dereg_modal.send_keys(Keys.ESCAPE)
        time.sleep(1)

    def test_reregistration_page(self):
        self.car1.save()
        self.car2.save()
        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        self.selenium.add_cookie({'name': 'sessionid', 'value': self.get_seller_sessionid(), 'path': '/'})
        self.selenium.add_cookie({'name': 'enjoyhint_cars', 'value': '1', 'path': '/'})
        self.selenium.add_cookie({'name': 'djdt', 'value': 'hide', 'path': '/'})
        self.selenium.get('%s%s' % (self.live_server_url, '/cars/reregistration?side=seller&car=' + str(self.car1.id)))

        find_by_id = self.selenium.find_element_by_id
        find_by_css = self.selenium.find_element_by_css_selector

        self.assertIn('active', find_by_css('.step_1').get_attribute('class'))
        self.assertNotIn('disabled', find_by_css('.step_1').get_attribute('class'))
        self.assertIn('disabled', find_by_css('.step_2').get_attribute('class'))
        self.assertNotIn('active', find_by_css('.step_2').get_attribute('class'))
        self.assertTrue(find_by_css('.step_1_body').is_displayed())
        self.assertFalse(find_by_css('.step_2_body').is_displayed())

        agreement_selector = Select(find_by_id('reregistration' + str(self.car1.id) + 'AgreementSelector'))
        self.assertEqual(agreement_selector.first_selected_option.get_property('value'), '1')
        find_by_id('reregistration' + str(self.car1.id) + 'BuyerIIN').send_keys('123456789011')
        find_by_css('.submit-iin-button').click()
        time.sleep(2)

        self.assertIn('complete', find_by_css('.step_1').get_attribute('class'))
        self.assertNotIn('active', find_by_css('.step_1').get_attribute('class'))
        self.assertIn('active', find_by_css('.step_2').get_attribute('class'))
        self.assertNotIn('disabled', find_by_css('.step_2').get_attribute('class'))
        self.assertFalse(find_by_css('.step_1_body').is_displayed())
        self.assertTrue(find_by_css('.step_2_body').is_displayed())
        time.sleep(1)

        reregistration = Reregistration.objects.get(car=self.car1.id)
        test_xml_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_xmls')
        signed_xml = open(os.path.join(test_xml_dir, 'seller_sign.xml'), 'r').read()

        c = Client(HTTP_COOKIE=SimpleCookie({'sessionid': self.get_seller_sessionid()}).output(header='', sep='; '))
        response = c.put(
            '/cars/reregistration',
            urlencode({'reregistrationId': reregistration.id, 'seller_sign': signed_xml, 'amount': 10000000}),
            'application/x-www-form-urlencoded'
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.content.decode()).get('result'), 'error')

        self.selenium.get('%s%s' % (self.live_server_url, '/cars/reregistration?side=seller&car=' + str(self.car1.id)))

        self.assertIn('complete', find_by_css('.step_1').get_attribute('class'))
        self.assertNotIn('active', find_by_css('.step_1').get_attribute('class'))
        self.assertIn('active', find_by_css('.step_2').get_attribute('class'))
        self.assertNotIn('disabled', find_by_css('.step_2').get_attribute('class'))
        self.assertFalse(find_by_css('.step_1_body').is_displayed())
        self.assertTrue(find_by_css('.step_2_body').is_displayed())
        self.assertTrue(find_by_css('#sellerSign' + str(self.car1.id) + ' img').is_displayed())

        self.selenium.get('%s%s' % (self.live_server_url, '/cars/reregistration?side=buyer&car=' + str(self.car1.id)))
        time.sleep(2)

        self.assertIn('active', find_by_css('.step_1').get_attribute('class'))
        self.assertNotIn('complete', find_by_css('.step_1').get_attribute('class'))
        self.assertIn('disabled', find_by_css('.step_2').get_attribute('class'))
        self.assertIn('disabled', find_by_css('.step_3').get_attribute('class'))
        self.assertIn('disabled', find_by_css('.step_4').get_attribute('class'))
        self.assertTrue(find_by_css('.step_1_body').is_displayed())
        self.assertFalse(find_by_css('.step_2_body').is_displayed())
        self.assertFalse(find_by_css('.step_3_body').is_displayed())
        self.assertFalse(find_by_css('.step_4_body').is_displayed())
        self.assertTrue(find_by_css('#sellerSign' + str(self.car1.id) + ' img').is_displayed())

        c = Client(HTTP_COOKIE=SimpleCookie({'sessionid': self.get_seller_sessionid()}).output(header='', sep='; '))
        response = c.put(
            '/cars/reregistration',
            urlencode({'reregistrationId': reregistration.id, 'buyer_sign': signed_xml, 'amount': 10000000}),
            'application/x-www-form-urlencoded'
        )
        self.assertEqual(response.status_code, 200)

        self.selenium.get('%s%s' % (self.live_server_url, '/cars/reregistration?side=buyer&car=' + str(self.car1.id)))
        time.sleep(2)

        self.assertIn('complete', find_by_css('.step_1').get_attribute('class'))
        self.assertIn('active', find_by_css('.step_2').get_attribute('class'))
        self.assertIn('disabled', find_by_css('.step_3').get_attribute('class'))
        self.assertIn('disabled', find_by_css('.step_4').get_attribute('class'))
        self.assertFalse(find_by_css('.step_1_body').is_displayed())
        self.assertTrue(find_by_css('.step_2_body').is_displayed())
        self.assertFalse(find_by_css('.step_3_body').is_displayed())
        self.assertFalse(find_by_css('.step_4_body').is_displayed())

        find_by_css('#reregistrationStep2SubmitButton').click()
        time.sleep(3)

        self.assertIn('complete', find_by_css('.step_1').get_attribute('class'))
        self.assertIn('complete', find_by_css('.step_2').get_attribute('class'))
        self.assertIn('active', find_by_css('.step_3').get_attribute('class'))
        self.assertIn('disabled', find_by_css('.step_4').get_attribute('class'))
        self.assertFalse(find_by_css('.step_1_body').is_displayed())
        self.assertFalse(find_by_css('.step_2_body').is_displayed())
        self.assertTrue(find_by_css('.step_3_body').is_displayed())
        self.assertFalse(find_by_css('.step_4_body').is_displayed())

        self.selenium.get('%s%s' % (self.live_server_url, '/cars/reregistration?side=buyer&car=' + str(self.car1.id)))
        time.sleep(2)

        self.assertIn('complete', find_by_css('.step_1').get_attribute('class'))
        self.assertIn('complete', find_by_css('.step_2').get_attribute('class'))
        self.assertIn('active', find_by_css('.step_3').get_attribute('class'))
        self.assertIn('disabled', find_by_css('.step_4').get_attribute('class'))
        self.assertFalse(find_by_css('.step_1_body').is_displayed())
        self.assertFalse(find_by_css('.step_2_body').is_displayed())
        self.assertTrue(find_by_css('.step_3_body').is_displayed())
        self.assertTrue(find_by_css('.step_3_body iframe').is_displayed())
        self.assertFalse(find_by_css('.step_4_body').is_displayed())

        reregistration = Reregistration.objects.get(car=self.car1.id)
        reregistration.is_tax_paid = True
        reregistration.save()

        self.selenium.get('%s%s' % (self.live_server_url, '/cars/reregistration?side=buyer&car=' + str(self.car1.id)))
        time.sleep(2)

        self.assertIn('complete', find_by_css('.step_1').get_attribute('class'))
        self.assertIn('complete', find_by_css('.step_2').get_attribute('class'))
        self.assertIn('complete', find_by_css('.step_3').get_attribute('class'))
        self.assertIn('active', find_by_css('.step_4').get_attribute('class'))
        self.assertFalse(find_by_css('.step_1_body').is_displayed())
        self.assertFalse(find_by_css('.step_2_body').is_displayed())
        self.assertFalse(find_by_css('.step_3_body').is_displayed())
        self.assertTrue(find_by_css('.step_4_body').is_displayed())

        self.assertEqual(
            find_by_css('.step_4_body p').text,
            'Забронируйте удобное для вас время осмотра ТС на территории спецЦОНа:'
        )

        self.selenium.execute_script('$(".datepicker").val("10 Август 2017")')
        self.selenium.execute_script('$("#inspectionDateInput' + str(self.car1.id) + '").val("2017-08-10")')
        find_by_css('.reserve-time-button').click()
        time.sleep(1)

        self.assertNotEqual(
            find_by_css('.step_4_body p').text,
            'Забронируйте удобное для вас время осмотра ТС на территории спецЦОНа:'
        )

        center = Center.objects.get(id=1)
        user_allower = User.objects.create(username='all123456')
        user_allower.set_password('password123')
        user_allower.save()
        user_revisor = User.objects.create(username='rev123456')
        user_revisor.set_password('password123')
        user_revisor.save()
        user_admin = User.objects.create(username='adm123456')
        user_admin.set_password('password123')
        user_admin.save()
        controller_allower = Inspector.objects.create(user=user_allower, center=center)
        controller_revisor = Inspector.objects.create(user=user_revisor, center=center)
        controller_admin = Inspector.objects.create(user=user_admin, center=center)
        time.sleep(1)

        self.selenium.get('%s%s' % (self.live_server_url, '/controller'))
        find_by_css('#loginUsername').send_keys(controller_allower.user.username)
        find_by_css('#loginPassword').send_keys('password123')
        find_by_css('[value="Войти"]').click()
        time.sleep(1)

    def test_all_payments(self):
        self.car1.save()
        self.car2.save()

        find_by_id = self.selenium.find_element_by_id

        car1Fine1 = Fine.objects.create(car=self.car1, amount=10000, info="Штраф 1", is_paid=False)
        car1Fine2 = Fine.objects.create(car=self.car1, amount=10000, info="Штраф 2", is_paid=False)
        car1Fine3 = Fine.objects.create(car=self.car1, amount=10000, info="Штраф 3", is_paid=False)
        car1Tax1 = Tax.objects.create(car=self.car1, amount=10000, info="Налог 1", is_paid=False)

        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        self.selenium.add_cookie({'name': 'sessionid', 'value': self.get_seller_sessionid(), 'path': '/'})
        self.selenium.add_cookie({'name': 'enjoyhint_cars', 'value': '1', 'path': '/'})
        self.selenium.add_cookie({'name': 'djdt', 'value': 'hide', 'path': '/'})
        self.selenium.get('%s%s' % (self.live_server_url, '/cars'))

        car1_panel = find_by_id('carPanel' + str(self.car1.id))

        self.assertNotIn('disabled', car1_panel.find_elements_by_class_name('pay-all-button')[0].get_attribute('class'))
        car1_panel.find_elements_by_class_name('pay-all-button')[0].click()
        time.sleep(1)
        self.assertTrue(car1_panel.find_elements_by_class_name('payAllModal')[0].is_displayed())

        car1_modal = car1_panel.find_elements_by_class_name('payAllModal')[0]
        self.assertTrue(car1_modal.find_elements_by_class_name('step_1')[0].is_displayed())
        self.assertFalse(car1_modal.find_elements_by_class_name('step_2')[0].is_displayed())
        self.assertIn(car1Fine1.info, car1_modal.find_elements_by_class_name('col-xs-9')[0].text)
        self.assertIn(car1Fine2.info, car1_modal.find_elements_by_class_name('col-xs-9')[1].text)
        self.assertIn(car1Fine3.info, car1_modal.find_elements_by_class_name('col-xs-9')[2].text)
        self.assertIn(car1Tax1.info, car1_modal.find_elements_by_class_name('col-xs-9')[3].text)
        self.assertEqual(4, len(car1_modal.find_elements_by_class_name('list-group-item-info')))
        self.assertEqual(40000, int(car1_modal.find_elements_by_class_name('payAllModalAmount')[0].text))

        car1_modal.find_elements_by_class_name('col-xs-9')[3].click()
        time.sleep(1)
        self.assertEqual(3, len(car1_modal.find_elements_by_class_name('list-group-item-info')))
        self.assertEqual(30000, int(car1_modal.find_elements_by_class_name('payAllModalAmount')[0].text))

        car1_modal.find_elements_by_class_name('col-xs-9')[3].click()
        time.sleep(1)
        self.assertEqual(4, len(car1_modal.find_elements_by_class_name('list-group-item-info')))
        self.assertEqual(40000, int(car1_modal.find_elements_by_class_name('payAllModalAmount')[0].text))

        car1_modal.find_elements_by_class_name('payAllModalButton')[0].click()
        time.sleep(1)
        self.assertFalse(car1_modal.find_elements_by_class_name('step_1')[0].is_displayed())
        self.assertTrue(car1_modal.find_elements_by_class_name('step_2')[0].is_displayed())

    def test_deregistration_page(self):
        pass

    def test_registration_page(self):
        self.car1.save()

        find_by_css = self.selenium.find_element_by_css_selector

        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        self.selenium.add_cookie({'name': 'sessionid', 'value': self.get_seller_sessionid(), 'path': '/'})
        self.selenium.add_cookie({'name': 'enjoyhint_cars', 'value': '1', 'path': '/'})
        self.selenium.add_cookie({'name': 'djdt', 'value': 'hide', 'path': '/'})
        self.selenium.get('%s%s' % (self.live_server_url, '/cars'))

        find_by_css('.new_reg_car_button').click()
        time.sleep(2)
        self.assertTrue(find_by_css('#registrationModal').is_displayed())
        self.selenium.get('%s%s' % (self.live_server_url, '/cars/registration'))

        self.assertIn('active', find_by_css('.step_1').get_attribute('class'))
        self.assertIn('disabled', find_by_css('.step_2').get_attribute('class'))
        self.assertIn('disabled', find_by_css('.step_3').get_attribute('class'))
        self.assertIn('disabled', find_by_css('.step_4').get_attribute('class'))
        self.assertIn('disabled', find_by_css('.step_5').get_attribute('class'))
        self.assertTrue(find_by_css('.step_1_body').is_displayed())
        self.assertFalse(find_by_css('.step_2_body').is_displayed())
        self.assertFalse(find_by_css('.step_3_body').is_displayed())
        self.assertFalse(find_by_css('.step_4_body').is_displayed())
        self.assertFalse(find_by_css('.step_5_body').is_displayed())

        find_by_css('#newRegistrationVinCode').send_keys('1FADP3L95DL207700')
        find_by_css('#getVinCodeInformation').click()
        time.sleep(5)

        self.assertEqual(find_by_css('#newRegistrationManufacturer').get_attribute("value"), 'FORD')
        self.assertEqual(find_by_css('#newRegistrationModel').get_attribute("value"), 'Focus')
        self.assertEqual(find_by_css('#newRegistrationYear').get_attribute("value"), '2013')

        find_by_css('#newRegistrationVinCodeButton').click()
        time.sleep(5)

        self.assertIn('complete', find_by_css('.step_1').get_attribute('class'))
        self.assertIn('active', find_by_css('.step_2').get_attribute('class'))
        self.assertIn('disabled', find_by_css('.step_3').get_attribute('class'))
        self.assertIn('disabled', find_by_css('.step_4').get_attribute('class'))
        self.assertIn('disabled', find_by_css('.step_5').get_attribute('class'))
        self.assertFalse(find_by_css('.step_1_body').is_displayed())
        self.assertTrue(find_by_css('.step_2_body').is_displayed())
        self.assertFalse(find_by_css('.step_3_body').is_displayed())
        self.assertFalse(find_by_css('.step_4_body').is_displayed())
        self.assertFalse(find_by_css('.step_5_body').is_displayed())

        self.assertEqual(find_by_css('#newRegistrationForm input[name="manufacturer"]').get_attribute("value"), 'FORD')
        self.assertEqual(find_by_css('#newRegistrationForm input[name="model"]').get_attribute("value"), 'Focus')
        self.assertEqual(find_by_css('#newRegistrationForm input[name="year"]').get_attribute("value"), '2013')
        self.assertEqual(find_by_css('#newRegistrationForm input[name="vin_code"]').get_attribute("value"), '1FADP3L95DL207700')

        # test_path = os.path.join(settings.BASE_DIR, 'apps', 'cars', 'test_xmls', 'login.xml')
        # find_by_css('input[type="file"]').send_keys(test_path)
        find_by_css('.send-documents-button').click()
        time.sleep(2)

        self.assertIn('complete', find_by_css('.step_1').get_attribute('class'))
        self.assertIn('complete', find_by_css('.step_2').get_attribute('class'))
        self.assertIn('active', find_by_css('.step_3').get_attribute('class'))
        self.assertIn('disabled', find_by_css('.step_4').get_attribute('class'))
        self.assertIn('disabled', find_by_css('.step_5').get_attribute('class'))
        self.assertFalse(find_by_css('.step_1_body').is_displayed())
        self.assertFalse(find_by_css('.step_2_body').is_displayed())
        self.assertTrue(find_by_css('.step_3_body').is_displayed())
        self.assertFalse(find_by_css('.step_4_body').is_displayed())
        self.assertFalse(find_by_css('.step_5_body').is_displayed())

        reg_id = find_by_css('#registrationStep3SubmitButton').get_attribute("data-regid")

        find_by_css('#registrationStep3SubmitButton').click()
        time.sleep(4)

        self.assertIn('complete', find_by_css('.step_1').get_attribute('class'))
        self.assertIn('complete', find_by_css('.step_2').get_attribute('class'))
        self.assertIn('complete', find_by_css('.step_3').get_attribute('class'))
        self.assertIn('active', find_by_css('.step_4').get_attribute('class'))
        self.assertIn('disabled', find_by_css('.step_5').get_attribute('class'))
        self.assertFalse(find_by_css('.step_1_body').is_displayed())
        self.assertFalse(find_by_css('.step_2_body').is_displayed())
        self.assertFalse(find_by_css('.step_3_body').is_displayed())
        self.assertTrue(find_by_css('.step_4_body').is_displayed())
        self.assertFalse(find_by_css('.step_5_body').is_displayed())

        registration = Registration.objects.get(id=reg_id)
        self.assertEqual(registration.car.manufacturer, 'FORD')
        self.assertEqual(registration.car.model, 'Focus')
        self.assertEqual(registration.car.year, '2013')
        self.assertEqual(registration.car.vin_code, '1FADP3L95DL207700')
        self.assertEqual(registration.car_vin_code, '1FADP3L95DL207700')
        registration.is_paid = True
        registration.save()
        time.sleep(1)

        self.selenium.get('%s%s' % (self.live_server_url, '/cars/registration'))
        time.sleep(1)

        self.assertIn('complete', find_by_css('.step_1').get_attribute('class'))
        self.assertIn('complete', find_by_css('.step_2').get_attribute('class'))
        self.assertIn('complete', find_by_css('.step_3').get_attribute('class'))
        self.assertIn('complete', find_by_css('.step_4').get_attribute('class'))
        self.assertIn('active', find_by_css('.step_5').get_attribute('class'))
        self.assertFalse(find_by_css('.step_1_body').is_displayed())
        self.assertFalse(find_by_css('.step_2_body').is_displayed())
        self.assertFalse(find_by_css('.step_3_body').is_displayed())
        self.assertFalse(find_by_css('.step_4_body').is_displayed())
        self.assertTrue(find_by_css('.step_5_body').is_displayed())

        self.assertEqual(
            find_by_css('.step_5_body p').text,
            'Забронируйте удобное для вас время осмотра ТС на территории спецЦОНа:'
        )

        self.selenium.execute_script('$(".datepicker").val("10 Август 2017")')
        self.selenium.execute_script('$("#inspectionDateInput").val("2017-08-10")')
        find_by_css('.reserve-time-button').click()
        time.sleep(1)

        self.assertNotEqual(
            find_by_css('.step_5_body p').text,
            'Забронируйте удобное для вас время осмотра ТС на территории спецЦОНа:'
        )

        center = Center.objects.get(id=1)
        user_allower = User.objects.create(username='all123456')
        user_allower.set_password('password123')
        user_allower.save()
        user_revisor = User.objects.create(username='rev123456')
        user_revisor.set_password('password123')
        user_revisor.save()
        user_admin = User.objects.create(username='adm123456')
        user_admin.set_password('password123')
        user_admin.save()
        controller_allower = Inspector.objects.create(user=user_allower, center=center)
        controller_revisor = Inspector.objects.create(user=user_revisor, center=center)
        controller_admin = Inspector.objects.create(user=user_admin, center=center)
        time.sleep(1)

        self.selenium.get('%s%s' % (self.live_server_url, '/controller'))
        find_by_css('#loginUsername').send_keys(controller_allower.user.username)
        find_by_css('#loginPassword').send_keys('password123')
        find_by_css('[value="Войти"]').click()
        time.sleep(1)
