import pytest
 
from access_control import check_access
 
 
@pytest.mark.access_control
@pytest.mark.requirement("AC-001")
def test_architect_can_view():
    """AC-001: Architect can view."""
    result = check_access("architect", "view")
 
    assert result is True
 
 
@pytest.mark.access_control
@pytest.mark.requirement("AC-001")
def test_architect_can_edit():
    """AC-001: Architect can edit."""
    result = check_access("architect", "edit")
 
    assert result is True
 
 
@pytest.mark.access_control
@pytest.mark.requirement("AC-002")
def test_engineer_can_view():
    """AC-002: Engineer can view."""
    result = check_access("engineer", "view")
 
    assert result is True
 
 
@pytest.mark.access_control
@pytest.mark.requirement("AC-002")
def test_engineer_can_edit():
    """AC-002: Engineer can edit."""
    result = check_access("engineer", "edit")
 
    assert result is True
 
 
@pytest.mark.access_control
@pytest.mark.requirement("AC-003")
def test_contractor_can_view():
    """AC-003: Contractor can view."""
    result = check_access("contractor", "view")
 
    assert result is True
 
 
@pytest.mark.access_control
@pytest.mark.negative
@pytest.mark.requirement("AC-003")
def test_contractor_cannot_edit():
    """AC-003: Contractor is denied edit, not just hidden from it."""
    result = check_access("contractor", "edit")
 
    assert result is False
 
 
@pytest.mark.access_control
@pytest.mark.requirement("AC-004")
def test_client_can_view():
    """AC-004: Client can view."""
    result = check_access("client", "view")
 
    assert result is True
 
 
@pytest.mark.access_control
@pytest.mark.negative
@pytest.mark.requirement("AC-004")
def test_client_cannot_edit():
    """AC-004: Client is denied edit, not just hidden from it."""
    result = check_access("client", "edit")
 
    assert result is False
 
 
@pytest.mark.access_control
@pytest.mark.negative
@pytest.mark.requirement("AC-005")
def test_unauthorised_user_cannot_view():
    """AC-005: An unregistered/unknown user is denied view."""
    result = check_access("unregistered_user", "view")
 
    assert result is False
 
 
@pytest.mark.access_control
@pytest.mark.negative
@pytest.mark.requirement("AC-005")
def test_unauthorised_user_cannot_edit():
    """AC-005: An unregistered/unknown user is denied edit."""
    result = check_access("unregistered_user", "edit")
 
    assert result is False
 
 
@pytest.mark.access_control
@pytest.mark.negative
@pytest.mark.requirement("AC-005")
def test_missing_username_rejected():
    """AC-005: A missing (None) username must be rejected without crashing."""
    result = check_access(None, "view")
 
    assert result is False
 
 
@pytest.mark.access_control
@pytest.mark.negative
@pytest.mark.requirement("AC-005")
def test_missing_action_rejected():
    """AC-005: A missing (None) action must be rejected without crashing."""
    result = check_access("architect", None)
 
    assert result is False
 
 
@pytest.mark.access_control
@pytest.mark.negative
def test_unrecognised_action_rejected():
    """An action outside view/edit (e.g. 'delete') must be denied."""
    result = check_access("architect", "delete")
 
    assert result is False
 