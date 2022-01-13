import base64
from unittest import TestCase

from app.helpers import decrypt, encrypt


class EncryptHelpersTest(TestCase):
    identifier = "123123123"
    secret_key = "abcdefghijklmnop"

    def test_encrypt(self):

        # Generate (bytes)encrypted_payload and (bytes)iv
        (encrypted_string, iv) = encrypt(self.identifier, self.secret_key)

        payload_string = base64.urlsafe_b64encode(iv + encrypted_string).decode()

        payload_bytes = base64.urlsafe_b64decode(payload_string.encode())

        payload_iv = payload_bytes[:16]
        payload_bsn = payload_bytes[16:]

        payload_identifier = decrypt(payload_bsn, payload_iv, self.secret_key)

        self.assertEqual(self.identifier, payload_identifier)
