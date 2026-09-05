import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import WeatherBackground from '../../components/WeatherBackground/WeatherBackground'
import RingChart from '../../components/RingChart/RingChart'
import { useAppState, DUMMY_ADVISORY, DUMMY_SCORE, DUMMY_DASHBOARD } from '../../hooks/useAppState'
import { useTheme } from '../../hooks/useTheme'
import { aqiBadgeColor } from '../../utils/weatherMap'
import styles from './AdvisoryPage.module.css'

function scoreColor(s) {
  if (s <= 2) return '#34D399'
  if (s <= 4) return '#FBBF24'
  if (s <= 6) return '#F97316'
  if (s <= 8) return '#EF4444'
  if (s <= 9) return '#C026D3'
  return '#7C2D12'
}
function scoreLabel(s) {
  if (s <= 2) return 'Low'
  if (s <= 4) return 'Moderate'
  if (s <= 6) return 'Elevated'
  if (s <= 8) return 'High'
  if (s <= 9) return 'Very High'
  return 'Hazardous'
}

function useTypewriter(text, speed = 20, startDelay = 500) {
  const [displayed, setDisplayed] = useState('')
  const [done, setDone] = useState(false)
  useEffect(() => {
    setDisplayed(''); setDone(false)
    let i = 0
    const t = setTimeout(() => {
      const iv = setInterval(() => {
        i++
        setDisplayed(text.slice(0, i))
        if (i >= text.length) { clearInterval(iv); setDone(true) }
      }, speed)
      return () => clearInterval(iv)
    }, startDelay)
    return () => clearTimeout(t)
  }, [text])
  return { displayed, done }
}

