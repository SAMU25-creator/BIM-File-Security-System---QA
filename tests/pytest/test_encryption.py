"""
test_encryption.py

Acceptance tests for Encryption (ENC-001 to ENC-004).

ASSUMED INTERFACE for the Development repo's encryption.py
(adjust the names below if Dev uses different ones):

    generate_key()              -> new key (str)
    encrypt_data(data: bytes)   -> ciphertext (bytes)
    decrypt_data(token: bytes)  -> original bytes
    store_file(name, data)      -> path of the encrypted file on disk
    read_file(name)             -> original bytes
    EncryptionError             -> raised for every failure

    Key is read from the BIM_ENCRYPTION_KEY environment variable and files
    are stored in the folder named by BIM_STORAGE_DIR.

Every test runs against a throw-away key and a throw-away storage folder
(pytest's tmp_path), so nothing touches real project data.
"""

import os

import pytest

encryption = pytest.importorskip(
    "encryption", reason="encryption.py not yet implemented in the Development repo"
)

generate_key = encryption.generate_key
encrypt_data = encryption.encrypt_data
decrypt_data = encryption.decrypt_data
store_file = encryption.store_file
read_file = encryption.read_file
EncryptionError = encryption.EncryptionError

KEY_ENV_VAR = getattr(encryption, "KEY_ENV_VAR", "BIM_ENCRYPTION_KEY")
STORAGE_ENV_VAR = getattr(encryption, "STORAGE_ENV_VAR", "BIM_STORAGE_DIR")

SECRET = b"Level 2 floor plan - CONFIDENTIAL"

BAD_FILENAMES = [
    "",
    "   ",
    None,
    123,
    "../escape.bim",
    "..\\escape.bim",
    "sub/dir.bim",
    "/abs.bim",
    ".",
    "..",
]

BAD_DATA = [None, "plain text, not bytes", 123, []]


@pytest.fixture(autouse=True)
def encryption_env(monkeypatch, tmp_path):
    """Fresh key and fresh storage folder for every test."""
    storage = tmp_path / "storage"
    monkeypatch.setenv(KEY_ENV_VAR, generate_key())
    monkeypatch.setenv(STORAGE_ENV_VAR, str(storage))
    return storage


def _raw(path):
    with open(path, "rb") as f:
        return f.read()


def _files_in(folder):
    return [
        os.path.join(root, name)
        for root, _dirs, names in os.walk(folder)
        for name in names
    ]


# --- ENC-001: files are stored encrypted ---

@pytest.mark.encryption
@pytest.mark.requirement("ENC-001")
def test_stored_file_is_not_plaintext():
    """ENC-001: The file on disk must not contain the original content."""
    path = store_file("plan.bim", SECRET)

    assert SECRET not in _raw(path)
    assert b"CONFIDENTIAL" not in _raw(path)


@pytest.mark.encryption
@pytest.mark.requirement("ENC-001")
def test_stored_file_differs_from_original():
    """ENC-001: What is written to storage is not the original bytes."""
    path = store_file("plan.bim", SECRET)

    assert _raw(path) != SECRET


@pytest.mark.encryption
@pytest.mark.requirement("ENC-001")
def test_no_plaintext_left_anywhere_in_storage(encryption_env):
    """ENC-001: No file in storage (including temp files) holds plaintext."""
    store_file("plan.bim", SECRET)

    for path in _files_in(encryption_env):
        assert SECRET not in _raw(path)


@pytest.mark.encryption
@pytest.mark.requirement("ENC-001")
def test_same_data_encrypts_differently_each_time():
    """ENC-001: Identical files must not produce identical ciphertext."""
    assert encrypt_data(SECRET) != encrypt_data(SECRET)

    path_a = store_file("a.bim", SECRET)
    path_b = store_file("b.bim", SECRET)
    assert _raw(path_a) != _raw(path_b)


# --- ENC-002: stored files decrypt back to the original ----------------------

