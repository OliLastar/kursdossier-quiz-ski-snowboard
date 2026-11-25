#!/usr/bin/env python3
"""Exportiert die Fragen in die offizielle Kahoot-Excel-Vorlage (pro Sprache, optional pro Thema).
Verwendung: export_kahoot.py --vorlage Kahoot_Quiz_Import_Template.xlsx --sprache de [--thema ftem] [--zeit 20] [--out out/]
Die Vorlage wird nicht mitgeliefert: bei Kahoot herunterladen."""
import argparse, glob, os, sys, yaml, openpyxl
ZEITEN = (5, 10, 15, 20, 30, 45, 60, 90, 120, 180, 240)
p = argparse.ArgumentParser()
p.add_argument("--vorlage", required=True); p.add_argument("--sprache", required=True, choices=("de", "fr", "it"))
p.add_argument("--thema"); p.add_argument("--zeit", type=int, default=20); p.add_argument("--out", default="out")
a = p.parse_args()
assert a.zeit in ZEITEN, f"Zeit muss einer von {ZEITEN} sein"
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pfade = sorted(glob.glob(os.path.join(root, "data", a.sprache, (a.thema or "*") + ".yaml")))
if not pfade: sys.exit("Keine Daten gefunden")
fragen = [f for pf in pfade for f in yaml.safe_load(open(pf, encoding="utf-8"))["fragen"]]
wb = openpyxl.load_workbook(a.vorlage); ws = wb.active
for i, f in enumerate(fragen):
    r = 9 + i
    ws.cell(r, 2).value = f["frage"]
    for j, x in enumerate(f["antworten"]): ws.cell(r, 3 + j).value = x
    ws.cell(r, 7).value = a.zeit; ws.cell(r, 8).value = str(f["richtig"])
os.makedirs(a.out, exist_ok=True)
name = os.path.join(a.out, f"Kahoot_Ski_{a.sprache.upper()}" + (f"_{a.thema}" if a.thema else "") + ".xlsx")
wb.save(name); print(f"{len(fragen)} Fragen -> {name}")
