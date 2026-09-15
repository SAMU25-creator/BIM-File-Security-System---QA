"""
Unit tests for session.py (session security).

Assumed interface (same as tests/pytest/test_session_security.py):

    create_session(username) -> token (non-empty str)
    validate_session(token)  -> True if the session is active, else False
    logout(token)            -> ends the session

Inactivity expiry is tested by moving the clock forward, so session.py
must read time via `time.time()` (i.e. `import time` in session.py).
"""

