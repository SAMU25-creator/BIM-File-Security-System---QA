"""

Acceptance tests for Authentication (AUTH-001 to AUTH-005).

ASSUMED INTERFACE for the Development repo's authentication.py
(adjust the function name below if Dev uses a different one):

    login(username, password) -> True if authentication succeeds,
                                 False if authentication fails

The authentication system is expected to enforce the following rules:

    AUTH-001: A registered user providing the correct password must be
              authenticated successfully.
    AUTH-002: An unregistered username must be rejected.
    AUTH-003: A registered username with an incorrect password must be
              rejected.
    AUTH-004: Empty credentials, a missing username and a missing password
              must be rejected without causing the system to crash.
    AUTH-005: Basic injection-style input in the username or password field
              must be safely rejected.

These tests cover both positive and negative authentication scenarios.

Positive tests verify that a valid user with the correct credentials is
able to log in.

Negative tests verify that login is denied when the username is unknown,
the password is wrong, the credentials are empty or missing, or the input
contains injection-style content.

The tests do not modify user accounts or project data. They only verify
the result returned by the login() function.
"""
import pytest

from authentication import login


# A registered user with the correct password must be authenticated.
@pytest.mark.auth
@pytest.mark.requirement("AUTH-001")
def test_valid_user_correct_password():
    """AUTH-001: A registered user providing the correct password must be authenticated successfully."""
    result = login("valid_user", "correct_password")

    assert result is True


# An unregistered username must be rejected, even with a correct-looking password.
@pytest.mark.auth
@pytest.mark.negative
@pytest.mark.requirement("AUTH-002")
def test_invalid_username_rejected():
    """AUTH-002: An unregistered username must be rejected."""
    result = login("invalid_user", "correct_password")

    assert result is False


# A registered username with the wrong password must be rejected.
@pytest.mark.auth
@pytest.mark.negative
@pytest.mark.requirement("AUTH-003")
def test_wrong_password_rejected():
    """AUTH-003: A registered username with an incorrect password must be rejected."""
    result = login("valid_user", "wrong_password")

    assert result is False


# Empty or missing credentials must be rejected without crashing the system.
@pytest.mark.auth
@pytest.mark.negative
@pytest.mark.requirement("AUTH-004")
def test_empty_credentials_rejected():
    """AUTH-004: Empty credentials must be rejected without causing the system to crash."""
    result = login("", "")

    assert result is False


@pytest.mark.auth
@pytest.mark.negative
@pytest.mark.requirement("AUTH-004")
def test_missing_username_rejected():
    """AUTH-004: A missing (None) username must be rejected without causing the system to crash."""
    result = login(None, "correct_password")

    assert result is False


@pytest.mark.auth
@pytest.mark.negative
@pytest.mark.requirement("AUTH-004")
def test_missing_password_rejected():
    """AUTH-004: A missing (None) password must be rejected without causing the system to crash."""
    result = login("valid_user", None)

    assert result is False


# Injection-style input in either field must be safely rejected, not interpreted.
@pytest.mark.auth
@pytest.mark.negative
@pytest.mark.requirement("AUTH-005")
def test_sql_injection_in_username_rejected():
    """AUTH-005: Basic injection-style input in the username field must be safely rejected."""
    result = login("' OR '1'='1", "correct_password")

    assert result is False


@pytest.mark.auth
@pytest.mark.negative
@pytest.mark.requirement("AUTH-005")
def test_sql_injection_in_password_rejected():
    """AUTH-005: Basic injection-style input in the password field must be safely rejected."""
    result = login("valid_user", "' OR '1'='1")

    assert result is False
