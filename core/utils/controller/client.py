import logging
import urllib.parse
from typing import Any
from typing import Dict
from typing import Optional

import requests
from django.conf import settings
from requests import Session

from ..http_helpers import safe_json

logger = logging.getLogger(__name__)


def get_http_session(token: str) -> Session:
    """Creates and returns a new Session instance with AAP credentials."""
    session = Session()
    session.verify = settings.AAP_VALIDATE_CERTS
    session.headers.update({"Content-Type": "application/json"})
    session.headers.update({"X-DAB-JW-TOKEN": token})
    return session


def get(
    session: Session, url: str, *, params: Optional[Dict] = None
) -> requests.Response:
    logger.debug(f"GET URL: {url}")
    response = session.get(url, params=params, stream=True)
    response.raise_for_status()
    return response


def post(session: requests.Session, path: str, data: Dict) -> Dict[str, Any]:
    """
    Create a resource on the AAP controller.
    Args:
        session: Pre-existing session.
        path: Controller endpoint, e.g. "/projects/" (must include trailing slash).
        data: JSON payload to send.
    Returns:
        JSON for the created or pre‑existing object.
    Raises:
        requests.HTTPError
    """
    url = urllib.parse.urljoin(settings.AAP_URL, path)
    logger.debug(f"POST URL: {url}")

    try:
        response = session.post(url, json=data)
        response.raise_for_status()
        return safe_json(lambda: response)()

    except requests.exceptions.HTTPError as e:
        logger.error(e.response.reason)
        logger.error(e.response.json())
        raise
