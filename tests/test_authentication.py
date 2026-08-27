from authentication import login


def test_valid_user_correct_password():
    result = login("valid_user", "correct_password")

    assert result is True

def test_invalid_username_rejected():
    result = login("invalid_user", "correct_password")

    assert result is False