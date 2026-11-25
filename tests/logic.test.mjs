// Erfolgskriterien (Logik): K1 nur 100 % besteht, K2 Hash statt Klartext, K3 Mischen ohne Verlust, K4 DE/FR/IT deckungsgleich
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { grade, newRound, hashOf } from '../src/lib/quiz.js'

const data = JSON.parse(readFileSync(new URL('../src/data/quizzes.json', import.meta.url)))
const slugs = data.themen.map((t) => t.slug)

// Richtige Position über den Hash ermitteln (so wie die App es prüft), nur für den Test.
const correctPick = async (f) => { for (let i = 0; i < 4; i++) if ((await hashOf(f.id, i)) === f.k) return i }

test('K1: nur alle richtig besteht', async () => {
  for (const s of slugs) for (const l of ['de', 'fr', 'it']) {
    const round = newRound(data.quiz[s][l]); const n = round.length
    const all = {}; for (const f of round) all[f.id] = await correctPick(f)
    assert.equal(await grade(round, all), n)
    const one = { ...all }; const f0 = round[0]; one[f0.id] = (all[f0.id] + 1) % 4
    assert.equal(await grade(round, one), n - 1)
    assert.equal(await grade(round, {}), 0)
  }
})
test('K2: kein Klartext-Antwortschlüssel in den Daten', () => {
  const raw = readFileSync(new URL('../src/data/quizzes.json', import.meta.url), 'utf8')
  assert.ok(!/richtig|correct|"r":/i.test(raw))
  for (const s of slugs) for (const l of ['de', 'fr', 'it']) for (const f of data.quiz[s][l]) assert.match(f.k, /^[0-9a-f]{64}$/)
})
test('K3: Mischen verliert nichts, 4 verschiedene Antworten', () => {
  for (const s of slugs) {
    const src = data.quiz[s].de; const r = newRound(src)
    assert.deepEqual(r.map((f) => f.id).sort(), src.map((f) => f.id).sort())
    for (const f of r) { assert.equal(f.opts.length, 4); assert.equal(new Set(f.opts.map((o) => o.text)).size, 4)
      assert.deepEqual(f.opts.map((o) => o.o).sort(), [0, 1, 2, 3]) }
  }
})
test('K4: DE/FR/IT haben dieselben Fragen-IDs und dieselbe richtige Position', () => {
  for (const s of slugs) {
    const sig = (l) => data.quiz[s][l].map((f) => `${f.id}:${f.k}`).join('|')
    assert.equal(sig('fr'), sig('de')); assert.equal(sig('it'), sig('de'))
  }
})
