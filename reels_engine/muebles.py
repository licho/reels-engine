"""Old Spanish name kept so existing channels keep working: same module as reels_engine.furniture."""
import sys
from . import furniture as _m
sys.modules[__name__] = _m
