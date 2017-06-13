import os

from django.test import TestCase, Client


class LoginTestCase(TestCase):
    def setUp(self):
        self.test_xml_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_xmls')

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
