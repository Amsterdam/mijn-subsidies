from app.server import get_all

from sys import argv
import json
from app import config, server, sisa_service

bsn = argv[1]

print("endpoint", config.SISA_API_ENDPOINT)
print("encryption key", config.SISA_ENCRYPTION_KEY)
print("client id", config.SISA_CLIENT_ID)
print("client secret", config.SISA_CLIENT_SECRET)

with server.app.app_context():
    summary = sisa_service.get_all(bsn)

print("\n\n\nResponse\n\n\n")
json.dumps(summary, indent=4)
print("\n\n\nend.Response\n\n\n")
