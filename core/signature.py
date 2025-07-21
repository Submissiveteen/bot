import hmac
import hashlib
from typing import Callable, Dict

class SignatureStrategy:
    def sign(self, params: Dict[str, str], secret: str) -> str:
        raise NotImplementedError


_REGISTRY: Dict[str, SignatureStrategy] = {}

def register_signature(name: str):
    def wrapper(cls):
        if not issubclass(cls, SignatureStrategy):
            raise TypeError("Must inherit from SignatureStrategy")
        _REGISTRY[name.lower()] = cls()
        return cls
    return wrapper


def get_signature_strategy(name: str) -> SignatureStrategy:
    return _REGISTRY.get(name.lower())


@register_signature("bitvalex")
class HMACSHA256Signature(SignatureStrategy):
    def sign(self, params: Dict[str, str], secret: str) -> str:
        data = ''.join(params[k] for k in sorted(params))
        return hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()


@register_signature("cryptomus")
class CryptoMusSignature(SignatureStrategy):
    def sign(self, params: Dict[str, str], secret: str) -> str:
        return HMACSHA256Signature().sign(params, secret)
