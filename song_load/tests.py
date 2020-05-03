from django.test import TestCase


class TestCaseStub(TestCase):
    def test_always_success(self):
        self.assertTrue(True)
