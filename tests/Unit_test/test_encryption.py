"""
Unit tests for encryption.py.

Assumed interface (same as tests/pytest/test_encryption.py):

    generate_key()              -> new key (str)
    encrypt_data(data: bytes)   -> ciphertext (bytes)
    decrypt_data(token: bytes)  -> original bytes
    store_file(name, data)      -> path of the encrypted file on disk
    read_file(name)             -> original bytes
    EncryptionError             -> raised for every failure

Key comes from BIM_ENCRYPTION_KEY, storage folder from BIM_STORAGE_DIR.
"""

import os
from pathlib import Path

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


@pytest.fixture(autouse=True)
def encryption_env(monkeypatch, tmp_path):
    """Fresh key and a storage folder that does not exist yet."""
    storage = tmp_path / "storage"
    monkeypatch.setenv(KEY_ENV_VAR, generate_key())
    monkeypatch.setenv(STORAGE_ENV_VAR, str(storage))
    return storage


# --- Keys ---

def test_generate_key_returns_non_empty_string():
    key = generate_key()

    assert isinstance(key, str)
    assert key != ""


def test_generate_key_returns_different_keys():
    assert generate_key() != generate_key()


# --- encrypt_data / decrypt_data ---

def test_encrypt_data_returns_bytes():
    result = encrypt_data(b"hello")

    assert isinstance(result, bytes)


def test_encrypt_data_output_differs_from_input():
    result = encrypt_data(b"hello")

    assert result != b"hello"
    assert b"hello" not in result


def test_decrypt_data_reverses_encrypt_data():
    result = decrypt_data(encrypt_data(b"hello"))

    assert result == b"hello"


def test_empty_bytes_round_trip():
    result = decrypt_data(encrypt_data(b""))

    assert result == b""


def test_decrypt_with_changed_key_rejected(monkeypatch):
    token = encrypt_data(b"hello")
    monkeypatch.setenv(KEY_ENV_VAR, generate_key())

    with pytest.raises(EncryptionError):
        decrypt_data(token)


def test_key_is_read_at_call_time(monkeypatch):
    first_key = os.environ[KEY_ENV_VAR]
    token = encrypt_data(b"hello")

    monkeypatch.setenv(KEY_ENV_VAR, generate_key())
    with pytest.raises(EncryptionError):
        decrypt_data(token)

    monkeypatch.setenv(KEY_ENV_VAR, first_key)
    assert decrypt_data(token) == b"hello"


# --- store_file / read_file ---

def test_store_file_returns_path_that_exists():
    path = store_file("plan.bim", b"hello")

    assert os.path.isfile(path)


def test_store_file_creates_missing_storage_folder(encryption_env):
    assert not encryption_env.exists()

    store_file("plan.bim", b"hello")

    assert encryption_env.is_dir()


def test_store_file_saves_inside_storage_folder(encryption_env):
    path = store_file("plan.bim", b"hello")

    assert Path(path).resolve().parent == encryption_env.resolve()


def test_store_file_uses_the_given_filename():
    path = store_file("plan.bim", b"hello")

    assert Path(path).name == "plan.bim"


def test_stored_file_is_not_plaintext():
    path = store_file("plan.bim", b"CONFIDENTIAL floor plan")

    assert b"CONFIDENTIAL" not in Path(path).read_bytes()


def test_store_file_leaves_no_temp_files(encryption_env):
    store_file("plan.bim", b"hello")

    assert os.listdir(encryption_env) == ["plan.bim"]


def test_two_files_stay_independent():
    store_file("a.bim", b"file a")
    store_file("b.bim", b"file b")

    assert read_file("a.bim") == b"file a"
    assert read_file("b.bim") == b"file b"


def test_overwrite_replaces_old_content():
    store_file("plan.bim", b"version 1")
    store_file("plan.bim", b"version 2")

    assert read_file("plan.bim") == b"version 2"


def test_filename_with_dots_and_spaces_is_allowed():
    store_file("plan v2.final.bim", b"hello")

    assert read_file("plan v2.final.bim") == b"hello"


def test_storage_folder_is_read_at_call_time(monkeypatch, tmp_path):
    other = tmp_path / "other_storage"
    monkeypatch.setenv(STORAGE_ENV_VAR, str(other))

    store_file("plan.bim", b"hello")

    assert (other / "plan.bim").is_file()


def test_unencrypted_file_in_storage_is_rejected(encryption_env):
    encryption_env.mkdir()
    (encryption_env / "plain.bim").write_bytes(b"not encrypted at all")

    with pytest.raises(EncryptionError):
        read_file("plain.bim")


# --- Errors ---

def test_encryption_error_is_an_exception():
    assert issubclass(EncryptionError, Exception)


def test_none_data_rejected():
    with pytest.raises(EncryptionError):
        encrypt_data(None)


def test_text_data_rejected():
    with pytest.raises(EncryptionError):
        encrypt_data("not bytes")


def test_none_filename_rejected():
    with pytest.raises(EncryptionError):
        store_file(None, b"hello")


def test_empty_filename_rejected():
    with pytest.raises(EncryptionError):
        store_file("", b"hello")


def test_parent_folder_filename_rejected(tmp_path):
    with pytest.raises(EncryptionError):
        store_file("../escape.bim", b"hello")

    assert not (tmp_path / "escape.bim").exists()


def test_subfolder_filename_rejected():
    with pytest.raises(EncryptionError):
        store_file("sub/plan.bim", b"hello")


def test_missing_file_rejected():
    with pytest.raises(EncryptionError):
        read_file("never-stored.bim")


def test_missing_key_rejected(monkeypatch):
    monkeypatch.delenv(KEY_ENV_VAR, raising=False)

    with pytest.raises(EncryptionError):
        encrypt_data(b"hello")


def test_invalid_key_rejected(monkeypatch):
    monkeypatch.setenv(KEY_ENV_VAR, "not-a-valid-key")

    with pytest.raises(EncryptionError):
        encrypt_data(b"hello")