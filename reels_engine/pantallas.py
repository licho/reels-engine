"""Old Spanish name kept so existing channels keep working: same module as reels_engine.screens."""
import sys
from . import screens as _m
sys.modules[__name__] = _m
