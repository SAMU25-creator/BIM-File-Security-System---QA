import time

import pytest

# Assumed Dev interface (same as the acceptance tests): audit_log.py with
# get_log_entries() and clear_log(), plus login() and access_file().
audit_log = pytest.importorskip(
    "audit_log", reason="audit_log.py not yet implemented in the Development repo"
)

from authentication import login
from access_control import access_file

get_log_entries = audit_log.get_log_entries
clear_log = audit_log.clear_log

# Field names and result values (adjust if Dev uses different ones).
FIELD_USER = "username"
FIELD_ACTION = "action"
FIELD_FILE = "file"
FIELD_TIME = "timestamp"
FIELD_RESULT = "result"

RESULT_SUCCESS = "success"
RESULT_FAILURE = "failure"
RESULT_ALLOWED = "allowed"
RESULT_DENIED = "denied"

BIM_FILE = "building_model.ifc"


# Start every test with an empty log so entries from other tests cannot interfere.
@pytest.fixture(autouse=True)
def empty_log():
    clear_log()
    yield
    clear_log()


# The log must be empty before anything happens.
def test_log_starts_empty():
    """Fresh log: no entries exist until an attempt is made."""
    assert get_log_entries() == []


# clear_log() must remove every entry that was written.
def test_clear_log_removes_entries():
    """After clear_log(): entries written earlier are gone."""
    login("valid_user", "correct_password")
    clear_log()

    assert get_log_entries() == []


# A successful login must add exactly one entry.
def test_successful_login_adds_one_entry():
    """Successful login: one log entry is added."""
    login("valid_user", "correct_password")

    assert len(get_log_entries()) == 1


# A successful login must be recorded as a success.
def test_successful_login_result_is_success():
    """Successful login: the entry's result is 'success'."""
    login("valid_user", "correct_password")

    assert get_log_entries()[0][FIELD_RESULT] == RESULT_SUCCESS


# A login with the wrong password must still add an entry.
def test_wrong_password_adds_one_entry():
    """Wrong password: one log entry is added."""
    login("valid_user", "wrong_password")

    assert len(get_log_entries()) == 1


# A login with the wrong password must be recorded as a failure.
def test_wrong_password_result_is_failure():
    """Wrong password: the entry's result is 'failure'."""
    login("valid_user", "wrong_password")

    assert get_log_entries()[0][FIELD_RESULT] == RESULT_FAILURE


# A login with an unknown username must still add an entry.
def test_unknown_username_adds_one_entry():
    """Unregistered username: one log entry is added."""
    login("invalid_user", "correct_password")

    assert len(get_log_entries()) == 1


# The login entry must record which username was used.
def test_login_entry_records_username():
    """Login entry: the username used is recorded."""
    login("invalid_user", "correct_password")

    assert get_log_entries()[0][FIELD_USER] == "invalid_user"


# Empty credentials must be logged without the system crashing.
def test_empty_credentials_logged_without_crashing():
    """Empty username and password: login is logged, no crash."""
    login("", "")

    assert len(get_log_entries()) == 1


# Each login attempt must add its own entry.
def test_each_login_attempt_adds_its_own_entry():
    """Three login attempts: three log entries."""
    login("valid_user", "correct_password")
    login("valid_user", "wrong_password")
    login("invalid_user", "correct_password")

    assert len(get_log_entries()) == 3


# Entries must be stored in the order the attempts happened.
def test_entries_are_in_order_of_attempts():
    """Two login attempts: the first attempt is the first entry."""
    login("valid_user", "correct_password")
    login("invalid_user", "correct_password")

    entries = get_log_entries()

    assert entries[0][FIELD_USER] == "valid_user"
    assert entries[1][FIELD_USER] == "invalid_user"


# An allowed file access must add one entry.
def test_allowed_access_adds_one_entry():
    """Allowed file access: one log entry is added."""
    access_file("architect", "view", BIM_FILE)

    assert len(get_log_entries()) == 1


# An allowed file access must be recorded as allowed.
def test_allowed_access_result_is_allowed():
    """Allowed file access: the entry's result is 'allowed'."""
    access_file("architect", "view", BIM_FILE)

    assert get_log_entries()[0][FIELD_RESULT] == RESULT_ALLOWED


# A denied file access must add one entry, not be silently dropped.
def test_denied_access_adds_one_entry():
    """Denied file access: one log entry is added."""
    access_file("contractor", "edit", BIM_FILE)

    assert len(get_log_entries()) == 1


# A denied file access must be recorded as denied.
def test_denied_access_result_is_denied():
    """Denied file access: the entry's result is 'denied'."""
    access_file("contractor", "edit", BIM_FILE)

    assert get_log_entries()[0][FIELD_RESULT] == RESULT_DENIED


# A denied edit by a client must be recorded as denied.
def test_client_denied_edit_is_logged_as_denied():
    """Client edit: logged as 'denied'."""
    access_file("client", "edit", BIM_FILE)

    assert get_log_entries()[0][FIELD_RESULT] == RESULT_DENIED


