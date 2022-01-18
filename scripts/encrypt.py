import base64

from app.helpers import decrypt, encrypt

identifier = "123123123"
secret_key = ""

# Generate (bytes)encrypted_payload and (bytes)iv
(encrypted_string, iv) = encrypt(identifier, secret_key)

payload_string = base64.urlsafe_b64encode(iv + encrypted_string).decode()
# payload_string = payload

print(payload_string)

payload_bytes = base64.urlsafe_b64decode(payload_string.encode("ASCII"))

payload_iv = payload_bytes[:16]
payload_bsn = payload_bytes[16:]

payload_identifier = decrypt(payload_bsn, payload_iv, secret_key)

assert identifier == payload_identifier

print("Success!!", payload_identifier)
