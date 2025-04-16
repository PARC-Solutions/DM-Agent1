"""
Encryption Manager for HIPAA Compliance

This module implements encryption functionality for protecting sensitive data
in the Medical Billing Denial Agent system, ensuring HIPAA compliance for
PHI data at rest and in transit.

Features:
- Data encryption at rest
- Secure key management
- Encrypted data formats
"""

import base64
import json
import logging
import os
import secrets
import time
from typing import Any, Dict, Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)

class EncryptionManager:
    """
    Manages encryption and decryption of sensitive data.
    
    This class provides methods for encrypting and decrypting data,
    key management, and secure data handling to ensure HIPAA compliance.
    """
    
    def __init__(self, 
                key_env_var: str = "ENCRYPTION_KEY",
                use_env_key: bool = True,
                auto_generate_key: bool = True):
        """
        Initialize the encryption manager.
        
        Args:
            key_env_var: Environment variable name for encryption key
            use_env_key: Whether to use the key from environment variables
            auto_generate_key: Whether to auto-generate a key if not found
        """
        self.key_env_var = key_env_var
        self.key = None
        self.cipher_suite = None
        
        # Try to get key from environment
        if use_env_key:
            env_key = os.getenv(key_env_var)
            if env_key:
                try:
                    # Check if key is valid
                    self.key = env_key.encode() if isinstance(env_key, str) else env_key
                    self.cipher_suite = Fernet(self.key)
                    logger.info("Encryption key loaded from environment")
                except Exception as e:
                    logger.warning(f"Invalid encryption key in environment: {e}")
                    self.key = None
        
        # Generate new key if needed and allowed
        if self.key is None and auto_generate_key:
            self.key = Fernet.generate_key()
            self.cipher_suite = Fernet(self.key)
            logger.warning("Generated new encryption key - this should be stored securely")
        
        if self.key is None:
            raise ValueError("No encryption key available and auto-generation disabled")
    
    def generate_key(self, password: str, salt: Optional[bytes] = None) -> bytes:
        """
        Generate a key from a password and optional salt.
        
        Args:
            password: Password to derive key from
            salt: Optional salt for key derivation
            
        Returns:
            Generated key
        """
        if salt is None:
            salt = secrets.token_bytes(16)
            
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt(self, data: Any) -> Dict[str, str]:
        """
        Encrypt data.
        
        Args:
            data: Data to encrypt
            
        Returns:
            Dictionary with encrypted data and metadata
        """
        if self.cipher_suite is None:
            raise ValueError("Encryption key not set")
            
        # Convert data to JSON string if it's not already a string
        if not isinstance(data, str):
            data_str = json.dumps(data)
        else:
            data_str = data
            
        # Encrypt the data
        encrypted_data = self.cipher_suite.encrypt(data_str.encode())
        
        # Return encrypted data with metadata
        return {
            "encrypted_data": base64.b64encode(encrypted_data).decode(),
            "encryption_timestamp": time.time(),
            "encryption_version": "v1"
        }
    
    def decrypt(self, encrypted_package: Dict[str, str]) -> Any:
        """
        Decrypt data.
        
        Args:
            encrypted_package: Dictionary with encrypted data and metadata
            
        Returns:
            Decrypted data
        """
        if self.cipher_suite is None:
            raise ValueError("Encryption key not set")
            
        # Extract encrypted data
        encrypted_data = base64.b64decode(encrypted_package["encrypted_data"])
        
        # Decrypt the data
        decrypted_data = self.cipher_suite.decrypt(encrypted_data).decode()
        
        # Try to parse as JSON
        try:
            return json.loads(decrypted_data)
        except json.JSONDecodeError:
            # Return as string if not valid JSON
            return decrypted_data
    
    def encrypt_field(self, field_value: Any) -> str:
        """
        Encrypt a single field value.
        
        Args:
            field_value: Value to encrypt
            
        Returns:
            Encrypted field value as a string
        """
        encrypted_package = self.encrypt(field_value)
        return json.dumps(encrypted_package)
    
    def decrypt_field(self, encrypted_field: str) -> Any:
        """
        Decrypt a single field value.
        
        Args:
            encrypted_field: Encrypted field value as a string
            
        Returns:
            Decrypted field value
        """
        try:
            encrypted_package = json.loads(encrypted_field)
            return self.decrypt(encrypted_package)
        except json.JSONDecodeError:
            raise ValueError("Invalid encrypted field format")
    
    def encrypt_document(self, document: Dict[str, Any], 
                        sensitive_fields: Optional[list] = None) -> Dict[str, Any]:
        """
        Selectively encrypt sensitive fields in a document.
        
        Args:
            document: Document to encrypt
            sensitive_fields: List of field names to encrypt
            
        Returns:
            Document with encrypted fields
        """
        if sensitive_fields is None:
            # Default sensitive fields
            sensitive_fields = [
                "patient_name", "patient_id", "dob", "ssn", "address",
                "phone", "email", "member_id", "account_number", "mrn",
                "diagnosis", "icd_codes", "procedure_details", "notes"
            ]
            
        encrypted_doc = document.copy()
        
        for field in sensitive_fields:
            if field in encrypted_doc and encrypted_doc[field]:
                # Mark the field as encrypted
                encrypted_value = self.encrypt_field(encrypted_doc[field])
                encrypted_doc[field] = {
                    "encrypted": True,
                    "value": encrypted_value
                }
                
        return encrypted_doc
    
    def decrypt_document(self, encrypted_doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt sensitive fields in an encrypted document.
        
        Args:
            encrypted_doc: Document with encrypted fields
            
        Returns:
            Document with decrypted fields
        """
        decrypted_doc = encrypted_doc.copy()
        
        for field, value in decrypted_doc.items():
            if isinstance(value, dict) and value.get("encrypted") == True:
                decrypted_doc[field] = self.decrypt_field(value["value"])
                
        return decrypted_doc
    
    def rotate_key(self, new_key: Optional[bytes] = None) -> bytes:
        """
        Rotate encryption key.
        
        Args:
            new_key: Optional new key to use
            
        Returns:
            New encryption key
        """
        old_key = self.key
        
        # Generate new key if not provided
        if new_key is None:
            new_key = Fernet.generate_key()
            
        # Update current key
        self.key = new_key
        self.cipher_suite = Fernet(self.key)
        
        logger.info("Encryption key rotated")
        return new_key
    
    def get_key(self) -> bytes:
        """
        Get the current encryption key.
        
        This should only be used for legitimate key backup purposes,
        not for normal operations.
        
        Returns:
            Current encryption key
        """
        logger.warning("Encryption key accessed - this should be rare")
        return self.key

# Create a singleton instance
default_encryption_manager = EncryptionManager()
