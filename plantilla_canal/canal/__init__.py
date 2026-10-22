"""Paquete del canal. Registra la configuración ANTES de que se use cualquier parte del motor."""
import os
from reels_engine import Channel, configure

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

configure(Channel(
    name="mi-canal",
    root=ROOT,
    outdir="/tmp/mi_canal_out",
    caption_highlight=(80, 220, 120),        # palabras *resaltadas* en verde
    chip_bg=(30, 110, 210),                  # letreros azules
    code_dirs=("canal",),
    catalog_out="canal/CATALOGO.md",
    catalog_header=("# Catálogo de mi canal\n", "Generado con `python3 -m canal.catalogo`.\n"),
    catalog_api=(("reels_engine.core", "reels_engine.core"), ("reels_engine.motion", "reels_engine.motion")),
    catalog_maps=("canal.personajes", "canal.props", "canal.fondos"),
))
