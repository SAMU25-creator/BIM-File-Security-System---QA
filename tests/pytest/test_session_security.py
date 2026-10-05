"""
test_session_security.py

Acceptance tests for Session Security (SESS-001 to SESS-005).

ASSUMED INTERFACE for the Development repo's session.py
(adjust the three names below if Dev uses different ones):

    create_session(username) -> token (non-empty str)
    validate_session(token)  -> True if the session is active, else False
    logout(token)            -> ends the session

Inactivity expiry is tested by moving the clock forward, so session.py
must read time via `time.time()` (i.e. `import time` in session.py).
If Dev exposes a timeout constant, set SESSION_TIMEOUT_ATTR below.
"""

import time

import pytest

session = pytest.importorskip(
    "session", reason="session.py not yet implemented in the Development repo"
)

create_session = session.create_session
validate_session = session.validate_session
logout = session.logout

# Name of the inactivity timeout constant in session.py (seconds), if any.
SESSION_TIMEOUT_ATTR = "SESSION_TIMEOUT"
FALLBACK_TIMEOUT = 30 * 60  # used if Dev exposes no constant


def _timeout():
    return getattr(session, SESSION_TIMEOUT_ATTR, FALLBACK_TIMEOUT)


@pytest.fixture
def fake_clock(monkeypatch):
    """Lets a test advance time without sleeping."""
    real_time = time.time
    offset = {"seconds": 0}
    monkeypatch.setattr(time, "time", lambda: real_time() + offset["seconds"])

    def advance(seconds):
        offset["seconds"] += seconds

    return advance


@pytest.mark.session
@pytest.mark.requirement("SESS-001")
def test_new_session_is_valid():
    """SESS-001: A session created for a user is valid straight away."""
    token = create_session("architect")

    assert isinstance(token, str) and token
    assert validate_session(token) is True


@pytest.mark.session
@pytest.mark.requirement("SESS-001")
def test_sessions_get_unique_tokens():
    """SESS-001: Two sessions must never share a token."""
    assert create_session("architect") != create_session("architect")


@pytest.mark.session
@pytest.mark.negative
@pytest.mark.requirement("SESS-002")
def test_logout_ends_session():
    """SESS-002: After logout, the old session token no longer works."""
    token = create_session("engineer")
    logout(token)

    assert validate_session(token) is False


@pytest.mark.session
@pytest.mark.negative
@pytest.mark.requirement("SESS-002")
def test_logout_only_ends_own_session():
    """SESS-002: Logging out one session must not end another user's session."""
    token_a = create_session("architect")
    token_b = create_session("client")
    logout(token_a)

    assert validate_session(token_a) is False
    assert validate_session(token_b) is True


@pytest.mark.session
@pytest.mark.negative
@pytest.mark.requirement("SESS-003")
def test_session_expires_after_inactivity(fake_clock):
    """SESS-003: A session left idle past the timeout is rejected."""
    token = create_session("contractor")
    fake_clock(_timeout() + 1)

    assert validate_session(token) is False


@pytest.mark.session
@pytest.mark.requirement("SESS-003")
def test_session_valid_just_before_timeout(fake_clock):
    """SESS-003: A session is still valid while inside the timeout window."""
    token = create_session("contractor")
    fake_clock(_timeout() - 5)

    assert validate_session(token) is True


@pytest.mark.session
@pytest.mark.negative
@pytest.mark.requirement("SESS-004")
def test_expired_token_stays_rejected(fake_clock):
    """SESS-004: An expired token is rejected on every reuse attempt."""
    token = create_session("client")
    fake_clock(_timeout() + 1)

    assert validate_session(token) is False
    assert validate_session(token) is False


@pytest.mark.session
@pytest.mark.negative
@pytest.mark.requirement("SESS-004")
def test_logged_out_token_stays_rejected():
    """SESS-004: A logged-out token cannot be reused, even repeatedly."""
    token = create_session("architect")
    logout(token)

    assert validate_session(token) is False
    assert validate_session(token) is False


@pytest.mark.session
@pytest.mark.negative
@pytest.mark.requirement("SESS-005")
@pytest.mark.parametrize(
    "bad_token",
    [None, "", "not-a-real-token", "' OR '1'='1", 12345],
)
def test_invalid_token_rejected_without_crash(bad_token):
    """SESS-005: Missing, unknown, or malformed tokens are rejected, never a crash."""
    assert validate_session(bad_token) is False


@pytest.mark.session
@pytest.mark.negative
@pytest.mark.requirement("SESS-005")
def test_logout_with_invalid_token_does_not_crash():
    """SESS-005: Logging out with a bad token must fail safely."""
    for bad_token in (None, "", "not-a-real-token"):
        logout(bad_token)  # must not raise