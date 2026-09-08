import pytest
 
from authentication import login

@pytest.mark.auth
@pytest.mark.requirement("AUTH-001")
def test_valid_user_correct_password():
    """AUTH-001: A registered user providing the correct password must be authenticated successfully."""
    result = login("valid_user", "correct_password")
 
    assert result is True
 
 
@pytest.mark.auth
@pytest.mark.negative
@pytest.mark.requirement("AUTH-002")
def test_invalid_username_rejected():
    """AUTH-002: An unregistered username must be rejected."""
    result = login("invalid_user", "correct_password")
 
    assert result is False
 
 
@pytest.mark.auth
@pytest.mark.negative
@pytest.mark.requirement("AUTH-003")
def test_wrong_password_rejected():
    """AUTH-003: A registered username with an incorrect password must be rejected."""
    result = login("valid_user", "wrong_password")
 
    assert result is False
 
 
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
 