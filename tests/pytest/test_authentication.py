"""

Acceptance tests for Authentication (AUTH-001 to AUTH-005).

ASSUMED INTERFACE for the Development repo's authentication.py
(adjust the function name below if Dev uses a different one):

    login(username, password) -> True if authentication succeeds,
                                 False if authentication fails

The authentication system is expected to enforce the following rules:

    AUTH-001: A registered user providing the correct password must be
              authenticated successfully.
    AUTH-002: An unregistered username must be rejected.
    AUTH-003: A registered username with an incorrect password must be
              rejected.
    AUTH-004: Empty credentials, a missing username and a missing password
              must be rejected without causing the system to crash.
    AUTH-005: Basic injection-style input in the username or password field
              must be safely rejected.

These tests cover both positive and negative authentication scenarios.

Positive tests verify that a valid user with the correct credentials is
able to log in.

Negative tests verify that login is denied when the username is unknown,
the password is wrong, the credentials are empty or missing, or the input
contains injection-style content.

The tests do not modify user accounts or project data. They only verify
the result returned by the login() function.
"""
