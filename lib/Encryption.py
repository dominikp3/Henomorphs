import os
from cryptography.hazmat.primitives import hashes, padding, hmac as crypto_hmac
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class InvalidPasswordError(Exception):
    pass


class Encryption:
    ITERATIONS = 100_000
    KEY_SIZE = 32  # 256-bit AES key
    BLOCK_SIZE = 128  # block size for AES in bits
    HMAC_SIZE = 32   # 256-bit HMAC

    @staticmethod
    def _derive_keys(password: str, salt: bytes) -> tuple[bytes, bytes]:
        """
        Derives two keys from the password and salt:
        - encryption key (AES)
        - HMAC key (for integrity verification)
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=Encryption.KEY_SIZE * 2,  # 64 bytes -> 32 AES + 32 HMAC
            salt=salt,
            iterations=Encryption.ITERATIONS,
            backend=default_backend()
        )
        full_key = kdf.derive(password.encode("utf-8"))
        return full_key[:Encryption.KEY_SIZE], full_key[Encryption.KEY_SIZE:]

    @staticmethod
    def encrypt(data: bytes, password: str) -> bytes:
        """Encrypts byte data with password, adds HMAC for verification."""
        salt = os.urandom(16)
        key_enc, key_mac = Encryption._derive_keys(password, salt)
        iv = os.urandom(16)

        # Padding
        padder = padding.PKCS7(Encryption.BLOCK_SIZE).padder()
        padded_data = padder.update(data) + padder.finalize()

        # Encryption AES-CBC
        cipher = Cipher(algorithms.AES(key_enc), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        # HMAC salt+iv+ciphertext
        h = crypto_hmac.HMAC(key_mac, hashes.SHA256(), backend=default_backend())
        h.update(salt + iv + ciphertext)
        mac = h.finalize()

        return salt + iv + ciphertext + mac

    @staticmethod
    def decrypt(raw: bytes, password: str) -> bytes:
        """Decrypts byte data with a password. Verifies HMAC."""
        salt, iv = raw[:16], raw[16:32]
        ciphertext, mac = raw[32:-Encryption.HMAC_SIZE], raw[-Encryption.HMAC_SIZE:]

        key_enc, key_mac = Encryption._derive_keys(password, salt)

        # HMAC check
        h = crypto_hmac.HMAC(key_mac, hashes.SHA256(), backend=default_backend())
        h.update(salt + iv + ciphertext)
        try:
            h.verify(mac)
        except Exception:
            raise InvalidPasswordError("Incorrect password or corrupted ciphertext (HMAC does not match).")

        # Decrypt
        cipher = Cipher(algorithms.AES(key_enc), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()

        # Remove padding
        unpadder = padding.PKCS7(Encryption.BLOCK_SIZE).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        return data
