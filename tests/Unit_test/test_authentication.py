import pytest

from authentication import login


# A registered user with the correct password must be logged in successfully.
def test_valid_user_correct_password():
    """Valid username and correct password: login succeeds."""
    result = login("valid_user", "correct_password")

    assert result is True


# A username that is not registered must be rejected, even if the password looks correct.
def test_invalid_username_rejected():
    """Unregistered username: login is denied."""
    result = login("invalid_user", "correct_password")

    assert result is False


# A registered user with the wrong password must be rejected.
def test_wrong_password_rejected():
    """Valid username but wrong password: login is denied."""
    result = login("valid_user", "wrong_password")

    assert result is False


# Empty credentials must be rejected without the system crashing.
def test_empty_credentials_rejected():
    """Empty username and password: login is denied, no crash."""
    result = login("", "")

    assert result is False


# A missing (None) username must be rejected without the system crashing.
def test_missing_username_rejected():
    """Missing username (None): login is denied, no crash."""
    result = login(None, "correct_password")

    assert result is False


# A missing (None) password must be rejected without the system crashing.
def test_missing_password_rejected():
    """Missing password (None): login is denied, no crash."""
    result = login("valid_user", None)

    assert result is False


# Injection-style input in the username field must be treated as plain text and rejected.
def test_sql_injection_in_username_rejected():
    """SQL injection string in username: login is denied."""
    result = login("' OR '1'='1", "correct_password")

    assert result is False


# Injection-style input in the password field must be treated as plain text and rejected.
def test_sql_injection_in_password_rejected():
    """SQL injection string in password: login is denied."""
    result = login("valid_user", "' OR '1'='1")

    assert result is False