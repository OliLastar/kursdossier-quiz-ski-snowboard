"""Erfolgskriterien (Oberfläche), gegen dist/ im echten Browser:
E1 6 Themen je Sprache; E2 alle richtig -> Bestanden + Zertifikat mit Name; E3 eine falsch -> Nicht bestanden, kein Zertifikat,
E4 nirgends wird eine richtige Antwort markiert/genannt; E5 Wiederholen startet ein neues Quiz; E6 Sprachwechsel behält das Thema;
E7 Zertifikat ohne Namen nicht möglich; E8 keine Konsolenfehler."""
import sys, yaml, pathlib, threading, http.server, functools, re
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
SLUGS = ['ausbildungsverstaendnis','ftem','wertvoller-sport','erscheinungsformen','rechte-pflichten','planung-lager']
def load(l, s): return {f['frage']: f['antworten'][f['richtig']-1] for f in yaml.safe_load((DATA/l/f'{s}.yaml').read_text(encoding='utf8'))['fragen']}, \
                       {f['frage']: [a for i,a in enumerate(f['antworten']) if i != f['richtig']-1] for f in yaml.safe_load((DATA/l/f'{s}.yaml').read_text(encoding='utf8'))['fragen']}
h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT/'dist'))
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), h); threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = f'http://127.0.0.1:{srv.server_address[1]}/'
fails = []; ok = lambda c, m: (None if c else fails.append(m))

def run(page, l, s, wrong_at=None):
    right, wrongs = load(l, s)
    page.goto(f'{URL}#/{l}/{s}'); page.reload()
    page.get_by_role('button').filter(has_text=re.compile('Quiz starten|Commencer|Avviare')).click()
    n = len(right); seen = 0
    while True:
        q = page.locator('legend').inner_text(); seen += 1
        # E4: während des Quiz nie eine Markierung ausser der eigenen Auswahl
        ok(page.locator('.opt.ok, .opt.right, .correct, [data-correct]').count() == 0, f'{l}/{s}: Markierung sichtbar')
        want = wrongs[q][0] if wrong_at == seen else right[q]
        page.locator('.opt', has_text=want).first.click()
        nxt = page.locator('.btn:not(.ghost)')
        nxt.click()
        if seen == n: break
    return n

with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox']); page = b.new_page()
    errs = []; page.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None); page.on('pageerror', lambda e: errs.append(str(e)))
    for l in ['de','fr','it']:
        page.goto(f'{URL}#/{l}'); page.reload()
        ok(page.locator('.theme').count() == 6, f'E1 {l}: 6 Themen')
    for l in ['de','fr','it']:
        for s in SLUGS:
            n = run(page, l, s)
            body = page.locator('main').inner_text()
            ok(re.search('Bestanden|Réussi|Superato', body) and not re.search('Nicht bestanden|Non réussi|Non superato', body), f'E2 {l}/{s}: nicht bestanden')
            ok(page.locator('.cert').count() == 0, f'E7 {l}/{s}: Zertifikat vor Namenseingabe')
            page.locator('.certform .btn').click()
            ok(page.locator('.cerr').count() == 1 and page.locator('.cert').count() == 0, f'E7 {l}/{s}: leerer Name akzeptiert')
            page.locator('.certform input').nth(0).fill('Anna'); page.locator('.certform input').nth(1).fill('Muster')
            page.locator('.certform .btn').click()
            c = page.locator('.cert').inner_text()
            ok('Anna Muster' in c and str(n) in c, f'E2 {l}/{s}: Zertifikat unvollständig')
    # E3/E5/E6 am Beispiel FTEM
    run(page, 'de', 'ftem', wrong_at=2)
    body = page.locator('main').inner_text()
    ok('Nicht bestanden' in body and '4 von 5' in body, 'E3: Fehlversuch nicht erkannt')
    ok(page.locator('.cert, .certform').count() == 0, 'E3: Zertifikat trotz Fehlversuch')
    right, wrongs = load('de','ftem')
    ok(not any(a in body for a in right.values()), 'E4: richtige Antwort im Ergebnis genannt')
    page.get_by_role('button', name='Quiz wiederholen').click()
    ok(page.locator('legend').count() == 1 and 'Frage 1 von 5' in page.locator('main').inner_text(), 'E5: kein neues Quiz')
    page.locator('.langs button', has_text='FR').click()
    ok('/fr/ftem' in page.url, 'E6: Sprachwechsel verliert Thema')
    ok(errs == [], f'E8: Konsolenfehler {errs}')
    b.close()
print('FEHLER:' if fails else 'ALLE ERFOLGSKRITERIEN ERFÜLLT', *fails, sep='\n')
sys.exit(1 if fails else 0)
