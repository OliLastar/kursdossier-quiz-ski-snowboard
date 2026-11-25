#!/usr/bin/env python3
"""Prüft alle Fragen: 4 verschiedene Antworten, genau 1 richtig, Kahoot-Limits, gleiche IDs in DE/FR/IT."""
import sys, glob, os, yaml
LANGS = ("de", "fr", "it")
MAX_Q, MAX_A = 120, 75          # harte Kahoot-Limits
SOLL_Q, SOLL_A = 90, 35         # interne Zielwerte (nur Hinweis)
def laden(root):
    daten = {}
    for lang in LANGS:
        for pfad in sorted(glob.glob(os.path.join(root, "data", lang, "*.yaml"))):
            with open(pfad, encoding="utf-8") as f:
                d = yaml.safe_load(f)
            for fr in d["fragen"]:
                daten.setdefault(lang, {})[fr["id"]] = (os.path.basename(pfad), fr)
    return daten
def main(root="."):
    fehler, hinweise = [], []
    daten = laden(root)
    ids = {l: set(daten.get(l, {})) for l in LANGS}
    for l in LANGS[1:]:
        if ids[l] != ids["de"]:
            fehler.append(f"{l}: IDs weichen von de ab: {sorted(ids[l] ^ ids['de'])}")
    for lang, fragen in daten.items():
        for id_, (datei, fr) in fragen.items():
            a = fr["antworten"]; ort = f"{lang}/{datei}:{id_}"
            if len(a) != 4 or len(set(a)) != 4: fehler.append(f"{ort}: genau 4 verschiedene Antworten nötig")
            if fr["richtig"] not in (1, 2, 3, 4): fehler.append(f"{ort}: richtig muss 1 bis 4 sein")
            if len(fr["frage"]) > MAX_Q: fehler.append(f"{ort}: Frage {len(fr['frage'])} > {MAX_Q}")
            if any(len(x) > MAX_A for x in a): fehler.append(f"{ort}: Antwort > {MAX_A}")
            if len(fr["frage"]) > SOLL_Q: hinweise.append(f"{ort}: Frage {len(fr['frage'])} > {SOLL_Q}")
            hinweise += [f"{ort}: Antwort '{x}' {len(x)} > {SOLL_A}" for x in a if len(x) > SOLL_A]
    for l in LANGS[1:]:
        for id_, (_, fr) in daten.get(l, {}).items():
            if id_ in daten["de"] and fr["richtig"] != daten["de"][id_][1]["richtig"]:
                fehler.append(f"{l}:{id_}: Position der richtigen Antwort weicht von de ab")
    for h in hinweise: print("Hinweis:", h)
    for e in fehler: print("FEHLER:", e)
    print(f"{sum(len(v) for v in daten.values())} Fragen geprüft, {len(fehler)} Fehler, {len(hinweise)} Hinweise")
    return 1 if fehler else 0
if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
