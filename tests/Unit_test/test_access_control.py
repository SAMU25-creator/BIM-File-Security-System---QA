import pytest

from access_control import check_access


def test_architect_can_view():
    result = check_access("architect", "view")

    assert result is True


def test_architect_can_edit():
    result = check_access("architect", "edit")

    assert result is True


def test_engineer_can_view():
    result = check_access("engineer", "view")

    assert result is True


def test_engineer_can_edit():
    result = check_access("engineer", "edit")

    assert result is True