@pytest.mark.encryption
@pytest.mark.requirement("ENC-002")
@pytest.mark.parametrize(
    "data",
    [SECRET, b"", bytes(range(256)), "plán – ünïcode".encode("utf-8")],
    ids=["text", "empty", "all-byte-values", "unicode"],
)
def test_stored_file_round_trips(data):
    """ENC-002: A stored file reads back as exactly the original bytes."""
    store_file("plan.bim", data)

    assert read_file("plan.bim") == data


@pytest.mark.encryption
@pytest.mark.requirement("ENC-002")
def test_large_file_round_trips():
    """ENC-002: A large (1 MB) file survives the round trip."""
    data = os.urandom(1_000_000)
    store_file("big.bim", data)

    assert read_file("big.bim") == data


@pytest.mark.encryption
@pytest.mark.requirement("ENC-002")
def test_encrypt_then_decrypt_data_round_trips():
    """ENC-002: decrypt_data reverses encrypt_data."""
    assert decrypt_data(encrypt_data(SECRET)) == SECRET


@pytest.mark.encryption
@pytest.mark.requirement("ENC-002")
def test_overwriting_a_file_returns_latest_version():
    """ENC-002: Storing under an existing name replaces the old content."""
    store_file("plan.bim", b"version 1")
    store_file("plan.bim", b"version 2")

    assert read_file("plan.bim") == b"version 2"


# --- ENC-003: wrong key / tampered data is rejected --------------------------

@pytest.mark.encryption
@pytest.mark.negative
@pytest.mark.requirement("ENC-003")
def test_wrong_key_cannot_read_file(monkeypatch):
    """ENC-003: A file encrypted with one key cannot be read with another."""
    store_file("plan.bim", SECRET)
    monkeypatch.setenv(KEY_ENV_VAR, generate_key())

    with pytest.raises(EncryptionError):
        read_file("plan.bim")


@pytest.mark.encryption
@pytest.mark.negative
@pytest.mark.requirement("ENC-003")
def test_wrong_key_cannot_decrypt_data(monkeypatch):
    """ENC-003: Ciphertext cannot be decrypted with a different key."""
    token = encrypt_data(SECRET)
    monkeypatch.setenv(KEY_ENV_VAR, generate_key())

    with pytest.raises(EncryptionError):
        decrypt_data(token)


