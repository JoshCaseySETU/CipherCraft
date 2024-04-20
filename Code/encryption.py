from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import os

import base64

def get_master_key():
    # Retrieve the master key from the environment variable
    master_key_str = os.environ.get("masterKey")

    if master_key_str is None:
        raise ValueError("Master key not found in environment variable.")

    # Ensure that the Base64 string has correct padding
    padding_length = len(master_key_str) % 4
    master_key_str += '=' * (4 - padding_length) if padding_length != 0 else ''

    # Decode the Base64-encoded string to get the binary data
    return base64.urlsafe_b64decode(master_key_str)


def generate_key():
    return os.urandom(32)

def initialize_cipher(master_key, user_key, iv):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=os.urandom(16),
        iterations=100000,
        backend=default_backend()
    )
    derived_key = kdf.derive(master_key)
    cipher = Cipher(algorithms.AES(derived_key), modes.CFB(iv), backend=default_backend())
    return cipher

def encrypt_data(cipher, data):
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data.encode()) + padder.finalize()
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return base64.urlsafe_b64encode(ciphertext)

def decrypt_data(cipher, encrypted_data):
    decryptor = cipher.decryptor()
    ciphertext = base64.urlsafe_b64decode(encrypted_data)
    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    original_data = unpadder.update(decrypted_data) + unpadder.finalize()
    return original_data.decode()

def test_encryption_decryption():
    # Get the master key from the environment variable
    master_key = get_master_key()

    # Generate a user key and initialization vector (IV)
    user_key = generate_key()
    iv = os.urandom(16)

    # Initialize cipher
    cipher = initialize_cipher(master_key, user_key, iv)

    # Test data
    original_data = "Hello, world!"

    # Encrypt the data
    encrypted_data = encrypt_data(cipher, original_data)
    print("Encrypted Data:", encrypted_data)

    # Decrypt the data
    decrypted_data = decrypt_data(cipher, encrypted_data)
    print("Decrypted Data:", decrypted_data)

    # Check if the decrypted data matches the original data
    assert decrypted_data == original_data, "Encryption and Decryption failed!"

if __name__ == "__main__":
    test_encryption_decryption()

