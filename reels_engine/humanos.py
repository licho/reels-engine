"""Old Spanish name kept so existing channels keep working: same module as reels_engine.humans."""
import sys
from . import humans as _m
sys.modules[__name__] = _m
