import logging
from typing import Optional
from typing import Tuple

import jwt
from ansible_base.jwt_consumer.common.auth import JWTAuthentication
from ansible_base.jwt_consumer.common.auth import JWTCommonAuth
from ansible_base.jwt_consumer.common.cert import JWTCert
from ansible_base.jwt_consumer.common.cert import JWTCertException
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request

from core.models import TokenUser

logger = logging.getLogger(__name__)


class PatternServiceJWTCommonAuth(JWTCommonAuth):

    def parse_jwt_token(self, request: Request) -> None:
        """
        Parses the given request token, sets self.user and self.token values.
        """

        self.user = None
        self.token = None

        logger.debug("Starting JWT Authentication")
        if request is None:
            return

        token_from_header = request.headers.get("X-DAB-JW-TOKEN", None)
        request_id = request.headers.get("X-Request-Id")
        if not token_from_header:
            logger.debug("X-DAB-JW-TOKEN header not set for JWT authentication")
            return
        logger.debug(f"Received JWT auth token: {token_from_header}")

        cert_object = JWTCert()
        try:
            cert_object.get_decryption_key()
        except JWTCertException as jce:
            logger.error(jce)
            raise AuthenticationFailed(jce)

        if cert_object.key is None:
            return

        try:
            self.token = self.validate_token(
                token_from_header, cert_object.key, request_id
            )
        except jwt.exceptions.DecodeError as de:
            # This exception means the decryption key failed... maybe it was because the
            # cache is bad.
            if not cert_object.cached:
                # It wasn't cached anyway so we an just raise our exception
                self.log_and_raise(
                    "JWT decoding failed: %(e)s, check your key and generated token",
                    {"e": de},
                )

            # We had a cached key so lets get the key again ignoring the cache
            old_key = cert_object.key
            try:
                cert_object.get_decryption_key(ignore_cache=True)
            except JWTCertException as jce:
                self.log_and_raise(
                    "Failed to get JWT token on the second try: %(e)s", {"e": jce}
                )
            if old_key == cert_object.key:
                # The new key matched the old key so don't even try and decrypt again,
                # the key just doesn't match
                self.log_and_raise(
                    "JWT decoding failed: %(e)s, cached key was correct; check your key "
                    "and generated token",
                    {"e": de},
                )
            # Since we got a new key, lets go ahead and try to validate the token again.
            # If it fails this time we can just raise whatever
            self.token = self.validate_token(
                token_from_header, cert_object.key, request_id
            )

        self.user = self.get_user()

    def get_user(self) -> Optional[TokenUser]:
        """
        Returns a stateless user object which is backed by the given validated
        token.
        """
        if not self.token:
            return None
        if "sub" not in self.token:
            # The TokenUser class assumes tokens will have a recognizable user
            # identifier claim.
            raise InvalidToken(
                detail="Token contained no recognizable user identification"
            )

        return TokenUser(self.token)


class PatternServiceAuthentication(JWTAuthentication):

    def __init__(self) -> None:
        self.common_auth = PatternServiceJWTCommonAuth(self.map_fields)

    def authenticate(
        self, request: Request
    ) -> Tuple[Optional[TokenUser], Optional[dict]]:
        self.common_auth.parse_jwt_token(request)

        logger.debug(f"User from token: {self.common_auth.user}")
        logger.debug(f"Token from token: {self.common_auth.token}")

        return self.common_auth.user, self.common_auth.token


class InvalidToken(AuthenticationFailed):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Token does not contain a valid Ansible ID for the user"
    default_code = "token_not_valid"
