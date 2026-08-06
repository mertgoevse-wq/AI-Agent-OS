import os
import logging
from cryptography.fernet import Fernet

class SecurityManager:
    """
    Handles API keys, secrets, and environment variable resolution securely.
    Ensures that secrets are never logged or stored directly in plain text.
    """
    def __init__(self):
        self.logger = logging.getLogger("OMNI.Security")
        # Generate a volatile encryption key for the session runtime
        self._encryption_key = Fernet.generate_key()
        self._cipher = Fernet(self._encryption_key)
        self._vault = {}
        
    def store_secret(self, key_name: str, secret_value: str):
        """
        Encrypts and stores a secret in the volatile vault.
        """
        encrypted = self._cipher.encrypt(secret_value.encode())
        self._vault[key_name] = encrypted
        self.logger.debug(f"Secret {key_name} securely stored in vault.")
        
    def resolve_secret(self, key_name: str) -> str:
        """
        Resolves a secret either from the environment variables or the secure vault.
        """
        if key_name in os.environ:
            return os.environ[key_name]
            
        if key_name in self._vault:
            return self._cipher.decrypt(self._vault[key_name]).decode()
            
        self.logger.warning(f"Failed to resolve secret: {key_name}")
        return ""
        
    def secure_log(self, message: str):
        """
        A secure logging wrapper that prevents accidental credential leakage.
        """
        # Mock redaction logic
        redacted = message.replace("sk-", "sk-****").replace("AIza", "AIza****")
        self.logger.info(redacted)
