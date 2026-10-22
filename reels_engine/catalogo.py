"""Old Spanish name kept so existing channels keep working: same module as reels_engine.catalog."""
import sys
from . import catalog as _m
sys.modules[__name__] = _m
