"""
test_encryption.py

Acceptance tests for Encryption (ENC-001 to ENC-004).

Interface of the Development repo's encryption.py:

    generate_key()              -> new key (str)
    encrypt_data(data: bytes)   -> ciphertext (bytes)
    decrypt_data(token: bytes)  -> original bytes
    store_file(name, data)      -> path of the encrypted file on disk
    read_file(name)             -> original bytes
    EncryptionError             -> raised for every failure

The key is read from BIM_ENCRYPTION_KEY and files are stored in the folder
named by BIM_STORAGE_DIR. Every test uses a throw-away key and a throw-away
storage folder, so nothing touches real project data.
"""

from pathlib import Path

import pytest

from encryption import (
    EncryptionError,
    decrypt_data,
    encrypt_data,
    generate_key,
    read_file,
    store_file,
)

SECRET = b"Level 2 floor plan - CONFIDENTIAL"


