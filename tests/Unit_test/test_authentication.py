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