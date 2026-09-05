import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import WeatherBackground from '../../components/WeatherBackground/WeatherBackground'
import RingChart from '../../components/RingChart/RingChart'
import { useAppState, DUMMY_SCORE, DUMMY_DASHBOARD } from '../../hooks/useAppState'
import { useTheme } from '../../hooks/useTheme'
import { aqiBadgeColor } from '../../utils/weatherMap'
import { fetchAdvisory } from '../../hooks/useApi'
import styles from './ExposurePage.module.css'

function scoreColor(s) {
  if (s <= 2)  return '#34D399'
  if (s <= 4)  return '#FBBF24'
  if (s <= 6)  return '#F97316'
  if (s <= 8)  return '#EF4444'
  if (s <= 9)  return '#C026D3'
  return '#7C2D12'
}
function scoreLabel(s) {
  if (s <= 2)  return 'Low'
  if (s <= 4)  return 'Moderate'
  if (s <= 6)  return 'Elevated'
  if (s <= 8)  return 'High'
  if (s <= 9)  return 'Very High'
  return 'Hazardous'
}

export default function ExposurePage() {
  const navigate = useNavigate()
  const { exposureResult, profile, dashboard, setAdvisory, theme } = useAppState()
  useTheme(theme)

  const [genLoading, setGenLoading] = useState(false)
  const result = exposureResult || DUMMY_SCORE
  const data   = dashboard || DUMMY_DASHBOARD

  const score   = result.score
  const sColor  = scoreColor(score)
  const sLabel  = scoreLabel(score)
  const ringPct = Math.min(score / 10, 1)
  const win     = result.best_window || { start: 19, end: 21, label: '7 PM – 9 PM' }
  const maxAqi  = Math.max(...data.hourly_aqi)
  const minAqi  = Math.min(...data.hourly_aqi)

  async function handleAdvisory() {
    setGenLoading(true)
    try {
      const text = await fetchAdvisory({
        conditions: { aqi: data.aqi, pm25: data.pm25, temp: data.temp },
        profile, score, label: sLabel, window: win.label,
      })
      setAdvisory(text)
      navigate('/advisory')
    } finally { setGenLoading(false) }
  }

  return (
    <motion.div
      className="page"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, x: -24 }}
      transition={{ duration: 0.45 }}
    >
      <WeatherBackground
        bgImage={theme.bg}
        overlayType={theme.overlayType}
        overlayDark={Math.min(theme.overlay + 0.05, 0.35)}
        theme={theme}
      />

      {/* Header */}
      <header className="app-header">
        <button className="back-btn" onClick={() => navigate('/profile')}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M19 12H5M12 5l-7 7 7 7"/>
          </svg>
        </button>
        <span style={{ fontSize:15, fontWeight:800, color:'#fff', textShadow:'0 1px 8px rgba(0,0,0,0.3)' }}>
          Exposure Score
        </span>
        <div
          className={styles.headerBadge}
          style={{ color: sColor, borderColor: `${sColor}66` }}
        >
          {sLabel}
        </div>
      </header>

      <div className="content-area">

        {/* ── Left ─────────────────────────────────────────── */}
        <motion.div
          className={styles.leftCol}
          initial={{ opacity: 0, x: -32 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.18, duration: 0.8, ease: [0.16,1,0.3,1] }}
        >
          <div className="eyebrow">Personalised Exposure Risk</div>

          {/* Score ring + meta */}
          <div className={styles.scoreHero}>
            <RingChart pct={ringPct} color={sColor} label={score.toFixed(1)} sublabel="/ 10" size={180} />
            <div className={styles.scoreMeta}>
              <div className={styles.scoreLabelBig} style={{ color: sColor }}>{sLabel}</div>
              <div className={styles.scoreSub}>
                {profile?.age_group || 'Adult'} ·{' '}
                {(profile?.health_condition || 'None').replace(/_/g,' ')} ·{' '}
                {(profile?.occupation || 'Desk job').replace(/_/g,' ')}
              </div>
              <div className={styles.scoreDivider} />
              <div className={styles.scoreContext}>
                AQI {data.aqi} · PM2.5 {data.pm25} μg/m³ · {data.temp}°C
              </div>
            </div>
          </div>

          {/* Score bar */}
          <div className={styles.scoreBarWrap}>
            <div className={styles.scoreBarTrack}>
              <motion.div
                className={styles.scoreBarFill}
                style={{ background: `linear-gradient(90deg,${sColor}66,${sColor})` }}
                initial={{ width: 0 }}
                animate={{ width: `${(score/10)*100}%` }}
                transition={{ duration: 1.4, delay: 0.5, ease: [0.16,1,0.3,1] }}
              />
              <motion.div
                className={styles.scoreBarHead}
                style={{ background: sColor }}
                initial={{ left: 0 }}
                animate={{ left: `calc(${(score/10)*100}% - 5px)` }}
                transition={{ duration: 1.4, delay: 0.5, ease: [0.16,1,0.3,1] }}
              />
            </div>
            <div className={styles.scoreBarTicks}>
              {['Low','Mod','Elev','High','V.High','Haz'].map(l => (
                <span key={l}>{l}</span>
              ))}
            </div>
          </div>

          {/* Explanation */}
          <div className={`${styles.explainCard} panel`}>
            <div className="eyebrow" style={{ marginBottom: 9 }}>How this score is calculated</div>
            <p style={{ fontSize:14, lineHeight:1.7, color:'rgba(255,255,255,0.82)', fontWeight:500 }}>
              Base risk from AQI and PM2.5 is multiplied by profile modifiers — health condition,
              occupation, and age sensitivity. Score is 0–10, deterministic and fully explainable.
            </p>
          </div>

          {/* Same-air comparison */}
          <div className={`${styles.compCard} panel`}>
            <div className="eyebrow" style={{ marginBottom: 13 }}>Same Air — Different Risk</div>
            <div className={styles.compRow}>
              <div>
                <div className={styles.compScore} style={{ color:'#FBBF24' }}>4.2</div>
                <div className={styles.compDesc}>Desk job · None · 18–30</div>
              </div>
              <div className={styles.compVs}>vs</div>
              <div>
                <div className={styles.compScore} style={{ color:'#C026D3' }}>9.6</div>
                <div className={styles.compDesc}>Outdoor worker · Asthma · 18–30</div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* ── Right ────────────────────────────────────────── */}
        <motion.div
          className={styles.rightCol}
          initial={{ opacity: 0, x: 32 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.30, duration: 0.8, ease: [0.16,1,0.3,1] }}
        >
          {/* Best window */}
          <div className={styles.windowBanner} style={{ borderColor:`${sColor}55` }}>
            <div className={styles.windowIcon} style={{ background:`${sColor}25` }}>
              <svg viewBox="0 0 24 24" fill="none" stroke={sColor} strokeWidth="1.8">
                <circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>
              </svg>
            </div>
            <div>
              <div className="eyebrow" style={{ marginBottom:4 }}>Lowest Exposure Window</div>
              <div className={styles.windowTime} style={{ color: sColor }}>{win.label}</div>
              <div className={styles.windowSub}>Best time to go outside today</div>
            </div>
          </div>

          {/* Strip */}
          <div className={`${styles.stripCard} panel`}>
            <div className="eyebrow" style={{ marginBottom:13 }}>24H Hourly Risk Profile</div>
            <div className={styles.strip}>
              {data.hourly_aqi.map((v, i) => {
                const norm     = (v - minAqi) / (maxAqi - minAqi || 1)
                const h        = 10 + norm * 68
                const isWindow = i >= win.start && i < win.end
                const isNow    = i === new Date().getHours()
                return (
                  <motion.div
                    key={i}
                    className={styles.stripBlock}
                    style={{
                      height:    `${h}%`,
                      background: isWindow ? '#34D399' : isNow ? sColor : `${aqiBadgeColor(v)}88`,
                      boxShadow:  (isWindow||isNow) ? `0 0 8px ${isWindow?'#34D399':sColor}` : 'none',
                      originY: 1,
                    }}
                    initial={{ scaleY: 0 }}
                    animate={{ scaleY: 1 }}
                    transition={{ delay: 0.35 + i * 0.012, duration: 0.36 }}
                    title={`${i}:00 — AQI ${v}`}
                  />
                )
              })}
            </div>
            <div className={styles.stripXAxis}>
              {[[0,'12am'],[6,'6am'],[12,'12pm'],[18,'6pm'],[23,'11pm']].map(([h,l]) => (
                <span key={h} style={{ left:`${(h/23)*100}%` }}>{l}</span>
              ))}
            </div>
            <div className={styles.stripLegend}>
              <div className={styles.legendItem}>
                <div className={styles.legendDot} style={{ background:'#34D399' }}/> Best window
              </div>
              <div className={styles.legendItem}>
                <div className={styles.legendDot} style={{ background: sColor }}/> Current hour
              </div>
            </div>
          </div>

          {/* Action chips */}
          <div className={styles.actions}>
            {score < 4 ? (
              <>
                <div className={styles.chip}><span>🟢</span> Normal outdoor activity is safe</div>
                <div className={styles.chip}><span>🏃</span> Exercise is low risk today</div>
              </>
            ) : score < 7 ? (
              <>
                <div className={styles.chip}><span>🟡</span> Limit prolonged outdoor exertion</div>
                <div className={styles.chip}><span>😷</span> Mask recommended if outdoors &gt; 1h</div>
              </>
            ) : (
              <>
                <div className={styles.chip}><span>🔴</span> Stay indoors during peak hours</div>
                <div className={styles.chip}><span>💊</span> Keep reliever medication on hand</div>
                <div className={styles.chip}><span>🌬️</span> Use air purifier if available</div>
              </>
            )}
          </div>

          {/* Advisory CTA */}
          <motion.button
            className={styles.advisoryBtn}
            onClick={handleAdvisory}
            disabled={genLoading}
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.85 }}
          >
            <div className={styles.btnGlow} style={{ background: sColor }} />
            {genLoading ? (
              <><span className="spinner" /> Generating AI advisory…</>
            ) : (
              <>
                <svg viewBox="0 0 24 24" fill="currentColor" style={{ width:17,height:17 }}>
                  <path d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456z"/>
                </svg>
                Generate AI Advisory →
              </>
            )}
          </motion.button>
        </motion.div>
      </div>
    </motion.div>
  )
}
