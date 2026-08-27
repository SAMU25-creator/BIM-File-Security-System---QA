# BIM File Security System — QA

Automated test suite that independently validates the BIM File Security System's authentication, access control, logging, and encryption.

This repo contains requirements and tests only. The system under test is a separate application owned by the Development team; these tests talk to it over HTTP.

> System under test: `bim-file-security-system`

## Getting started

Requires Python 3.11+, Git, and an SSH key registered with GitHub.

```bash
git clone git@github.com:<org>/bim-file-security-qa.git
cd bim-file-security-qa
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # set BASE_URL and test credentials for each role
```

## Running tests

Start the BIM File Security System first, then:

```bash
pytest                                  # full suite
pytest -m access                        # one area
pytest tests/test_authentication.py     # one file
pytest -k "unauthorised_access"         # one test
```

Markers: `auth`, `access`, `logging`, `encryption`, `session`, `negative`, `regression`.

## Structure

```
requirements/    Documented requirements, one file per area
tests/           pytest suite
test_data/       Seed users (one per role), sample BIM files, payloads
reports/         Test results
evidence/        Failure evidence
```

## What is tested

| Area | Expected behaviour |
|---|---|
| Authentication | Only registered users can log in |
| Access control | Architects and Engineers can view/edit; Contractors and Clients can view only |
| Unauthorised access | Users without an account, or with an invalid/unknown role, are denied access |
| Event logging | Every access attempt (allowed or denied) is recorded with user, action, file, and timestamp |
| Encryption | Files are encrypted at rest; data is protected in transit |
| Session security | Sessions expire, invalidate on logout, and cannot be reused |
| Failed logins | Repeated failed attempts are throttled or locked out |

## Traceability

Requirements use IDs (`AUTH-001`, `AC-001`, `AC-002`, `LOG-001`, `ENC-001`, `SESS-001`) defined under `requirements/`. Every test links to the requirement it covers:

```python
@pytest.mark.access
@pytest.mark.requirement("AC-002")
def test_contractor_cannot_edit_file(api, access_log):
    """AC-002: Contractors have view-only access and must not be able to edit files."""
    response = api.edit_file(role="contractor", file_id="bim_001")
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert access_log.latest(action="edit_attempt")["result"] == "denied"
```

Example manual test case:

> **Test:** Try accessing the construction-site dashboard using an unauthorised account.
> **Expected:** Access denied and event logged.
> **Actual:** Access denied and event logged.
> **Result:** PASS ✅

## Workflow

Requirement → test case → automated test → execution. On failure, QA raises a defect against the BIM File Security System repo with reproduction steps, expected vs actual result, and evidence, then retests after the fix.

A feature is done when the requirement is documented, tests are automated and passing, defects are closed and retested, and evidence is collected.

## Out of scope

Penetration testing, load testing, production environments, physical site security, and implementing or fixing the BIM File Security System itself.

Details: `docs/qa-strategy.md`



bim-file-security-qa/
│
├── requirements/
│   ├── authentication.md
│   ├── access-control.md
│   ├── logging.md
│   └── encryption.md
│
├── tests/
│   ├── test_authentication.py
│   ├── test_access_control.py
│   ├── test_logging.py
│   ├── test_encryption.py
│   └── test_session.py
│
├── test_data/
├── reports/
├── evidence/
│
├── .env
├── .env.example
├── requirements.txt
├── pytest.ini
└── README.md