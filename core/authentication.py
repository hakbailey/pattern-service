import logging
from datetime import datetime
from typing import Optional
from typing import Tuple
from typing import Union

import jwt
from ansible_base.jwt_consumer.common.cert import JWTCert
from ansible_base.jwt_consumer.common.cert import JWTCertException
from ansible_base.jwt_consumer.common.exceptions import InvalidTokenException
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request

from core.models import TokenUser

logger = logging.getLogger(__name__)

REQUIRED_USER_DATA = [
    "username",
    "first_name",
    "last_name",
    "email",
    "is_superuser",
]


class PatternServiceAuthentication(BaseAuthentication):

    def authenticate(
        self, request: Request
    ) -> Tuple[Optional[TokenUser], Optional[dict]]:
        logger.debug("Starting JWT Authentication")

        if request is None:
            return None, None

        jwt_token = request.headers.get("X-DAB-JW-TOKEN")
        request_id = request.headers.get("X-Request-Id")
        if not jwt_token:
            logger.debug("X-DAB-JW-TOKEN header not set for JWT authentication")
            return None, None
        logger.debug(f"Received JWT auth token: {jwt_token}")

        token_claims = parse_token(jwt_token, request_id)
        if not token_claims:
            return None, None

        user = get_user(jwt_token, token_claims)
        if not user:
            return None, None

        logger.debug(f"User from token: {user}")
        logger.debug(f"Token claims: {token_claims}")

        return user, token_claims


def parse_token(token: str, request_id: str) -> Optional[dict]:
    cert_object = JWTCert()
    try:
        cert_object.get_decryption_key()
    except JWTCertException as e:
        logger.error(e)
        raise AuthenticationFailed(str(e))
    if cert_object.key is None:
        return None

    try:
        validated_token = validate_token(token, cert_object.key, request_id)
    except jwt.exceptions.DecodeError as e:
        # This exception means the decryption key failed... maybe it was because the
        # cache is bad.
        if not cert_object.cached:
            # It wasn't cached anyway so we can just raise our exception
            logger.error("JWT decoding failed, check your key and generated token")
            raise AuthenticationFailed(str(e))

        # We had a cached key so lets get the key again ignoring the cache
        old_key = cert_object.key
        try:
            cert_object.get_decryption_key(ignore_cache=True)
        except JWTCertException as jce:
            logger.error("Failed to get JWT token on the second try")
            raise AuthenticationFailed(str(jce))
        if old_key == cert_object.key:
            # The new key matched the old key so don't even try and decrypt again, the
            # key just doesn't match
            logger.error(
                "JWT decoding failed. Cached key was correct, check your key and "
                "generated token"
            )
            raise AuthenticationFailed(str(e))
        # Since we got a new key, lets go ahead and try to validate the token again.
        # If it fails this time we can just raise whatever
        validated_token = validate_token(token, cert_object.key, request_id)

    return validated_token


def validate_token(
    token: str,
    decryption_key: Union[bytes, str, jwt.PyJWK],
    request_id: Optional[str] = None,
) -> dict:
    validated_token_claims = None

    try:
        logger.info("Decoding JWT token")
        validated_token_claims = decode_jwt_token(token, decryption_key)
    except jwt.exceptions.DecodeError as e:
        raise e
    except jwt.exceptions.ExpiredSignatureError:
        expired_token = decode_jwt_token(
            token,
            decryption_key,
            additional_options={"verify_exp": False},
        )
        expired_time = expired_token.get("exp")
        now = datetime.now().timestamp()
        time_diff = int(now - expired_time)
        logger.error(
            f"JWT expired {time_diff} seconds ago - check for clock skew. "
            f"Request ID: {request_id}"
        )
        raise InvalidTokenException
    except jwt.exceptions.InvalidAudienceError as e:
        logger.error("JWT did not come for the correct audience")
        raise AuthenticationFailed(str(e))
    except jwt.exceptions.InvalidIssuerError as e:
        logger.error("JWT did not come from the correct issuer")
        raise AuthenticationFailed(str(e))
    except jwt.exceptions.MissingRequiredClaimError as e:
        logger.error("Failed to decrypt JWT")
        raise AuthenticationFailed(str(e))
    except Exception as e:
        logger.error(f"Unexpected error occurred decrypting JWT: {str(e)}.")
        raise AuthenticationFailed

    logger.debug(validated_token_claims)

    # Ensure all of the required user data is present
    missing_user_data = []
    for field in REQUIRED_USER_DATA:
        if field not in validated_token_claims["user_data"]:
            missing_user_data.append(field)
    if missing_user_data:
        logger.error(
            f"JWT did not have proper user_data, missing fields: {missing_user_data}"
        )
        raise AuthenticationFailed

    return validated_token_claims


def decode_jwt_token(
    token: str,
    decryption_key: Union[bytes, str, jwt.PyJWK],
    additional_options: dict = {},
) -> dict:
    local_required_fields = ["sub", "user_data", "exp", "claims_hash", "version"]
    options = {"require": local_required_fields}
    options.update(additional_options)
    return jwt.decode(
        token,
        decryption_key,
        audience="ansible-services",
        options=options,
        issuer="ansible-issuer",
        algorithms=["RS256"],
    )


def get_user(jwt_token: str, token_claims: dict) -> Optional[TokenUser]:
    """
    Returns a stateless user object backed by the given validated token claims.
    """
    if "sub" not in token_claims:
        # The TokenUser class assumes tokens will have a recognizable user
        # identifier claim (ansible ID).
        raise InvalidTokenException(
            detail="Token contained no recognizable user identification"
        )

    return TokenUser(token_claims, jwt_token)
