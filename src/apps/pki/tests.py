import os
import time
import datetime

from django.test import Client
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from pki.models import RevokedCertificate
from django.utils.timezone import make_aware


class LoginTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super(LoginTestCase, cls).setUpClass()
        cls.test_xml_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_xmls')
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(LoginTestCase, cls).tearDownClass()

    def test_valid_xml(self):
        signed_xml = open(os.path.join(self.test_xml_dir, 'valid.xml'), 'r').read()
        c = Client()
        response = c.post('/pki/login/', {'signedXml': signed_xml})
        self.assertEqual(response.json()['status'], 'success')

    def test_invalid_sign_xml(self):
        signed_xml = open(os.path.join(self.test_xml_dir, 'invalid_sign.xml'), 'r').read()
        c = Client()
        response = c.post('/pki/login/', {'signedXml': signed_xml})
        self.assertEqual(response.json()['status'], 'error')

    def test_invalid_signed_xml(self):
        signed_xml = open(os.path.join(self.test_xml_dir, 'valid.xml'), 'r').read()[:-5]
        c = Client()
        response = c.post('/pki/login/', {'signedXml': signed_xml})
        self.assertEqual(response.json()['status'], 'error')

    def test_blank_signed_xml(self):
        c = Client()
        response = c.post('/pki/login/', {})
        self.assertEqual(response.json()['status'], 'error')
        response = c.post('/pki/login/', {'signedXml': ''})
        self.assertEqual(response.json()['status'], 'error')

    def test_expired_xml(self):
        signed_xml = open(os.path.join(self.test_xml_dir, 'expired.xml'), 'r').read()
        c = Client()
        response = c.post('/pki/login/', {'signedXml': signed_xml})
        self.assertEqual(response.json()['status'], 'error')

    def test_login_form(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        self.selenium.add_cookie({'name': 'sessionid', 'value': '', 'path': '/'})
        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        find_by_css = self.selenium.find_element_by_css_selector
        login_modal = find_by_css("#loginModal")
        login_modal_close_button = find_by_css("#loginModal .close")
        jumbotron_start_login_button = find_by_css('.jumbotron [data-target="#loginModal"]')
        header_start_login_button = find_by_css('nav [data-target="#loginModal"]')
        self.assertFalse(login_modal.is_displayed())
        jumbotron_start_login_button.click()
        time.sleep(1)
        self.assertTrue(login_modal.is_displayed())
        login_modal_close_button.click()
        time.sleep(1)
        self.assertFalse(login_modal.is_displayed())
        header_start_login_button.click()
        time.sleep(1)
        self.assertTrue(login_modal.is_displayed())

    def test_revoked_cert_login(self):
        signed_xml = open(os.path.join(self.test_xml_dir, 'revoked.xml'), 'r').read()
        RevokedCertificate.objects.create(
            serial_number='232246770346734382260783361829888060015272895260',
            revocation_date=make_aware(datetime.datetime.now())
        )
        c = Client()
        response = c.post('/pki/login/', {'signedXml': signed_xml})
        self.assertEqual(response.json()['status'], 'error')

    def test_forbidden_if_not_logined(self):
        c = Client()
        response = c.get("/cars/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.templates[0].name, "403.html")
        self.selenium.get('%s%s' % (self.live_server_url, '/cars/'))
        find_by_css = self.selenium.find_element_by_css_selector
        login_modal = find_by_css("#loginModal")
        header_start_login_button = find_by_css('nav [data-target="#loginModal"]')
        self.assertFalse(login_modal.is_displayed())
        header_start_login_button.click()
        time.sleep(1)
        self.assertTrue(login_modal.is_displayed())
