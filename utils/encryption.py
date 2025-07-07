# utils/encryption.py

import os
from cryptography.fernet import Fernet
# Removed top-level import: from config.settings import ENCRYPTION_KEY_FILE
import logging

# Get logger - Ensure logger is configured elsewhere (e.g., in utils/logger.py)
# If not configured, basicConfig might be needed here for testing,
# but ideally setup is centralized.
# logging.basicConfig(level=logging.INFO) # Example basic config
logger = logging.getLogger(__name__) # Use module name for logger

def generate_encryption_key():
    """Generate a new encryption key using Fernet."""
    logger.debug("Generating new encryption key.")
    try:
        return Fernet.generate_key()
    except Exception as e:
        logger.error(f"Error generating encryption key: {e}", exc_info=True)
        raise # Re-raise the exception after logging

def load_or_generate_and_save_key():
    """
    Loads the encryption key from the file defined in settings.
    If the file doesn't exist, generates a new key, saves it, and returns it.
    """
    # Import ENCRYPTION_KEY_FILE *inside* the function where it's needed
    from config.settings import ENCRYPTION_KEY_FILE

    key_path = ENCRYPTION_KEY_FILE # Use the imported path

    try:
        if key_path.exists():
            logger.info(f"Loading encryption key from: {key_path}")
            with open(key_path, 'rb') as f:
                key = f.read()
            if not key:
                logger.error(f"Encryption key file exists but is empty: {key_path}")
                raise ValueError("Encryption key file is empty.")
            logger.debug("Encryption key loaded successfully.")
            return key
        else:
            logger.warning(f"Encryption key file not found at: {key_path}. Generating a new key.")
            key = generate_encryption_key()
            try:
                # Ensure the directory exists before writing
                key_path.parent.mkdir(parents=True, exist_ok=True)
                with open(key_path, 'wb') as f:
                    f.write(key)
                logger.info(f"New encryption key generated and saved to: {key_path}")
                return key
            except IOError as e:
                logger.error(f"Failed to save new encryption key to {key_path}: {e}", exc_info=True)
                raise # Re-raise the exception
            except Exception as e:
                 logger.error(f"An unexpected error occurred saving the key to {key_path}: {e}", exc_info=True)
                 raise # Re-raise the exception

    except Exception as e:
        # Catch any other unexpected errors during the process
        logger.error(f"Error loading or generating encryption key from {key_path}: {e}", exc_info=True)
        raise # Re-raise the exception


# --- Keep a cached key in memory after first load/generation ---
_cached_key = None

def get_key():
    """Gets the encryption key, loading/generating it only once."""
    global _cached_key
    if _cached_key is None:
        _cached_key = load_or_generate_and_save_key()
    return _cached_key

def encrypt_data(data):
    """Encrypt data using the automatically loaded/generated key."""
    try:
        key = get_key() # Use the function to get the key
        fernet = Fernet(key)

        # Ensure data is bytes before encryption
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        elif isinstance(data, bytes):
            data_bytes = data
        else:
            # Handle other types if necessary, or raise an error
            logger.error(f"Unsupported data type for encryption: {type(data)}")
            raise TypeError("Data must be string or bytes to encrypt.")

        encrypted_data = fernet.encrypt(data_bytes)
        logger.debug("Data encrypted successfully.")
        return encrypted_data
    except Exception as e:
        logger.error(f"Error encrypting data: {e}", exc_info=True)
        raise # Re-raise the exception

def decrypt_data(encrypted_data):
    """Decrypt data using the automatically loaded/generated key."""
    try:
        key = get_key() # Use the function to get the key
        fernet = Fernet(key)

        # Ensure input is bytes
        if not isinstance(encrypted_data, bytes):
             logger.error(f"Data to decrypt must be bytes, got: {type(encrypted_data)}")
             raise TypeError("Encrypted data must be bytes to decrypt.")

        decrypted_data_bytes = fernet.decrypt(encrypted_data)
        logger.debug("Data decrypted successfully.")
        # Optionally, try decoding to UTF-8, but return bytes if it fails
        try:
            return decrypted_data_bytes.decode('utf-8')
        except UnicodeDecodeError:
            logger.warning("Decrypted data is not valid UTF-8, returning as bytes.")
            return decrypted_data_bytes
    except Exception as e:
        # Fernet raises InvalidToken if decryption fails (wrong key, corrupted data)
        logger.error(f"Error decrypting data: {e}", exc_info=True)
        raise # Re-raise the exception

