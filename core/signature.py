import hmac
import hashlib
from typing import Dict

class SignatureStrategy:
    def sign(self, params: Dict[str, str], secret: str) -> str:
        raise NotImplementedError

class HMACSHA256Signature(SignatureStrategy):
    def sign(self, params: Dict[str, str], secret: str) -> str:
        data = ''.join(params[k] for k in sorted(params))
        return hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()

SIGNATURE_REGISTRY = {
    "bitvalex": HMACSHA256Signature(),
    "cryptomus": HMACSHA256Signature(),
}
