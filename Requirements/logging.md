3. Logging (proves your security actually works)
Every login attempt (success + failure) creates a log entry
Every file access attempt (allowed + denied) creates a log entry
Log entries contain: who, what action, which file, when
Denied actions are logged as denied, not silently dropped