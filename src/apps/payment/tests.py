from django.test import TestCase

from .api import get_checkout_url, get_order_status


class CheckoutTestCase(TestCase):

    def test_success_get_checkout_url(self):
        product_id = 'prod-1'
        amount = 50000
        order_desc = 'test-1'

        data = get_checkout_url({'product_id':  product_id,
                                 'amount':      amount,
                                 'order_desc':  order_desc})

        self.assertEqual(data['response']['response_status'], 'success')

    def test_failed_get_checkout_url(self):
        product_id = 'prod-1'
        amount = -50000
        order_desc = 'test-1'

        data = get_checkout_url({'product_id':  product_id,
                                 'amount':      amount,
                                 'order_desc':  order_desc})

        self.assertEqual(data['response']['response_status'], 'failure')

    def test_success_get_order_status(self):
        product_id = 'prod-1'
        amount = 50000
        order_desc = 'test-1'

        data = get_checkout_url({'product_id': product_id,
                                 'amount': amount,
                                 'order_desc': order_desc})

        status = get_order_status(data['response']['order_id'])

        self.assertEqual(status['response']['response_status'], 'success')