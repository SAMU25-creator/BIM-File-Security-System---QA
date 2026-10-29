# BIM File Security System — QA

Automated test suite that independently verifies the BIM File Security System's authentication, access control, audit logging, encryption, and session security.

This repo contains requirements and tests only. The system under test (`authentication.py`, `access_control.py`, `audit_log.py`, `encryption.py`, `session_security.py`) lives in the separate Development repository, `BIM-File-Security-System`. The tests import its modules directly and call the functions themselves. There is no running server or HTTP layer involved.

> System under test: `BIM-File-Security-System`

## Getting started

Requires Python 3.11+ and Git.

```bash
git clone <qa-repo-url>
cd BIM-File-Security-System---QA
python -m venv .venv
```

Activate the environment.

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux/macOS:**

```bash
source .venv/bin/activate
```

Install the dependencies. `cryptography` is needed because the Development repo's `encryption.py` uses it.

```bash
pip install pytest cryptography
```

### Point the tests at the Development repo

The tests import the Development modules (`from authentication import login`, `from access_control import check_access`, and so on), so the Development repo must be on the Python path. Set `PYTHONPATH` to wherever you cloned it.

**Windows PowerShell:**

```powershell
$env:PYTHONPATH = "C:\path\to\BIM-File-Security-System"
```

**Linux/macOS:**

```bash
export PYTHONPATH="/path/to/BIM-File-Security-System"
```

> `conftest.py` currently also adds a hardcoded path from one contributor's machine. It is harmless on other machines (the path simply does not exist), but setting `PYTHONPATH` as above is what makes the suite portable.

The encryption tests need no setup. They create a throw-away key and storage folder for every test, so no real project data is touched.

## Running tests

```bash
pytest tests/pytest                           # acceptance suite (requirement-tagged)
pytest tests/Unit_test                        # unit suite
pytest tests/pytest/test_authentication.py    # one file
pytest tests/pytest -v                        # verbose, one line per test
pytest -m negative                            # only tests for rejected or denied behaviour
pytest -m requirement                         # anything tagged with a requirement ID
pytest -k "ENC"                               # tests whose name or ID matches
```

Save evidence and a report for a run:

```bash
pytest tests/pytest -v | Tee-Object evidence/run.txt        # PowerShell
pytest tests/pytest -v | tee evidence/run.txt               # Linux/macOS
pytest tests/pytest --junitxml=reports/results.xml
```

### Markers

All markers are registered in `pytest.ini`:

| Marker | Meaning |
|---|---|
| `auth` | Authentication tests |
| `access_control` | Access control tests |
| `logging` | Audit logging tests |
| `encryption` | Encryption tests |
| `session` | Session security tests |
| `negative` | Tests for invalid or rejected input, or denied actions |
| `requirement("<ID>")` | Links a test to a requirement ID |

## Structure

```text
BIM-File-Security-System---QA/
│
├── Requirements/            Documented requirements, one file per area
│   ├── authentication.md
│   ├── access-control.md
│   ├── logging.md
│   └── encryption.md
│
├── tests/
│   ├── pytest/              Acceptance tests, tagged with requirement IDs
│   │   ├── test_authentication.py
│   │   ├── test_access_control.py
│   │   ├── test_audit_log.py
│   │   ├── test_encryption.py
│   │   └── test_session_security.py
│   └── Unit_test/           Plainer function-level tests for the same five areas
│       ├── test_authentication.py
│       ├── test_access_control.py
│       ├── test_audit_log.py
│       ├── test_encryption.py
│       └── test_session_security.py
│
├── evidence/                Saved test run output
├── reports/                 Saved test reports
├── test_data/               Test data (none needed so far)
├── conftest.py              Adds the Development repo to sys.path
├── pytest.ini               Registered markers
├── requirements.txt         Python dependencies for the suite
└── what-to-test             Working notes: the original breakdown of what to test, and why in that order
```

## What is tested

| Area | Requirement IDs | Acceptance tests | Unit tests |
|---|---|---|---|
| Authentication | AUTH-001 – AUTH-005 | `test_authentication.py` | `test_authentication.py` |
| Access control | AC-001 – AC-005 | `test_access_control.py` | `test_access_control.py` |
| Audit logging | LOG-001 – LOG-004 | `test_audit_log.py` | `test_audit_log.py` |
| Encryption | ENC-001 – ENC-004 | `test_encryption.py` | `test_encryption.py` |
| Session security | SESS-001 – SESS-005 | `test_session_security.py` | `test_session_security.py` |

