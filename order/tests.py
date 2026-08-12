from django.test import TestCase
from unittest.mock import patch

from order.utils import create_new_order
from user_management.models import CustomUser, DeliveryData


class TestCreateNewOrderSync(TestCase):

    def test_create_new_order_sync(self):
        cart_data = {1:1 , 4:2 , 2:4}
        user = CustomUser.objects.get(id=1)
        delivery_address_id = DeliveryData.objects.filter(owner=user)

        result = create_new_order(user, cart_data, delivery_address_id)
        self.assertIsInstance(result)