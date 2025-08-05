import hashlib
import secrets
import base64
from typing import Tuple

def generate_password_hash(email: str, password: str) -> Tuple[str, str]:
    """
    Generates a password hash and salt.
    
    Args:
        email: The email address
        password: The password
        
    Returns:
        A tuple containing the salt and the hashed password
    """
    # Generate a random salt (16 bytes, base64 encoded)
    salt = base64.b64encode(secrets.token_bytes(16)).decode('utf-8')
    
    # Create the hash using PBKDF2 with SHA512
    password_hash = hashlib.pbkdf2_hmac(
        'sha512',
        password.encode('utf-8'),
        (salt + email + ":").encode('utf-8'),
        1000,
        64
    )
    
    # Convert to base64 string
    password_hash_b64 = base64.b64encode(password_hash).decode('utf-8')
    
    return salt, password_hash_b64

def verify_password(password: str, email: str, salt: str, stored_hash: str) -> bool:
    """
    Verify a password against a stored hash.
    
    Args:
        password: The password to verify
        email: The email
        salt: The stored salt
        stored_hash: The stored password hash
        
    Returns:
        True if password is correct, False otherwise
    """
    # Generate hash with the same parameters
    password_hash = hashlib.pbkdf2_hmac(
        'sha512',
        password.encode('utf-8'),
        (salt + email + ":").encode('utf-8'),
        1000,
        64
    )
    
    # Convert to base64 string
    password_hash_b64 = base64.b64encode(password_hash).decode('utf-8')
    
    # Compare with stored hash
    return password_hash_b64 == stored_hash
