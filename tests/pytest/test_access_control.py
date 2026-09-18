"""

Acceptance tests for Access Control (AC-001 to AC-005).

ASSUMED INTERFACE for the Development repo's access_control.py
(adjust the function name below if Dev uses a different one):

    check_access(username, action) -> True if access is allowed,
                                     False if access is denied

The access-control system is expected to enforce the following permissions:

    AC-001: Architects can view and edit BIM files.
    AC-002: Engineers can view and edit BIM files.
    AC-003: Contractors can view BIM files but cannot edit them.
    AC-004: Clients can view BIM files but cannot edit them.
    AC-005: Unregistered users, missing usernames, missing actions,
            and unrecognised actions must be denied access.

These tests cover both positive and negative access-control scenarios.

Positive tests verify that authorised roles can perform the actions
they are permitted to perform.

Negative tests verify that users are denied access when they do not
have the required permission or when invalid/incomplete access details
are provided.

The tests do not modify BIM files or project data. They only verify
the permission decisions returned by the check_access() function.
"""
import pytest
 
from access_control import check_access
 


#Access must be granted for the architect to view and be able to edit BIM files.
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
 
 
#Access must be granted for the engineer to be able to view and edit action. 
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
 

#Access must be granted for the contractor to view BIM files but not edit them.
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
 
 