import hashlib
import hmac
from datetime import datetime, timezone, timedelta
from typing import Dict, Any


import time
import random

from jose import jws
from jose.constants import ALGORITHMS


class BitzlatoAuthV1:
    def __init__(self, key_: dict, email: str, kid: str):
        self.kid = kid
        self.key = key_
        self.email = email

    def _get_token(self):
        claims = {
            "email": self.email,
            "aud": "usr",
            "iat": int(time.time()),
            "jti": hex(random.getrandbits(64))
        }
        return jws.sign(claims, self.key, headers={"kid": self.kid}, algorithm=ALGORITHMS.ES256)

    def get_headers(self):
        return {
            "Authorization": "Bearer " + self._get_token(),
        }


class BitzlatoAuthV2:
    """
    Auth class required by bitzlato.com API
    Learn more at https://bitzlato.com
    """
    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        # POSIX epoch for nonce
        self.date_epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)

    def _nonce(self):
        """ Function created to enable patching during unit tests execution.
        :return: time based nonce
        """
        date_now = datetime.now(timezone.utc)
        posix_timestamp_millis = int(((date_now - self.date_epoch) // timedelta(microseconds=1)) // 1000)
        return str(posix_timestamp_millis)

    def generate_signature(self, auth_payload) -> (Dict[str, Any]):
        """
        Generates a HS256 signature from the payload.
        :return: the HS256 signature
        """
        return hmac.new(
            self.secret_key.encode('utf-8'),
            msg=auth_payload.encode('utf-8'),
            digestmod=hashlib.sha256).hexdigest()

    def get_headers(self) -> (Dict[str, Any]):
        """
        Generates authentication headers required by Bitzlato.com
        :return: a dictionary of auth headers
        """
        # Must use UTC timestamps for nonce, can't use tracking nonce
        nonce = self._nonce()
        auth_payload = nonce + self.api_key
        signature = self.generate_signature(auth_payload)
        return {
            "X-Auth-Apikey": self.api_key,
            "X-Auth-Nonce": nonce,
            "X-Auth-Signature": signature,
            "Content-Type": "application/json",
        }