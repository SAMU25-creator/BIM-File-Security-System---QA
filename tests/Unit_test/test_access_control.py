import pytest

from access_control import check_access


# Test that an architect is allowed to view files.
def test_architect_can_view():
    result = check_access("architect", "view")

    assert result is True

#Test that an architect is allowed to edit files.
def test_architect_can_edit():
    result = check_access("architect", "edit")

    assert result is True

# Test that an engineer is allowed to view files.
def test_engineer_can_view():
    result = check_access("engineer", "view")

    assert result is True

def test_engineer_can_edit():
    result = check_access("engineer", "edit")

    assert result is True

# Test that a contractor is allowed to view files.
def test_contractor_can_view():
    result = check_access("contractor", "view")

    assert result is True


def test_contractor_cannot_edit():
    result = check_access("contractor", "edit")

    assert result is False

# Test that a client is allowed to view files.
def test_client_can_view():
    result = check_access("client", "view")

    assert result is True


def test_client_cannot_edit():
    result = check_access("client", "edit")

    assert result is False

# Test that an unregistered user cannot view and edit the files.
def test_unauthorised_user_cannot_view():
    result = check_access("unregistered_user", "view")

    assert result is False

def test_unauthorised_user_cannot_edit():
    result = check_access("unregistered_user", "edit")

    assert result is False

# Test that access is denied when the username is missing.
def test_missing_username_rejected():
    result = check_access(None, "view")

    assert result is False

# Test that access is denied when the action is missing.
def test_missing_action_rejected():
    result = check_access("architect", None)

    assert result is False

# Test that an unsupported action, such as "delete", is rejected.
def test_unrecognised_action_rejected():
    result = check_access("architect", "delete")

    assert result is False