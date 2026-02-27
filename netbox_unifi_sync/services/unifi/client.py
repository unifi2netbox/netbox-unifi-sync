from .resources import BaseResource
import logging

logger = logging.getLogger(__name__)


class Client(BaseResource):
    """
    UniFi client (STA) resource.

    Integration API v1:  /sites/{site_id}/clients
        Returns all known clients (online + recently offline) with lastSeen timestamp.

    Legacy API:  /api/s/{site_name}/stat/user
        Returns all known clients with last_seen timestamp.
    """
    API_PATH = "/api/s"
    BASE_PATH = "stat"
    LEGACY_ENDPOINT = "user"
    INTEGRATION_API_PATH = "/sites"
    INTEGRATION_ENDPOINT = "clients"

    def __init__(self, unifi, site, **kwargs):
        self.unifi = unifi
        self.site = site
        if getattr(unifi, "api_style", None) == "integration":
            super().__init__(
                unifi,
                site,
                endpoint=self.INTEGRATION_ENDPOINT,
                api_path=self.INTEGRATION_API_PATH,
                base_path=None,
                **kwargs,
            )
        else:
            super().__init__(
                unifi,
                site,
                endpoint=self.LEGACY_ENDPOINT,
                api_path=self.API_PATH,
                base_path=self.BASE_PATH,
                **kwargs,
            )
