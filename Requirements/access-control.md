2. Access control per role (the core of your project)
Test each role against each action — this is your access matrix from the README, turned into test cases:
Architect → can view ✅, can edit ✅
Engineer → can view ✅, can edit ✅
Contractor → can view ✅, cannot edit ❌ (should be denied, not just hidden in UI)
Client → can view ✅, cannot edit ❌
Unauthorised/no account → cannot view or edit ❌

Test both directions — that permitted actions succeed and that forbidden actions are actually blocked (not just "hidden" from the UI but still reachable via a direct request).