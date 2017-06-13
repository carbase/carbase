from django.test import TestCase

from .api import get_checkout_url


class CheckoutTestCase(TestCase):

    def test_success_get_checkout_url(self):
        product_id = 'prod-1'
        amount = 50000
        order_desc = 'test_success_get_checkout_url'

        data = get_checkout_url({'product_id':  product_id,
                                 'amount':      amount,
                                 'order_desc':  order_desc})

        self.assertEqual(data['response']['pg_status'], 'ok')

    def test_failed_get_checkout_url_on_thausand_float_amount(self):
        product_id = 'prod-2'
        amount = 50000.00
        order_desc = 'test_failed_get_checkout_url_on_thausand_float_amount'

        data = get_checkout_url({'product_id':  product_id,
                                 'amount':      amount,
                                 'order_desc':  order_desc})

        self.assertEqual(data['response']['pg_status'], 'error')
