import base64
import random
import hashlib
import hmac
import secrets
import struct


def encrypt(text,key):

    initialization_vector = secrets.token_bytes(16)

    hmac_key = hashlib.sha256(key + b"hmac").digest()

    hmac_obj = hmac.new(hmac_key, digestmod=hashlib.sha256)

    ciphertext = bytearray()
    for i, byte in enumerate(text):
        xor_byte = byte ^ key[(i + struct.unpack(">I", initialization_vector[:4])[0]) % len(key)]
        ciphertext.append(xor_byte)
        hmac_obj.update(bytes([xor_byte]))

    mac_tag = hmac_obj.digest()

    encrypted_message = initialization_vector + mac_tag + bytes(ciphertext)

    return base64.b64encode(encrypted_message)

def decrypt(encrypted_content, key):
        """Decrypts content using XOR cipher with HMAC verification."""
        initialization_vector = encrypted_content[:16]  
        mac_tag = encrypted_content[16:48]  
        ciphertext = encrypted_content[48:]

        # Get HMAC key from the main key
        hmac_key = hashlib.sha256(key + b"hmac").digest()

        # Verify the HMAC tag
        hmac_obj = hmac.new(hmac_key, digestmod=hashlib.sha256)
        for byte in ciphertext:
            hmac_obj.update(bytes([byte]))  # Update HMAC with the ciphertext byte

        if not hmac.compare_digest(hmac_obj.digest(), mac_tag):
            print("HMAC verification failed. Data integrity compromised.")
            return None

        # Decrypt the ciphertext
        plaintext = bytearray()
        for i, byte in enumerate(ciphertext):
            xor_byte = byte ^ key[(i + struct.unpack(">I", initialization_vector[:4])[0]) % len(key)]
            plaintext.append(xor_byte)

        return bytes(plaintext)