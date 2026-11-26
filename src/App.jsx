import { useEffect, useState } from 'react'
import data from './data/quizzes.json'
import { LANGS, LOCALE, T } from './lib/i18n.js'
import { grade, newRound } from './lib/quiz.js'
import logoJs from './assets/logo-js.png'
import logoSki from './assets/logo-swiss-ski.png'

// Adresse: #/<sprache>/<thema> – jedes Quiz hat so einen eigenen Link.
// Enthalten die Daten nur ein Thema, ist die Seite ein einzelnes Quiz (ohne Themenwahl).
const SINGLE = data.themen.length === 1 ? data.themen[0].slug : null
const readHash = () => {
  const [, l, s] = window.location.hash.split('/')
  return { lang: LANGS.includes(l) ? l : 'de', slug: SINGLE || (data.quiz[s] ? s : null) }
}

export default function App() {
  const [{ lang, slug }, setNav] = useState(readHash)
  useEffect(() => {
    const f = () => setNav(readHash())
    window.addEventListener('hashchange', f)
    return () => window.removeEventListener('hashchange', f)
  }, [])
  const go = (l, s) => {
    setNav({ lang: l, slug: s })
    try { window.location.hash = `/${l}${s && !SINGLE ? `/${s}` : ''}` } catch { /* Adresse nicht beschreibbar (z. B. eingebettete Vorschau) */ }
  }
  const t = T[lang]
  useEffect(() => { document.documentElement.lang = lang; document.title = SINGLE ? `${data.themen[0].titel[lang]} – ${t.title}` : t.title }, [lang, t.title])

  return (
    <div className="wrap">
      <header className="no-print">
        <div className="brand">
          <span className="jslogo"><img src={logoJs} alt="J+S" /></span>
          <span className="jslogo"><img className="skilogo" src={logoSki} alt="Swiss-Ski" /></span>
        </div>
        <nav className="langs" aria-label={t.lang}>
          {LANGS.map((l) => (
            <button key={l} className={l === lang ? 'active' : ''} onClick={() => go(l, slug)} aria-pressed={l === lang}>{l.toUpperCase()}</button>
          ))}
        </nav>
      </header>
      <main className="card">
        {slug
          ? <Quiz key={`${lang}/${slug}`} lang={lang} slug={slug} onExit={SINGLE ? null : () => go(lang, null)} />
          : <Home lang={lang} onPick={(s) => go(lang, s)} />}
      </main>
    </div>
  )
}

function Home({ lang, onPick }) {
  const t = T[lang]
  return (
    <>
      <h1>{t.title}</h1>
      <p className="lead">{t.intro}</p>
      <h2>{t.themes}</h2>
      <ul className="themes">
        {data.themen.map((th) => (
          <li key={th.slug}>
            <button className="theme" onClick={() => onPick(th.slug)}>
              <span>{th.titel[lang]}</span>
              <small>{data.quiz[th.slug][lang].length} {t.questions}</small>
            </button>
          </li>
        ))}
      </ul>
    </>
  )
}

