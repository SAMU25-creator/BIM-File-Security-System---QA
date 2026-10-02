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


