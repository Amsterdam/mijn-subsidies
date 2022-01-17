from app.server import get_all

from sys import argv
import json
from app import config, server, sisa_service

bsn = argv[1]

with server.app.app_context():
    summary = sisa_service.get_all(bsn)

print("\n\n\nResponse\n\n\n")
json.dumps(summary, indent=4)
print("\n\n\nend.Response\n\n\n")
