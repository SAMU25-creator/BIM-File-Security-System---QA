"""
test_logging.py

Acceptance tests for Logging (LOG-001 to LOG-004).

ASSUMED INTERFACE for the Development repo's audit_log.py
(adjust the names and field constants below if Dev uses different ones;
the module is not called logging.py so it does not clash with Python's
built-in logging module):

    get_log_entries() -> list of log entries, oldest first. Each entry is a
                         dict with the fields named in the FIELD_* constants.
    clear_log()       -> empties the log, so every test starts clean.

    login(username, password)                  (authentication.py)
        must write a log entry for every attempt.
    access_file(username, action, filename)    (access_control.py)
        -> True if allowed, False if denied. It uses check_access() to
        decide and must write a log entry for every attempt.

The logging system is expected to enforce the following rules:

    LOG-001: Every login attempt, successful or failed, creates a log entry.
    LOG-002: Every file access attempt, allowed or denied, creates a log
             entry.
    LOG-003: Log entries contain who, what action, which file, and when.
    LOG-004: Denied actions are logged as denied, not silently dropped.

These tests cover both positive and negative logging scenarios.

Positive tests verify that attempts which succeed (a valid login, an
allowed file access) are recorded with the correct details.

Negative tests verify that attempts which fail (a wrong password, an
unknown user, a denied edit) are still recorded, and are marked as denied
rather than disappearing from the log.

The tests do not modify BIM files or user accounts. They only inspect the
entries written to the log. The log is cleared before every test.
"""
import time

import pytest

audit_log = pytest.importorskip(
    "audit_log", reason="audit_log.py not yet implemented in the Development repo"
)

from authentication import login
from access_control import access_file

get_log_entries = audit_log.get_log_entries
clear_log = audit_log.clear_log

# Field names used inside a log entry 
FIELD_USER = "username"
FIELD_ACTION = "action"
FIELD_FILE = "file"
FIELD_TIME = "timestamp"
FIELD_RESULT = "result"

# Values used in the result field 
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


# LOG-001: A successful login must create exactly one log entry.
@pytest.mark.logging
@pytest.mark.requirement("LOG-001")
def test_successful_login_is_logged():
    """LOG-001: A successful login creates a log entry recording who logged in."""
    login("valid_user", "correct_password")

    entries = get_log_entries()

    assert len(entries) == 1
    assert entries[0][FIELD_USER] == "valid_user"
    assert entries[0][FIELD_RESULT] == RESULT_SUCCESS


# LOG-001: A failed login with the wrong password must still be logged.
@pytest.mark.logging
@pytest.mark.negative
@pytest.mark.requirement("LOG-001")
def test_failed_login_wrong_password_is_logged():
    """LOG-001: A failed login (wrong password) creates a log entry marked as a failure."""
    login("valid_user", "wrong_password")

    entries = get_log_entries()

    assert len(entries) == 1
    assert entries[0][FIELD_USER] == "valid_user"
    assert entries[0][FIELD_RESULT] == RESULT_FAILURE


# LOG-001: A failed login for an unknown username must still be logged.
@pytest.mark.logging
@pytest.mark.negative
@pytest.mark.requirement("LOG-001")
def test_failed_login_unknown_user_is_logged():
    """LOG-001: A failed login (unregistered username) creates a log entry marked as a failure."""
    login("invalid_user", "correct_password")

    entries = get_log_entries()

    assert len(entries) == 1
    assert entries[0][FIELD_USER] == "invalid_user"
    assert entries[0][FIELD_RESULT] == RESULT_FAILURE


# Each login attempt must add its own entry, so repeated attempts are all visible.
@pytest.mark.logging
@pytest.mark.requirement("LOG-001")
def test_every_login_attempt_adds_one_entry():
    """LOG-001: Three login attempts (one success, two failures) create three log entries."""
    login("valid_user", "correct_password")
    login("valid_user", "wrong_password")
    login("invalid_user", "correct_password")

    assert len(get_log_entries()) == 3


