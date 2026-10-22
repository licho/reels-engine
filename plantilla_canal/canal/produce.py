"""python3 -m canal.produce SPEC.py texto|hoja|preview|check|sinvoz|final VOZ.mp3"""
from . import ROOT  # registra la configuración
from reels_engine.produce import main
if __name__ == "__main__":
    main()
