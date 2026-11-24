"""Small input checks used by the routes."""
import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def clean(value, max_len=255):
    return (value or "").strip()[:max_len]


def to_int(value, default=None):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def to_float(value, default=None):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def valid_name(name):
    return 2 <= len(name) <= 80


def valid_email(email):
    return len(email) <= 120 and bool(EMAIL_RE.match(email))


def valid_phone(phone):
    """Indian mobile number: 10 digits, starts with 6-9."""
    return bool(re.fullmatch(r"[6-9]\d{9}", phone))


def valid_pincode(pincode):
    return bool(re.fullmatch(r"\d{6}", pincode))


def password_error(password):
    """Returns an error message, or None if the password is fine."""
    if len(password) < 8:
        return "Password must be at least 8 characters."
    if len(password) > 100:
        return "Password is too long."
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        return "Password must contain at least one letter and one number."
    return None


def safe_next(url):
    """Only allow redirects inside our own site."""
    if url and url.startswith("/") and not url.startswith("//") and "\\" not in url:
        return url
    return None