export default function AdvisoryPage() {
  const navigate = useNavigate()
  const { advisory, exposureResult, profile, dashboard, theme } = useAppState()
  useTheme(theme)

  const text   = advisory       || DUMMY_ADVISORY
  const result = exposureResult || DUMMY_SCORE
  const data   = dashboard      || DUMMY_DASHBOARD

  const score   = result.score
  const sColor  = scoreColor(score)
  const sLabel  = scoreLabel(score)
  const ringPct = Math.min(score / 10, 1)
  const win     = result.best_window || { start: 19, end: 21, label: '7 PM – 9 PM' }

  const { displayed, done } = useTypewriter(text)
  const [copied, setCopied] = useState(false)

  function handleCopy() {
    navigator.clipboard?.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2200)
  }

  return (
    <motion.div
      className="page"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.55 }}
    >
      <WeatherBackground
        bgImage={theme.bg}
        overlayType={theme.overlayType}
        overlayDark={Math.min(theme.overlay + 0.06, 0.36)}
        theme={theme}
      />

      {/* subtle perspective grid */}
      <div className={styles.grid} />

      {/* Header */}
      <header className="app-header">
        <button className="back-btn" onClick={() => navigate('/exposure')}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M19 12H5M12 5l-7 7 7 7"/>
          </svg>
        </button>

        <div className={styles.headerCenter}>
          <div className={styles.aiTag}>
            <svg viewBox="0 0 24 24" fill="currentColor" style={{ width:11, height:11 }}>
              <path d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456z"/>
            </svg>
            AI Advisory
          </div>
          <span style={{ fontSize:14, fontWeight:800, color:'#fff', textShadow:'0 1px 8px rgba(0,0,0,0.3)' }}>
            Personalised Air Report
          </span>
        </div>

        <button className={styles.copyBtn} onClick={handleCopy}>
          {copied ? '✓ Copied' : 'Copy'}
        </button>
      </header>

      <div className="content-area">

        {/* ── Left: advisory card ───────────────────────── */}
        <motion.div
          className={styles.leftCol}
          initial={{ opacity: 0, x: -32 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.22, duration: 0.85, ease: [0.16,1,0.3,1] }}
        >
          <div className={styles.advisoryCard}>
            {/* Rotating accent border */}
            <div className={styles.cardBorderRing} style={{ '--ac': sColor }} />

            <div className={styles.cardInner}>
              <div className={styles.sheen} />

              {/* Card header row */}
              <div className={styles.cardTop}>
                <div
                  className={styles.cardPulse}
                  style={{ background: sColor, boxShadow: `0 0 10px ${sColor}` }}
                />
                <span className="eyebrow" style={{ color:'rgba(255,255,255,0.75)' }}>
                  AI Advisory · Generated from your score
                </span>
                <span className="mono-tag" style={{ marginLeft:'auto' }}>
                  {new Date().toLocaleTimeString('en-IN', { hour:'2-digit', minute:'2-digit' })}
                </span>
              </div>

              {/* The advisory text — most important element on this screen */}
              <blockquote className={styles.advisoryText}>
                <span className={styles.openQuote}>"</span>
                {displayed}
                {!done && <span className={styles.cursor} />}
                {done  && <span className={styles.closeQuote}>"</span>}
              </blockquote>

              {/* Profile tags — appear after typewriter finishes */}
              <AnimatePresence>
                {done && (
                  <motion.div
                    className={styles.tagStrip}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4 }}
                  >
                    {[
                      profile?.age_group || 'Adult',
                      (profile?.health_condition || 'None').replace(/_/g,' '),
                      (profile?.occupation || 'Desk job').replace(/_/g,' '),
                      `AQI ${data.aqi}`,
                      `Score ${score.toFixed(1)}`,
                      theme.label,
                    ].map(tag => (
                      <span key={tag} className={styles.tag}>{tag}</span>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>

              <div className={styles.watermark}>VD</div>
            </div>
          </div>

          <p className={styles.disclaimer}>
            Advisory is AI-generated from deterministic exposure scores and real-time atmospheric data.
            Not a substitute for medical advice.
          </p>
        </motion.div>

        {/* ── Right sidebar ─────────────────────────────── */}
        <motion.div
          className={styles.rightCol}
          initial={{ opacity: 0, x: 32 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.35, duration: 0.85, ease: [0.16,1,0.3,1] }}
        >
          {/* Score ring */}
          <div className={`${styles.scorePanel} panel`}>
            <RingChart pct={ringPct} color={sColor} label={score.toFixed(1)} sublabel="/ 10" size={110} />
            <div className={styles.scorePanelText}>
              <div style={{ fontSize:'1.25rem', fontWeight:900, color: sColor,
                textShadow:'0 2px 12px rgba(0,0,0,0.25)', transition:'color .5s' }}>
                {sLabel}
              </div>
              <div style={{ fontSize:13.5, fontWeight:700, color:'#fff', marginTop:4,
                textShadow:'0 1px 6px rgba(0,0,0,0.25)' }}>
                {data.city_name}
              </div>
              <div style={{ fontSize:12, color:'rgba(255,255,255,0.62)', marginTop:2 }}>
                {(profile?.occupation || 'Desk job').replace(/_/g,' ')}
              </div>
            </div>
          </div>

          {/* 2×2 data grid */}
          <div className={styles.dataGrid}>
            {[
              { val: data.aqi,             sup:'',   label:'AQI',      color: aqiBadgeColor(data.aqi) },
              { val: `${data.temp}°`,       sup:'C',  label:'Temp',     color:'#FB923C' },
              { val: data.pm25,             sup:'μg', label:'PM 2.5',   color: aqiBadgeColor(data.aqi) },
              { val: `${data.humidity}%`,   sup:'',   label:'Humidity', color:'#38BDF8' },
            ].map(item => (
              <div
                key={item.label}
                className={`${styles.dataCell} panel`}
              >
                <div className={styles.dataCellVal}>
                  <span style={{ color: item.color }}>{item.val}</span>
                  {item.sup && <sup className={styles.dataCellSup}>{item.sup}</sup>}
                </div>
                <div className={styles.dataCellLabel}>{item.label}</div>
              </div>
            ))}
          </div>

          {/* Best window */}
          <div className={`${styles.windowCard} panel`}>
            <div className="eyebrow" style={{ marginBottom:6 }}>Best Window Today</div>
            <div style={{ fontSize:'1.4rem', fontWeight:900, color: sColor,
              textShadow:'0 2px 10px rgba(0,0,0,0.2)', transition:'color .5s' }}>
              {win.label}
            </div>
            <div className={styles.winBar}>
              {Array.from({ length: 24 }).map((_, i) => (
                <div
                  key={i}
                  className={styles.winBarBlock}
                  style={{
                    background: (i >= (win.start||19) && i < (win.end||21))
                      ? '#34D399'
                      : 'rgba(255,255,255,0.14)',
                  }}
                />
              ))}
            </div>
          </div>

          {/* What next */}
          <div className={`${styles.nextCard} panel`}>
            <div className="eyebrow" style={{ marginBottom:8 }}>What Next</div>
            {[
              { icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{width:15,height:15}}><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>, label:'Check another city', to:'/' },
              { icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{width:15,height:15}}><path d="M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>, label:'Try different profile', to:'/profile' },
            ].map(item => (
              <button key={item.label} className={styles.nextBtn} onClick={() => navigate(item.to)}>
                {item.icon}{item.label}
              </button>
            ))}
          </div>
        </motion.div>
      </div>
    </motion.div>
  )
}
