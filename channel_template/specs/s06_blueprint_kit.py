"""Example spec with the blueprint kit: question card, size comparison, steps, failure chain, charts, neon flows and
the answer card. Try it with:
  python3 -m channel.produce specs/s06_blueprint_kit.py preview 1 5 9 13 17
  python3 -m channel.produce specs/s06_blueprint_kit.py check"""
from reels_engine.core import *
from reels_engine.motion import tw
from reels_engine.blueprint import blueprint_bg, kicker, plan_stamp, VOLT
from reels_engine.blueprint.marks import flow_path, fact_tag, grid_wipe
from reels_engine.blueprint.charts import hbar_chart, limit_meter
from reels_engine.blueprint.parts import pump, plan_tank, plan_pipe
from reels_engine.blueprint.templates import question_card, size_compare, steps, failure_chain, answer_card

NAME = "s06_blueprint_kit"
LINES = [
    ("curious", "How big is a city water tank, really?", "How big is a *water tank*?"),
    ("calm", "Bigger than a bus. About as tall as a plane is long.", "Bigger than a *bus*"),
    ("calm", "Water is pumped up at night, stored, and falls by gravity during the day.", "Pump · store · *fall*"),
    ("serious", "If the pump fails, the tank empties and the pressure drops in every home.", "One pump fails… *every* tap feels it"),
    ("calm", "That is why cities keep the tank half full, never empty.", "Kept *half full*, never empty"),
]
FACT = {"fact": "FACT", "estimate": "ESTIMATE", "hypothetical": "HYPOTHETICAL"}

def sheet(c, kick):
    img, d = canvas(blueprint_bg(c.t))
    kicker(img, kick, 60, 236)
    plan_stamp(img, [("sheet", f"0{c.line + 1}/05"), ("system", "water")], 1020, 160)
    return img

def question(c):
    img = sheet(c, "HIDDEN INFRASTRUCTURE")
    question_card(img, "HOW BIG IS A\n*WATER TANK*?", 60, 420, appear_=tw(c.lt, 0, 1.6, 0, 1), size=84)
    pump(img, 540, 1050, 90, c.t)
    flow_path(img, [(160, 1050), (450, 1050)], c.t, VOLT, kind="dots")
    grid_wipe(img, tw(c.lt, 0, .35, 1, 0))
    return img

def compare(c):
    img = sheet(c, "TO SCALE")
    size_compare(img, [("person", "PERSON"), ("bus", "BUS"), ("plane", "PLANE")], (60, 520, 1020, 1300), k=tw(c.lt, 0, 2.4, 0, 1))
    fact_tag(img, "estimate", 60, 1360, labels=FACT)
    return img

def route(c):
    img = sheet(c, "STEP BY STEP")
    active = min(2, int(tw(c.lt, .3, 3.6, 0, 3)))
    steps(img, [("PUMP", "at night"), ("STORE", "in the tank"), ("FALL", "by gravity")], (60, 340, 1020, 900),
          active=active, t=c.t)
    plan_tank(img, 700, 1000, 960, 1280, .7, c.t, label="tank", percent=True)
    plan_pipe(img, [(120, 1320), (580, 1320), (580, 1260), (700, 1260)], c.t, w=20)
    return img

def failure(c):
    img = sheet(c, "CHAIN REACTION")
    failure_chain(img, ["PUMP", "TANK", "PRESSURE", "TAPS"], (60, 340, 1020, 1300), fail=0, k=tw(c.lt, .5, 3, 0, 1),
                  t=c.t)
    return img

def answer(c):
    img = sheet(c, "THE ANSWER")
    hbar_chart(img, [("BUS", 12), ("PLANE", 38), ("TANK", 30)], 60, 420, 900, k=tw(c.lt, 0, 1.4, 0, 1), unit=" m",
               highlight=2)
    limit_meter(img, 540, 1000, 200, tw(c.lt, .4, 2, 0, 50), 100, 85, label="tank level", unit="%")
    answer_card(img, "Kept *half full*, never empty", 60, 1120, 960, k=tw(c.lt, 1, 2, 0, 1), label="ANSWER")
    fact_tag(img, "hypothetical", 60, 1330, labels=FACT)
    return img

SCENES = [(0, question), (1, compare), (2, route), (3, failure), (4, answer)]
SFX = [(0, .2, "pop")]
MUSIC = ("pad", [], None)