# LOG-002: An allowed file access must create a log entry.
@pytest.mark.logging
@pytest.mark.requirement("LOG-002")
def test_allowed_file_access_is_logged():
    """LOG-002: An allowed file access (architect views a file) creates a log entry."""
    access_file("architect", "view", BIM_FILE)

    entries = get_log_entries()

    assert len(entries) == 1
    assert entries[0][FIELD_USER] == "architect"
    assert entries[0][FIELD_RESULT] == RESULT_ALLOWED


# LOG-002: A denied file access must create a log entry as well.
@pytest.mark.logging
@pytest.mark.negative
@pytest.mark.requirement("LOG-002")
def test_denied_file_access_is_logged():
    """LOG-002: A denied file access (contractor edits a file) creates a log entry."""
    access_file("contractor", "edit", BIM_FILE)

    entries = get_log_entries()

    assert len(entries) == 1
    assert entries[0][FIELD_USER] == "contractor"


# LOG-002: A denied access from an unregistered user must be logged too.
@pytest.mark.logging
@pytest.mark.negative
@pytest.mark.requirement("LOG-002")
def test_unregistered_user_access_attempt_is_logged():
    """LOG-002: An access attempt by an unregistered user creates a log entry."""
    access_file("unregistered_user", "view", BIM_FILE)

    entries = get_log_entries()

    assert len(entries) == 1
    assert entries[0][FIELD_USER] == "unregistered_user"


# LOG-003: A file access entry must record who, what action, which file, and when.
@pytest.mark.logging
@pytest.mark.requirement("LOG-003")
def test_file_access_entry_contains_who_action_file_and_time():
    """LOG-003: A file access log entry contains the user, the action, the file, and a timestamp."""
    access_file("engineer", "edit", BIM_FILE)

    entry = get_log_entries()[0]

    assert entry[FIELD_USER] == "engineer"
    assert entry[FIELD_ACTION] == "edit"
    assert entry[FIELD_FILE] == BIM_FILE
    assert entry[FIELD_TIME] not in (None, "")


# LOG-003: The log entry must show who was acting, not just that something happened.
@pytest.mark.logging
@pytest.mark.requirement("LOG-003")
def test_login_entry_contains_who_and_time():
    """LOG-003: A login log entry contains the username and a timestamp."""
    login("valid_user", "correct_password")

    entry = get_log_entries()[0]

    assert entry[FIELD_USER] == "valid_user"
    assert entry[FIELD_TIME] not in (None, "")


# LOG-003: The timestamp must reflect when the attempt actually happened.
@pytest.mark.logging
@pytest.mark.requirement("LOG-003")
def test_log_timestamp_matches_time_of_attempt():
    """LOG-003: The timestamp falls between just before and just after the attempt."""
    before = time.time()
    access_file("architect", "view", BIM_FILE)
    after = time.time()

    logged_time = get_log_entries()[0][FIELD_TIME]

    # Accepts a numeric timestamp (seconds) or a datetime object.
    if hasattr(logged_time, "timestamp"):
        logged_time = logged_time.timestamp()

    assert before <= logged_time <= after


# LOG-004: A denied edit must be recorded as denied, not as allowed or left out.
@pytest.mark.logging
@pytest.mark.negative
@pytest.mark.requirement("LOG-004")
def test_denied_edit_is_logged_as_denied():
    """LOG-004: A client's denied edit is logged with the result 'denied'."""
    access_file("client", "edit", BIM_FILE)

    entry = get_log_entries()[0]

    assert entry[FIELD_RESULT] == RESULT_DENIED
    assert entry[FIELD_ACTION] == "edit"
    assert entry[FIELD_FILE] == BIM_FILE


# LOG-004: An unrecognised action is denied, and that denial must be logged.
@pytest.mark.logging
@pytest.mark.negative
@pytest.mark.requirement("LOG-004")
def test_unrecognised_action_is_logged_as_denied():
    """LOG-004: A denied unrecognised action (architect 'delete') is logged with the result 'denied'."""
    access_file("architect", "delete", BIM_FILE)

    entry = get_log_entries()[0]

    assert entry[FIELD_RESULT] == RESULT_DENIED


