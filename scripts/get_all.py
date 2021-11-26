from app.server import get_all

from sys import argv
import json
from app import config

bsn = argv[1]

summary = get_all(bsn)

print("\n\n\nResponse\n\n\n")
json.dumps(summary, indent=4)
print("\n\n\nend.Response\n\n\n")
