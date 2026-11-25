#!/usr/bin/env python3
"""Erzeugt src/data/quizzes.json aus den YAML-Dateien (data/<sprache>/<thema>.yaml).
Die richtige Antwort wird nicht im Klartext abgelegt, sondern als SHA-256 (id + Position)."""
import sys, json, hashlib, pathlib, yaml
quelle = pathlib.Path(sys.argv[1]); ziel = pathlib.Path(sys.argv[2])
THEMEN = [
 ('ausbildungsverstaendnis', {'de':'Ausbildungsverständnis','fr':'Conception de la formation','it':'Concezione della formazione'}),
 ('ftem', {'de':'FTEM','fr':'FTEM','it':'FTEM'}),
 ('wertvoller-sport', {'de':'Wertvoller Sport','fr':'Un sport respectueux des valeurs éthiques','it':'Sport rispettoso dei valori etici'}),
 ('erscheinungsformen', {'de':'Erscheinungsformen und Trainingsformen','fr':'Formes caractéristiques et formes d’entraînement','it':'Forme caratteristiche e forme di allenamento'}),
 ('rechte-pflichten', {'de':'Rechte und Pflichten','fr':'Droits et devoirs','it':'Diritti e doveri'}),
 ('planung-lager', {'de':'Planung Lager','fr':'Planification de camp','it':'Pianificazione del campo'}),
]
h = lambda i, n: hashlib.sha256(f'quiz:{i}:{n}'.encode()).hexdigest()
out = {'themen': [], 'quiz': {}}
for slug, titel in THEMEN:
    out['themen'].append({'slug': slug, 'titel': titel}); out['quiz'][slug] = {}
    ids = None
    for sp in ('de','fr','it'):
        d = yaml.safe_load((quelle/sp/f'{slug}.yaml').read_text(encoding='utf8'))
        fr = [{'id': f['id'], 'q': f['frage'], 'a': f['antworten'], 'k': h(f['id'], f['richtig']-1)} for f in d['fragen']]
        cur = [(f['id'], f['k']) for f in fr]
        assert ids is None or ids == cur, f'{slug}/{sp}: IDs oder richtige Positionen weichen von DE ab'
        ids = cur; out['quiz'][slug][sp] = fr
ziel.write_text(json.dumps(out, ensure_ascii=False, separators=(',',':')), encoding='utf8')
print('OK', {s: len(out['quiz'][s]['de']) for s,_ in THEMEN})