@pytest.mark.encryption
@pytest.mark.negative
@pytest.mark.requirement("ENC-003")
def test_tampered_file_rejected():
    """ENC-003: Changing a single byte of the stored file is detected."""
    path = store_file("plan.bim", SECRET)
    tampered = bytearray(_raw(path))
    tampered[len(tampered) // 2] ^= 1
    with open(path, "wb") as f:
        f.write(bytes(tampered))

    with pytest.raises(EncryptionError):
        read_file("plan.bim")


@pytest.mark.encryption
@pytest.mark.negative
@pytest.mark.requirement("ENC-003")
def test_truncated_file_rejected():
    """ENC-003: A stored file cut short is rejected, not partially returned."""
    path = store_file("plan.bim", SECRET)
    raw = _raw(path)
    with open(path, "wb") as f:
        f.write(raw[: len(raw) // 2])

    with pytest.raises(EncryptionError):
        read_file("plan.bim")


@pytest.mark.encryption
@pytest.mark.negative
@pytest.mark.requirement("ENC-003")
@pytest.mark.parametrize(
    "garbage",
    [b"", b"garbage", b"\x00" * 64],
    ids=["empty", "text", "zeros"],
)
def test_garbage_ciphertext_rejected(garbage):
    """ENC-003: Data that was never encrypted by the system is rejected."""
    with pytest.raises(EncryptionError):
        decrypt_data(garbage)


@pytest.mark.encryption
@pytest.mark.negative
@pytest.mark.requirement("ENC-003")
def test_failed_decrypt_does_not_leak_secrets(monkeypatch):
    """ENC-003: The error for a failed decrypt shows neither key nor content."""
    store_file("plan.bim", SECRET)
    right_key = os.environ[KEY_ENV_VAR]
    wrong_key = generate_key()
    monkeypatch.setenv(KEY_ENV_VAR, wrong_key)

    with pytest.raises(EncryptionError) as excinfo:
        read_file("plan.bim")

    message = str(excinfo.value)
    assert right_key not in message
    assert wrong_key not in message
    assert SECRET.decode() not in message


# --- ENC-004: bad input is rejected safely -----------------------------------

@pytest.mark.encryption
@pytest.mark.negative
@pytest.mark.requirement("ENC-004")
@pytest.mark.parametrize("bad_name", BAD_FILENAMES)
def test_store_rejects_unsafe_filename(bad_name, tmp_path):
    """ENC-004: Empty, non-string, or path-escaping filenames are rejected."""
    with pytest.raises(EncryptionError):
        store_file(bad_name, SECRET)

    assert not (tmp_path / "escape.bim").exists()


@pytest.mark.encryption
@pytest.mark.negative
@pytest.mark.requirement("ENC-004")
@pytest.mark.parametrize("bad_name", BAD_FILENAMES)
def test_read_rejects_unsafe_filename(bad_name):
    """ENC-004: Reading with an unsafe filename is rejected."""
    with pytest.raises(EncryptionError):
        read_file(bad_name)


@pytest.mark.encryption
@pytest.mark.negative
@pytest.mark.requirement("ENC-004")
@pytest.mark.parametrize("bad_data", BAD_DATA)
def test_store_rejects_non_bytes_data(bad_data):
    """ENC-004: Only bytes can be stored; anything else is rejected."""
    with pytest.raises(EncryptionError):
        store_file("plan.bim", bad_data)


@pytest.mark.encryption
@pytest.mark.negative
@pytest.mark.requirement("ENC-004")
@pytest.mark.parametrize("bad_data", BAD_DATA)
def test_encrypt_rejects_non_bytes_data(bad_data):
    """ENC-004: encrypt_data only accepts bytes."""
    with pytest.raises(EncryptionError):
        encrypt_data(bad_data)


@pytest.mark.encryption
@pytest.mark.negative
@pytest.mark.requirement("ENC-004")
@pytest.mark.parametrize("bad_token", BAD_DATA)
def test_decrypt_rejects_non_bytes_data(bad_token):
    """ENC-004: decrypt_data only accepts bytes."""
    with pytest.raises(EncryptionError):
        decrypt_data(bad_token)


@pytest.mark.encryption
@pytest.mark.negative
@pytest.mark.requirement("ENC-004")
def test_failed_store_writes_nothing(encryption_env):
    """ENC-004: A rejected store leaves no file behind in storage."""
    with pytest.raises(EncryptionError):
        store_file("plan.bim", None)

    assert not encryption_env.exists() or _files_in(encryption_env) == []


@pytest.mark.encryption
@pytest.mark.negative
@pytest.mark.requirement("ENC-004")
def test_reading_missing_file_rejected():
    """ENC-004: Reading a file that was never stored fails safely."""
    with pytest.raises(EncryptionError):
        read_file("never-stored.bim")


@pytest.mark.encryption
@pytest.mark.negative
@pytest.mark.requirement("ENC-004")
def test_missing_key_rejected(monkeypatch):
    """ENC-004: With no key configured, nothing is encrypted or stored."""
    monkeypatch.delenv(KEY_ENV_VAR, raising=False)

    with pytest.raises(EncryptionError):
        encrypt_data(SECRET)
    with pytest.raises(EncryptionError):
        store_file("plan.bim", SECRET)


@pytest.mark.encryption
@pytest.mark.negative
@pytest.mark.requirement("ENC-004")
def test_invalid_key_rejected_without_leaking_it(monkeypatch):
    """ENC-004: A malformed key is rejected and never shown in the error."""
    bad_key = "not-a-valid-key"
    monkeypatch.setenv(KEY_ENV_VAR, bad_key)

    with pytest.raises(EncryptionError) as excinfo:
        encrypt_data(SECRET)

    assert bad_key not in str(excinfo.value)