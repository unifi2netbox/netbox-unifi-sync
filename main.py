"""Compatibility module alias for legacy ``import main`` usage."""

import sys

from unifi2netbox.services import sync_engine as _sync_engine


sys.modules[__name__] = _sync_engine
