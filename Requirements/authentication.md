1. Authentication first:
- Valid user + correct password → logs in successfully
- Invalid username → rejected
- Valid username + wrong password → rejected
- Empty/missing credentials → rejected, not a crash
- Basic injection attempt in username/password fields → safely rejected, no error leak