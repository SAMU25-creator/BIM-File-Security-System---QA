import pytest

from authentication import login


def test_valid_user_correct_password():
    result = login("valid_user", "correct_password")

    assert result is True