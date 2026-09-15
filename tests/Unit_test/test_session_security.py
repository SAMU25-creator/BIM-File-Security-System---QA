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
    "session", reason="session.py not yet implemented in the Development repo"
)

create_session = session.create_session
validate_session = session.validate_session
logout = session.logout

# Inactivity timeout (seconds). Uses Dev's constant if one exists.
TIMEOUT = getattr(session, "SESSION_TIMEOUT", 30 * 60)


@pytest.fixture
def fake_clock(monkeypatch):
    """Advance time without sleeping."""
    real_time = time.time
    offset = {"seconds": 0}
    monkeypatch.setattr(time, "time", lambda: real_time() + offset["seconds"])

    def advance(seconds):
        offset["seconds"] += seconds

    return advance


# --- Creating sessions ---

def test_create_session_returns_non_empty_string():
    token = create_session("architect")

    assert isinstance(token, str)
    assert token != ""


def test_new_session_is_valid():
    token = create_session("architect")

    assert validate_session(token) is True


def test_two_sessions_get_different_tokens():
    token_a = create_session("architect")
    token_b = create_session("architect")

    assert token_a != token_b


def test_many_sessions_all_get_unique_tokens():
    tokens = {create_session("engineer") for _ in range(50)}

    assert len(tokens) == 50


