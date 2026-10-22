"""python3 -m channel.publish VIDEO.mp4 "YYYY-MM-DD HH:MM" --title "..." | setup youtube|facebook … | status"""
import sys
from . import ROOT  # registers the configuration
from reels_engine.publish import main
if __name__ == "__main__":
    sys.exit(main())
