"""Builds the passcode-protected defects list at /defects/.
The repo is public, so the defects are never committed as plain text: this script encrypts
defects.json (AES-256-GCM, key from the passcode via PBKDF2-SHA256) into defects/data.enc.json,
and the page decrypts it in the browser with the passcode.

Setup:  keep the plain source at ~/defects-src/defects.json (outside the repo; also gitignored as defects.json).
Usage:  DEFECTS_PASSCODE='...' python3 tools/build_defects.py [path/to/defects.json]
Then commit defects/data.enc.json and push to main. To close an item, set "status": "closed" and "closed" date, rebuild, push.

defects.json: {"updated": "2026-11-09", "defects": [{"id","lot","location","title","detail","severity","status","raised","comment","closed","photos":[]}]}
status: open | in_progress | fixed | closed     severity: minor | major | critical
Photos are not encrypted here; keep them out of the repo (link to a shared folder in "detail" for now)."""
import base64, json, os, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITER = 250_000
src = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser('~/defects-src/defects.json')
pw = os.environ.get('DEFECTS_PASSCODE')
if not pw:
    sys.exit('Set DEFECTS_PASSCODE')
data = json.load(open(src))
b = lambda x: base64.b64encode(x).decode()
salt, iv = os.urandom(16), os.urandom(12)
key = PBKDF2HMAC(hashes.SHA256(), 32, salt, ITER).derive(pw.encode())
ct = AESGCM(key).encrypt(iv, json.dumps(data, separators=(',', ':')).encode(), None)
os.makedirs(os.path.join(ROOT, 'defects'), exist_ok=True)
json.dump({'v': 1, 'iter': ITER, 'salt': b(salt), 'iv': b(iv), 'ct': b(ct)}, open(os.path.join(ROOT, 'defects', 'data.enc.json'), 'w'))
print('defects/data.enc.json written,', len(data.get('defects', [])), 'items')
