"""
Unit tests for session.py (session security).

Assumed interface (same as tests/pytest/test_session_security.py):

    create_session(username) -> token (non-empty str)
    validate_session(token)  -> True if the session is active, else False
    logout(token)            -> ends the session

Inactivity expiry is tested by moving the clock forward, so session.py
must read time via `time.time()` (i.e. `import time` in session.py).
"""

import time

import pytest

session = pytest.importorskip(
    "session", 
    reason="session.py not yet implemented in the Development repo"
)

create_session = session.create_session
validate_session = session.validate_session
logout = session.logout

# Use the application's configured timeout when available.
# Otherwise, default to 30 minutes.
TIMEOUT = getattr(session, "SESSION_TIMEOUT", 30 * 60)


@pytest.fixture
def fake_clock(monkeypatch):
    """Advance time without sleeping."""
    real_time = time.time
    offset = {"seconds": 0}

    # Replace time.time() with a controllable clock
    monkeypatch.setattr(time, "time", lambda: real_time() + offset["seconds"])

    def advance(seconds):
        offset["seconds"] += seconds

    return advance


# ---------------------------------------------------------------------------
# Session creation
# ---------------------------------------------------------------------------

def test_create_session_returns_non_empty_string():
    """A newly created session should return a non-empty string token."""
    token = create_session("architect")

    assert isinstance(token, str)
    assert token != ""


def test_new_session_is_valid():
    """A newly created session should immediately be considered active."""
    token = create_session("architect")

    assert validate_session(token) is True


def test_two_sessions_get_different_tokens():
    """Creating two sessions should produce different tokens."""
    token_a = create_session("architect")
    token_b = create_session("architect")

    assert token_a != token_b


def test_many_sessions_all_get_unique_tokens():
    """Multiple sessions should each receive a unique token."""
    tokens = {create_session("engineer") for _ in range(50)}

    assert len(tokens) == 50


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------


def test_logout_ends_session():
    """Logging out should make the session token invalid."""
    token = create_session("engineer")
    logout(token)

    assert validate_session(token) is False


def test_logout_does_not_end_another_session():
    """Logging out one session should not affect another active session."""
    token_a = create_session("architect")
    token_b = create_session("client")
    logout(token_a)

    assert validate_session(token_a) is False
    assert validate_session(token_b) is True


def test_logged_out_token_stays_rejected():
    """A token should remain invalid after the session has been logged out."""
    token = create_session("architect")
    logout(token)

    assert validate_session(token) is False
    assert validate_session(token) is False


def test_logout_twice_does_not_crash():
    """Logging out the same token twice should not raise an exception."""
    token = create_session("architect")
    logout(token)
    logout(token)

    assert validate_session(token) is False


# ---------------------------------------------------------------------------
# Inactivity expiry
# ---------------------------------------------------------------------------

def test_session_expires_after_timeout(fake_clock):
    """A session should become invalid after exceeding the inactivity timeout."""
    token = create_session("contractor")
    fake_clock(TIMEOUT + 1)

    assert validate_session(token) is False


def test_session_valid_just_before_timeout(fake_clock):
    """A session should remain valid when checked shortly before expiry."""
    token = create_session("contractor")
    fake_clock(TIMEOUT - 5)

    assert validate_session(token) is True


def test_expired_token_stays_rejected(fake_clock):
    """An expired token should remain invalid when validated repeatedly."""
    token = create_session("client")
    fake_clock(TIMEOUT + 1)

    assert validate_session(token) is False
    assert validate_session(token) is False


def test_new_session_after_expiry_is_valid(fake_clock):
    """A new session should be valid even after an older session has expired."""
    old_token = create_session("client")
    fake_clock(TIMEOUT + 1)
    new_token = create_session("client")

    assert validate_session(old_token) is False
    assert validate_session(new_token) is True


# ---------------------------------------------------------------------------
# Invalid and malformed tokens
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "bad_token",
    [
        None,
        "",
        "   ",
        "not-a-real-token",
        "' OR '1'='1",
        12345,
        [],
        {},
    ],
)
def test_invalid_token_rejected_without_crash(bad_token):
    """Invalid or malformed tokens should be rejected safely."""
    result = validate_session(bad_token)

    assert result is False


@pytest.mark.parametrize("bad_token", [None, "", "not-a-real-token"])
def test_logout_with_invalid_token_does_not_crash(bad_token):
    """Logging out with an invalid token should not raise an exception."""
    logout(bad_token)  # must not raise