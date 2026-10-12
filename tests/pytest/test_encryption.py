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


# Give every test a fresh key and a fresh storage folder.
@pytest.fixture(autouse=True)
def encryption_env(monkeypatch, tmp_path):
    storage = tmp_path / "storage"
    monkeypatch.setenv("BIM_ENCRYPTION_KEY", generate_key())
    monkeypatch.setenv("BIM_STORAGE_DIR", str(storage))
    return storage


# --- ENC-001: files are stored encrypted ---

# The file on disk must not contain the original content.
@pytest.mark.encryption
@pytest.mark.requirement("ENC-001")
def test_stored_file_is_not_plaintext():
    """ENC-001: The file on disk does not contain the original content."""
    path = store_file("plan.bim", SECRET)

    assert b"CONFIDENTIAL" not in Path(path).read_bytes()


# The same data must not produce the same ciphertext twice.
@pytest.mark.encryption
@pytest.mark.requirement("ENC-001")
def test_same_data_encrypts_differently_each_time():
    """ENC-001: Encrypting the same data twice gives different ciphertext."""
    assert encrypt_data(SECRET) != encrypt_data(SECRET)


# --- ENC-002: stored files decrypt back to the original ---

# A stored file must read back as exactly the original bytes.
@pytest.mark.encryption
@pytest.mark.requirement("ENC-002")
@pytest.mark.parametrize("data", [SECRET, b"", bytes(range(256))], ids=["text", "empty", "binary"])
def test_stored_file_round_trips(data):
    """ENC-002: A stored file reads back as exactly the original bytes."""
    store_file("plan.bim", data)

    assert read_file("plan.bim") == data


# decrypt_data must reverse encrypt_data.
@pytest.mark.encryption
@pytest.mark.requirement("ENC-002")
def test_encrypt_then_decrypt_round_trips():
    """ENC-002: decrypt_data reverses encrypt_data."""
    assert decrypt_data(encrypt_data(SECRET)) == SECRET


# Storing under an existing name must replace the old content.
@pytest.mark.encryption
@pytest.mark.requirement("ENC-002")
def test_overwriting_a_file_returns_latest_version():
    """ENC-002: Storing under an existing name replaces the old content."""
    store_file("plan.bim", b"version 1")
    store_file("plan.bim", b"version 2")

    assert read_file("plan.bim") == b"version 2"


# --- ENC-003: wrong key or changed data is rejected ---

# A file encrypted with one key must not be readable with another key.
@pytest.mark.encryption
@pytest.mark.negative
@pytest.mark.requirement("ENC-003")
def test_wrong_key_cannot_read_file(monkeypatch):
    """ENC-003: A file encrypted with one key cannot be read with another."""
    store_file("plan.bim", SECRET)
    monkeypatch.setenv("BIM_ENCRYPTION_KEY", generate_key())

    with pytest.raises(EncryptionError):
        read_file("plan.bim")


