from django.test import TestCase
from orbit.tasks import send_birthday_wishes
from orbit.models import CustomUser
from datetime import date

class BirthdayTaskTest(TestCase):
    def test_birthday_email(self):
        user = CustomUser.objects.create_user(
            username="test_user",
            email="test@example.com",
            birthday=date.today()
        )
        result = send_birthday_wishes()
        self.assertEqual(result, "Birthday wishes sent to 1 users")