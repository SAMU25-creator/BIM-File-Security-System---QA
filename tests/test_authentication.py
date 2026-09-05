from authentication import login


def test_valid_user_correct_password():
    result = login("valid_user", "correct_password")

    assert result is True

def test_invalid_username_rejected():
    result = login("invalid_user", "correct_password")

    assert result is False

def test_wrong_password_rejected():
    result = login("valid_user", "wrong_password")

    assert result is False 

def test_empty_credentials_rejected():
    result = login("", "")

    assert result is False


def test_missing_username_rejected():
    result = login(None, "correct_password")

    assert result is False


def test_missing_password_rejected():
    result = login("valid_user", None)

    assert result is False


def test_sql_injection_in_username_rejected():
    result = login("' OR '1'='1", "correct_password")

    assert result is False


def test_sql_injection_in_password_rejected():
    result = login("valid_user", "' OR '1'='1")

    assert result is False