# Changing one byte of the stored file must be detected.
@pytest.mark.encryption
@pytest.mark.negative
@pytest.mark.requirement("ENC-003")
def test_changed_file_rejected():
    """ENC-003: Changing a single byte of the stored file is detected."""
    path = Path(store_file("plan.bim", SECRET))
    data = bytearray(path.read_bytes())
    data[len(data) // 2] ^= 1
    path.write_bytes(bytes(data))

    with pytest.raises(EncryptionError):
        read_file("plan.bim")


# A stored file that is cut short must be rejected.
@pytest.mark.encryption
@pytest.mark.negative
@pytest.mark.requirement("ENC-003")
def test_cut_off_file_rejected():
    """ENC-003: A stored file that is cut short is rejected."""
    path = Path(store_file("plan.bim", SECRET))
    data = path.read_bytes()
    path.write_bytes(data[: len(data) // 2])

    with pytest.raises(EncryptionError):
        read_file("plan.bim")


# Data that was never encrypted by the system must be rejected.
@pytest.mark.encryption
@pytest.mark.negative
@pytest.mark.requirement("ENC-003")
@pytest.mark.parametrize("garbage", [b"", b"garbage"], ids=["empty", "text"])
def test_garbage_data_rejected(garbage):
    """ENC-003: Data that was never encrypted is rejected."""
    with pytest.raises(EncryptionError):
        decrypt_data(garbage)


# The error message must not show the key or the file content.
@pytest.mark.encryption
@pytest.mark.negative
@pytest.mark.requirement("ENC-003")
def test_failed_decrypt_does_not_leak_secrets(monkeypatch):
    """ENC-003: The error for a failed decrypt shows neither the key nor the content."""
    store_file("plan.bim", SECRET)
    wrong_key = generate_key()
    monkeypatch.setenv("BIM_ENCRYPTION_KEY", wrong_key)

    with pytest.raises(EncryptionError) as error:
        read_file("plan.bim")

    assert wrong_key not in str(error.value)
    assert SECRET.decode() not in str(error.value)


# --- ENC-004: bad input is rejected safely ---

# File names that are empty, not text, or point outside the storage folder must be rejected.
BAD_FILENAMES = [None, "", "../escape.bim", "sub/plan.bim", ".."]


@pytest.mark.encryption
@pytest.mark.negative
@pytest.mark.requirement("ENC-004")
@pytest.mark.parametrize("bad_name", BAD_FILENAMES)
def test_store_rejects_unsafe_filename(bad_name):
    """ENC-004: store_file rejects empty, non-text, and path-escaping file names."""
    with pytest.raises(EncryptionError):
        store_file(bad_name, SECRET)


@pytest.mark.encryption
@pytest.mark.negative
@pytest.mark.requirement("ENC-004")
@pytest.mark.parametrize("bad_name", BAD_FILENAMES)
def test_read_rejects_unsafe_filename(bad_name):
    """ENC-004: read_file rejects empty, non-text, and path-escaping file names."""
    with pytest.raises(EncryptionError):
        read_file(bad_name)


# Only bytes can be encrypted, decrypted, or stored.
@pytest.mark.encryption
@pytest.mark.negative
@pytest.mark.requirement("ENC-004")
@pytest.mark.parametrize("bad_data", [None, "text, not bytes", 123])
def test_non_bytes_data_rejected(bad_data):
    """ENC-004: encrypt_data, decrypt_data, and store_file only accept bytes."""
    with pytest.raises(EncryptionError):
        encrypt_data(bad_data)
    with pytest.raises(EncryptionError):
        decrypt_data(bad_data)
    with pytest.raises(EncryptionError):
        store_file("plan.bim", bad_data)


# A rejected store must not leave a file behind.
@pytest.mark.encryption
@pytest.mark.negative
@pytest.mark.requirement("ENC-004")
def test_failed_store_writes_nothing(encryption_env):
    """ENC-004: A rejected store leaves no file in storage."""
    with pytest.raises(EncryptionError):
        store_file("plan.bim", None)

    assert list(encryption_env.glob("*")) == []


# Reading a file that was never stored must fail safely.
@pytest.mark.encryption
@pytest.mark.negative
@pytest.mark.requirement("ENC-004")
def test_reading_missing_file_rejected():
    """ENC-004: Reading a file that was never stored is rejected."""
    with pytest.raises(EncryptionError):
        read_file("never-stored.bim")


# With no key set, nothing can be encrypted or stored.
@pytest.mark.encryption
@pytest.mark.negative
@pytest.mark.requirement("ENC-004")
def test_missing_key_rejected(monkeypatch):
    """ENC-004: With no key configured, nothing is encrypted or stored."""
    monkeypatch.delenv("BIM_ENCRYPTION_KEY")

    with pytest.raises(EncryptionError):
        encrypt_data(SECRET)
    with pytest.raises(EncryptionError):
        store_file("plan.bim", SECRET)


# A malformed key must be rejected and never shown in the error.
@pytest.mark.encryption
@pytest.mark.negative
@pytest.mark.requirement("ENC-004")
def test_invalid_key_rejected_without_leaking_it(monkeypatch):
    """ENC-004: A malformed key is rejected and not shown in the error."""
    monkeypatch.setenv("BIM_ENCRYPTION_KEY", "not-a-valid-key")

    with pytest.raises(EncryptionError) as error:
        encrypt_data(SECRET)

    assert "not-a-valid-key" not in str(error.value)