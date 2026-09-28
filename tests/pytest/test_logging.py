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
