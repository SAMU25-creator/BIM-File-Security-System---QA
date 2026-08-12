Smart Construction Site Cybersecurity — QA


Automated test suite that independently validates the cybersecurity system built for a smart construction site.

This repo contains requirements and tests only. The system under test is a separate Java application owned by the Cybersecurity team; these tests talk to it over HTTP.

## System under test: smart-construction-cybersecurity

## Getting started
- Requires Python 3.11+,Git, and an SSH key registered with GitHub.
- bash
- git clone git@github.com:<org>/smart-construction-qa.git
- cd smart-construction-qa
- python -m venv .venv
- source .venv/bin/activate        # Windows: .venv\Scripts\activate
- pip install -r requirements.txt
- cp .env.example .env             # set BASE_URL and test credentials

## Running tests
Start the cybersecurity system first, then:
bash
pytest                                  # full suite
pytest -m auth                          # one area
pytest tests/test_authentication.py     # one file
pytest -k "invalid_login"               # one test
Markers: auth, access, devices, alerts, logging, negative, regression.

## Structure
text
requirements/    Documented requirements, one file per area
tests/           pytest suite
test_data/       Seed users, devices, payloads
reports/         Test results
evidence/        Failure evidence

## What is tested
# Area	               Expected behaviour
Authentication         Only registered users can authenticate
Access control	       Users can only reach resources they are authorised for
Device monitoring	   Unauthorised devices on the site network are identified
Security alerts	       Suspicious activity generates an alert
Event logging	       Security events are recorded with actor, action, and timestamp
Failed logins	       Repeated failed attempts are throttled or locked out
Data protection	       Sensitive information is protected in transit and at rest
Session security	   Sessions expire, invalidate on logout, and cannot be reused

## Traceability
Requirements use IDs (AUTH-002, AC-001, DEV-001, ALRT-001, LOG-001) defined under requirements/. Every test links to the requirement it covers:
python
@pytest.mark.auth
@pytest.mark.requirement("AUTH-002")
    <!-- def test_invalid_login_is_rejected(api, security_log):
        """AUTH-002: Invalid credentials must be rejected and the attempt logged."""
        response = api.login(username="unknown_user", password="incorrect_password")
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert security_log.latest(event_type="failed_login")["username"] == "unknown_user" -->


## Workflow
Requirement → test case → automated test → execution. On failure, QA raises a defect against the Cybersecurity repo with reproduction steps, expected vs actual result, and evidence, then retests after the fix.

A feature is done when the requirement is documented, tests are automated and passing, defects are closed and retested, and evidence is collected.

## Out of scope
Penetration testing, load testing, production environments, physical site security, and implementing or fixing the cybersecurity system itself.
Details: docs/qa-strategy.md

