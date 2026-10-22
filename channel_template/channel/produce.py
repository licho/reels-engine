"""python3 -m channel.produce SPEC.py text|sheet|preview|check|silent|final VOICE.mp3"""
from . import ROOT  # registers the configuration
from reels_engine.produce import main
if __name__ == "__main__":
    main()