### Authentication (AUTH)

| ID | Expected behaviour |
|---|---|
| AUTH-001 | A registered user with the correct password is authenticated |
| AUTH-002 | An unregistered username is rejected |
| AUTH-003 | A registered username with the wrong password is rejected |
| AUTH-004 | Empty or missing (`None`) credentials are rejected without crashing |
| AUTH-005 | Injection-style input in either field is safely rejected, with no internal error leaked |

### Access control (AC)

| ID | Expected behaviour |
|---|---|
| AC-001 | Architect can view and edit |
| AC-002 | Engineer can view and edit |
| AC-003 | Contractor can view, but is denied edit (not just hidden from it) |
| AC-004 | Client can view, but is denied edit (not just hidden from it) |
| AC-005 | Unregistered users, missing usernames, missing actions and unrecognised actions are denied, without crashing |

### Audit logging (LOG)

| ID | Expected behaviour |
|---|---|
| LOG-001 | Every login attempt, successful or failed, creates a log entry |
| LOG-002 | Every file access attempt, allowed or denied, creates a log entry |
| LOG-003 | Each entry records who, what action, which file, and when |
| LOG-004 | Denied actions are logged as denied, not silently dropped |

### Encryption (ENC)

| ID | Expected behaviour |
|---|---|
| ENC-001 | Files are stored encrypted. The file on disk does not contain the original content, and the same data encrypts differently each time |
| ENC-002 | A stored file decrypts back to exactly the original content (text, empty and binary data) |
| ENC-003 | A wrong key, a changed byte, a cut-off file or never-encrypted data is rejected, and errors do not reveal the key or content |
| ENC-004 | Bad input (wrong data type, unsafe file names, missing file, missing or invalid key) is rejected safely, and a rejected store writes nothing |

### Session security (SESS)

| ID | Expected behaviour |
|---|---|
| SESS-001 | A created session is valid and has a unique token |
| SESS-002 | Logging out ends the session, the old token stops working, and other sessions are not affected |
| SESS-003 | Sessions expire after 30 minutes of inactivity and stay valid just inside the timeout window |
| SESS-004 | Expired or logged-out tokens are rejected every time they are reused |
| SESS-005 | Missing, unknown or malformed tokens are rejected without crashing |

Inactivity expiry is tested by moving the clock forward (a `fake_clock` fixture patches `time.time`), so the suite never has to wait 30 minutes.

## Traceability

Every test in `tests/pytest/` links back to the requirement it verifies:

```python
@pytest.mark.access_control
@pytest.mark.negative
@pytest.mark.requirement("AC-003")
def test_contractor_cannot_edit():
    """AC-003: Contractor is denied edit, not just hidden from it."""
    result = check_access("contractor", "edit")

    assert result is False
```

| Prefix | Area | Range |
|---|---|---|
| `AUTH-` | Authentication | `AUTH-001` to `AUTH-005` |
| `AC-` | Access control | `AC-001` to `AC-005` |
| `LOG-` | Logging | `LOG-001` to `LOG-004` |
| `ENC-` | Encryption | `ENC-001` to `ENC-004` |
| `SESS-` | Session security | `SESS-001` to `SESS-005` |

The full requirement wording, with IDs, is in the Development repo's README. `Requirements/` holds the original per-area test notes.

`tests/Unit_test/` covers the same five areas as `tests/pytest/` but as plainer function-level checks without requirement tags.

## Development and QA workflow

```text
Requirement → Test case → Development implementation → QA automated test → Execution → PASS/FAIL → Defect investigation → Fix → Retest
```

A feature is considered complete when:

* The requirement is documented.
* The Development implementation is completed.
* QA tests have been written.
* Tests pass.
* Any defects have been fixed and retested.
* Evidence and test reports have been collected in `evidence/` and `reports/`.

The QA repo must not duplicate the Development implementation just to make tests pass. It only checks the Development system's behaviour.

## Known limitations

* `conftest.py` still contains a hardcoded path from one machine. Use `PYTHONPATH` as described above.
* `Unit_test/` largely mirrors the acceptance suite. It could be extended with finer-grained edge cases beyond the requirements.
* The tests check the behaviour of the individual modules. They do not check that login creates a session or that file access requires a valid session, because the Development system does not connect these yet.
* The original notes mention testing HTTPS/TLS. The system is terminal-based with no network layer, so that is not tested.

## Out of scope

Penetration testing, load and performance testing, production deployment, physical site security, and implementing or fixing the Development system itself (QA only verifies it).

WTC-HM2LDD4R