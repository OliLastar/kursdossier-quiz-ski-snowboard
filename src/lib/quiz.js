// Logik ohne Oberfläche: mischen und auswerten. Die richtige Antwort liegt nur als Hash vor.
export const hashOf = async (id, n) => {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(`quiz:${id}:${n}`))
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, '0')).join('')
}

const shuffle = (arr) => {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

// Neue Runde: Fragen und Antworten in zufälliger Reihenfolge; "o" = ursprüngliche Position.
export const newRound = (fragen) =>
  shuffle(fragen).map((f) => ({
    id: f.id, q: f.q, k: f.k,
    opts: shuffle(f.a.map((text, o) => ({ text, o }))),
  }))

// Liefert nur die Anzahl richtiger Antworten, nie welche.
export const grade = async (round, picks) => {
  let n = 0
  for (const f of round) {
    const p = picks[f.id]
    if (p !== undefined && (await hashOf(f.id, p)) === f.k) n++
  }
  return n
}
