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

