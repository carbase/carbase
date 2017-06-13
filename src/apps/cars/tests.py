import os

from django.test import TestCase, Client

class LoginTestCase(TestCase):
    def test_anonymous_get_cars(self):
        c = Client()
        response = c.get('/cars/')
        print(response)