function Quiz({ lang, slug, onExit }) {
  const t = T[lang]
  const titel = data.themen.find((x) => x.slug === slug).titel[lang]
  const [round, setRound] = useState(() => newRound(data.quiz[slug][lang]))
  const [phase, setPhase] = useState('intro') // intro | quiz | result
  const [i, setI] = useState(0)
  const [picks, setPicks] = useState({})
  const [score, setScore] = useState(0)
  const n = round.length

  const start = () => { setPicks({}); setI(0); setPhase('quiz') }
  const retry = () => { setRound(newRound(data.quiz[slug][lang])); start() }
  const finish = async () => { setScore(await grade(round, picks)); setPhase('result') }

  if (phase === 'intro') return (
    <>
      <p className="tag">{t.title}</p>
      <h1>{titel}</h1>
      <p className="lead">{n} {t.questions}. {t.rule}</p>
      <div className="row">
        {onExit && <button className="btn ghost" onClick={onExit}>{t.toThemes}</button>}
        <button className="btn" onClick={start}>{t.start}</button>
      </div>
    </>
  )

  if (phase === 'quiz') {
    const f = round[i]
    return (
      <>
        <p className="tag">{titel}</p>
        <div className="progress" aria-hidden="true"><i style={{ width: `${((i + 1) / n) * 100}%` }} /></div>
        <p className="meta">{t.qOf(i + 1, n)}</p>
        <fieldset className="q">
          <legend>{f.q}</legend>
          <div className="opts">
            {f.opts.map((o) => (
              <label key={o.o} className={`opt${picks[f.id] === o.o ? ' sel' : ''}`}>
                <input type="radio" name={f.id} checked={picks[f.id] === o.o} onChange={() => setPicks({ ...picks, [f.id]: o.o })} />
                <span>{o.text}</span>
              </label>
            ))}
          </div>
        </fieldset>
        <div className="row">
          <button className="btn ghost" onClick={() => (i === 0 ? setPhase('intro') : setI(i - 1))}>{t.back}</button>
          {i < n - 1
            ? <button className="btn" disabled={picks[f.id] === undefined} onClick={() => setI(i + 1)}>{t.next}</button>
            : <button className="btn" disabled={picks[f.id] === undefined} onClick={finish}>{t.finish}</button>}
        </div>
      </>
    )
  }

  const passed = score === n
  return passed
    ? <Pass lang={lang} titel={titel} n={n} onExit={onExit} />
    : (
      <>
        <p className="tag">{titel}</p>
        <h1 className="fail">{t.failH}</h1>
        <p className="lead">{t.failTxt(score, n)}</p>
        <div className="row">
          {onExit && <button className="btn ghost" onClick={onExit}>{t.toThemes}</button>}
          <button className="btn" onClick={retry}>{t.retry}</button>
        </div>
      </>
    )
}

function Pass({ lang, titel, n, onExit }) {
  const t = T[lang]
  const [first, setFirst] = useState('')
  const [last, setLast] = useState('')
  const [name, setName] = useState(null)
  const [err, setErr] = useState(false)
  const [date] = useState(() => {
    const d = new Date()
    return `${d.toLocaleDateString(LOCALE[lang], { day: 'numeric', month: 'long', year: 'numeric' })}, ${d.toLocaleTimeString(LOCALE[lang], { hour: '2-digit', minute: '2-digit' })}`
  })
  const create = (e) => {
    e.preventDefault()
    if (!first.trim() || !last.trim()) { setErr(true); return }
    setErr(false); setName(`${first.trim()} ${last.trim()}`)
  }
  return (
    <>
      <div className="no-print">
        <p className="tag">{titel}</p>
        <h1 className="ok">{t.passH}</h1>
        <p className="lead">{t.passTxt(n)}</p>
        {!name && (
          <form onSubmit={create} className="certform">
            <p>{t.certIntro}</p>
            <input aria-label={t.first} placeholder={t.first} value={first} onChange={(e) => setFirst(e.target.value)} autoComplete="off" />
            <input aria-label={t.last} placeholder={t.last} value={last} onChange={(e) => setLast(e.target.value)} autoComplete="off" />
            {err && <p className="cerr" role="alert">{t.certErr}</p>}
            <button className="btn" type="submit">{t.certBtn}</button>
          </form>
        )}
      </div>
      {name && (
        <>
          <section className="cert" aria-label={t.cert}>
            <img className="certlogo" src={logoSki} alt="Swiss-Ski" />
            <p className="ctitle">{t.cert}</p>
            <p className="cname">{name}</p>
            <p>{t.certLine}</p>
            <p className="ctheme">{titel}</p>
            <p className="ccourse">{t.certCourse}</p>
            <p className="cscore">{t.certAll(n)}</p>
            <p className="cdate">{date}</p>
          </section>
          <p className="note no-print">{t.priv} {t.printHint}</p>
          <div className="row no-print">
            {onExit && <button className="btn ghost" onClick={onExit}>{t.toThemes}</button>}
            <button className="btn" onClick={() => window.print()}>{t.print}</button>
          </div>
        </>
      )}
    </>
  )
}
