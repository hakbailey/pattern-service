import logging
from typing import Dict
from typing import Optional

import requests
from requests import Session
from requests.auth import HTTPBasicAuth

from pattern_service.settings.aap import AAP_PASSWORD
from pattern_service.settings.aap import AAP_USERNAME
from pattern_service.settings.aap import AAP_VALIDATE_CERTS

logger = logging.getLogger(__name__)


def get_http_session() -> Session:
    """Creates and returns a new Session instance with AAP credentials."""
    session = Session()
    session.auth = HTTPBasicAuth(AAP_USERNAME, AAP_PASSWORD)
    session.verify = AAP_VALIDATE_CERTS
    session.headers.update({"Content-Type": "application/json"})
    return session


def get(url: str, *, params: Optional[Dict] = None) -> requests.Response:
    with get_http_session() as session:
        response = session.get(url, params=params, stream=True)
        response.raise_for_status()
        return response
