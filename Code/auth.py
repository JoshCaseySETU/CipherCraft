from flask import render_template, redirect, url_for, session
from database import databaseConnect
import re
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC, hashes
import base64
import os
import secrets

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
    padded_data = padder.update(data) + padder.finalize()
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

def assign_unauthenticated_token():
    if 'unauthenticated_token' not in session:
        session['unauthenticated_token'] = generate_unauthenticated_token()

def remove_unauthenticated_token():
    session.pop('unauthenticated_token', None)

def assign_authenticated_token():
    session['authenticated'] = True

def generate_unauthenticated_token():
    return secrets.token_hex(16)

def passwordPolicy(password):
    if len(password) < 12:
        return "Password must be at least 12 characters long."

    if not any(char.isupper() for char in password) or not any(char.islower() for char in password):
        return "Password must contain a mixture of upper and lower case characters."

    if not any(char.isdigit() for char in password):
        return "Password must contain at least one digit."

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain at least one symbol (!@#$%^&*(),.?\":{}|<>)."

    return None

# Setting users session - Session Management 
def sessionMan(username):
    session['username']=username
    
# Checks if username already exist
def usernameExists(username):
    query = "SELECT * FROM userInfo WHERE username = %s"
    data = (username,)
    result = databaseConnect(query, data, fetchone=True)
    return result is not None

# Sign up function - Checks information & queries to database
def signUp(username, email, confirmEmail, password, confirmPassword, bcrypt):
    
    # Calls function checking username 
    if usernameExists(username):
        error_message = "Username is taken. Please enter a different username."
        return render_template("auth.html", error=error_message)
    
    # Making sure users entered the correct password and email
    if password == confirmPassword and email == confirmEmail:
        
        # Validate password against policy
        password_policy_error = passwordPolicy(password)
        if password_policy_error:
            return render_template("signUp.html", error=password_policy_error)
        
        # Hashes the password 
        hashPassword = bcrypt.generate_password_hash(password)
        
        user_key = generate_key()
        iv = os.urandom(16)
        master_key = get_master_key()
        user_key_cipher = initialize_cipher(master_key, user_key, iv)
        encrypted_user_key = encrypt_data(user_key_cipher, user_key)
        email_cipher = initialize_cipher(master_key, user_key, iv)
        encrypt_email = encrypt_data(email_cipher, email.encode('utf-8'))
        
        # Queries to database using parametization 
        query = "INSERT INTO userInfo (username, email, password, userKey, iv) VALUES (%s, %s, %s, %s, %s)"
        data = (username, encrypt_email, hashPassword, encrypted_user_key, iv)
        databaseConnect(query, data)
        return redirect(url_for('login'))
    else:
        error_message = "Passwords or emails don't match"
        return render_template("auth.html", error=error_message)

# Login function - Checks information in database to ensure user exist
def Login(username, password, bcrypt):
    
    # Queries database checking username is there 
    query = "SELECT * FROM userInfo WHERE username = %s"
    data = (username,)
    result = databaseConnect(query, data, fetchone=True)

    # hashes user password and checks it is same in the database 
    if result and bcrypt.check_password_hash(result[3], password):
        remove_unauthenticated_token()
        assign_authenticated_token()
        sessionMan(username)
        return redirect('/')
    else:
        error_message = "Invalid credentials. Please try again."
        return render_template("auth.html", error=error_message) 