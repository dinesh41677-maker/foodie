import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import validators as v


def test_phone():
    assert v.valid_phone("9876543210")
    assert not v.valid_phone("1234567890")
    assert not v.valid_phone("98765")
    assert not v.valid_phone("98765abcde")


def test_email():
    assert v.valid_email("a@b.com")
    assert not v.valid_email("not-an-email")


def test_password():
    assert v.password_error("short1")
    assert v.password_error("onlyletters")
    assert v.password_error("12345678")
    assert v.password_error("Good1234") is None


def test_pincode():
    assert v.valid_pincode("636001")
    assert not v.valid_pincode("63600")


def test_safe_next():
    assert v.safe_next("/cart") == "/cart"
    assert v.safe_next("//evil.com") is None
    assert v.safe_next("https://evil.com") is None
