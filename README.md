# BIM File Security System — QA

Automated test suite that independently verifies the BIM File Security System's authentication, access control, logging, encryption, and session security.

This repo contains requirements and tests only. The system under test — `authentication.py`, `access_control.py`, and the rest — lives in the separate Development repository, `BIM-File-Security-System`. Tests import its modules directly and call the functions themselves; there is no running server or HTTP layer involved.

> System under test: `BIM-File-Security-System`

## Getting started

Requires Python 3.11+ and Git.

```bash
git clone <qa-repo-url>
cd BIM-File-Security-System---QA
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install pytest
```

Tests import the Development repo's modules (`from authentication import login`, `from access_control import check_access`, etc.), so that repo needs to be on the Python path. `conftest.py` currently does this with a hardcoded path to one contributor's machine — anyone else running the suite will need to update it, ideally to something portable (e.g. a relative path, or a `DEV_REPO_PATH` environment variable) rather than a machine-specific one.

## Running tests

```bash
pytest tests/pytest                      # acceptance suite (requirement-tagged)
pytest tests/Unit_test                   # unit suite
pytest tests/pytest/test_authentication.py   # one file
pytest -m requirement                    # anything tagged with a requirement ID
pytest -k "unauthorised"                 # one test by name
```

Markers currently in use: `auth`, `access_control`, `negative`, `requirement("<ID>")`. These aren't registered in `pytest.ini` yet, so pytest will emit `PytestUnknownMarkWarning` for each — harmless, but worth registering (see `pytest.ini` below) to clean up test output.

## Structure

```
Requirements/            Documented requirements, one file per area
    authentication.md
    access-control.md
    logging.md
    encryption.md

tests/
    pytest/               Acceptance tests, tagged with requirement IDs (AUTH-00X, AC-00X, ...)
        test_authentication.py
        test_access-control.py
        test_session_security.py   (stub — not yet written)
        test_encryption.py         (stub — not yet written)
        test_logging.py            (stub — not yet written)
    Unit_test/            Plainer function-level tests, same coverage as pytest/ so far
        test_authentication.py
        test_access_control.py
        test_session.py            (stub — not yet written)
        test_session_security.py   (stub — not yet written)
        test_encryption.py         (stub — not yet written)
        test_logging.py            (stub — not yet written)

conftest.py               Adds the Development repo to sys.path (currently a hardcoded local path)
pytest.ini                Currently empty — no markers or testpaths registered yet
requirements.txt          Currently empty — add `pytest` (and anything else the suite needs) here
what-to-test              Working notes: the original breakdown of what to test, by area, and why in that order
```

## What is tested so far

| Area | Requirement IDs | Status |
|---|---|---|
| Authentication | AUTH-001 – AUTH-005 | Implemented and passing (both `pytest/` and `Unit_test/`) |
| Access control | AC-001 – AC-005 | Implemented and passing (both `pytest/` and `Unit_test/`) |
| Logging | LOG-001 onward | Requirement doc exists; no implementation or tests yet |
| Encryption | ENC-001 onward | Requirement doc exists; no implementation or tests yet |
| Session security | SESS-001 onward | No requirement doc, implementation, or tests yet |

### Authentication (AUTH-001 – AUTH-005)

| ID | Expected behaviour |
|---|---|
| AUTH-001 | A registered user with the correct password logs in successfully |
| AUTH-002 | An unregistered username is rejected |
| AUTH-003 | A registered username with the wrong password is rejected |
| AUTH-004 | Empty or missing (`None`) credentials are rejected without crashing |
| AUTH-005 | Injection-style input in either field is safely rejected, with no internal error leaked |

### Access control (AC-001 – AC-005)

| ID | Expected behaviour |
|---|---|
| AC-001 | Architect can view and edit |
| AC-002 | Engineer can view and edit |
| AC-003 | Contractor can view, but is denied edit (not just hidden from it) |
| AC-004 | Client can view, but is denied edit (not just hidden from it) |
| AC-005 | An unregistered/unknown user is denied both view and edit; malformed input (`None`, wrong type) is rejected without crashing |

## Traceability

Requirements are documented under `Requirements/` with unique IDs. Every test in `tests/pytest/` links back to the requirement it verifies, e.g.:

```python
@pytest.mark.access_control
@pytest.mark.negative
@pytest.mark.requirement("AC-003")
def test_contractor_cannot_edit():
    """AC-003: Contractor is denied edit, not just hidden from it."""
    result = check_access("contractor", "edit")

    assert result is False
```

`tests/Unit_test/` currently mirrors the same cases without the requirement tags or docstrings — it exists as a plainer, isolated check of each function rather than a distinct layer of coverage. If the two suites are meant to serve different purposes going forward (e.g. `Unit_test/` covering finer-grained edge cases beyond what's in the requirements docs), that split still needs to be built out.

## Development and QA workflow

```
Requirement → Test case → Development implementation → QA automated test → Execution → PASS/FAIL → Defect investigation → Fix → Retest
```

A feature is considered complete when: the requirement is documented, the Development implementation exists, QA tests have been written, the tests pass, and any defects found have been fixed and retested.

## Out of scope

Penetration testing, load and performance testing, production deployment, physical site security, and implementing or fixing the Development system itself (QA only verifies it).