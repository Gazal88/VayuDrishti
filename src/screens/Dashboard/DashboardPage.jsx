import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import WeatherBackground from '../../components/WeatherBackground/WeatherBackground'
import ReadoutCard       from '../../components/ReadoutCard/ReadoutCard'
import { useAppState, DUMMY_DASHBOARD } from '../../hooks/useAppState'
import { useTheme } from '../../hooks/useTheme'
import { aqiBadgeColor, aqiBadgeLabel } from '../../utils/weatherMap'
import styles from './DashboardPage.module.css'

function normalise(arr) {
  const mn = Math.min(...arr), mx = Math.max(...arr)
  return arr.map(v => (v - mn) / (mx - mn || 1))
}

const STAGGER = { hidden: {}, show: { transition: { staggerChildren: 0.08 } } }
const CARD_V  = {
  hidden: { opacity: 0, y: 20, scale: 0.94 },
  show:   { opacity: 1, y: 0,  scale: 1, transition: { duration: 0.6, ease: [0.16,1,0.3,1] } }
}

export default function DashboardPage() {
  const navigate = useNavigate()
  const { dashboard, setDashboard, city, theme } = useAppState()
  useTheme(theme)

  const data = dashboard || DUMMY_DASHBOARD
  useEffect(() => { if (!dashboard) setDashboard(DUMMY_DASHBOARD) }, [])

  const aqiColor = aqiBadgeColor(data.aqi)
  const aqiLabel = aqiBadgeLabel(data.aqi)
  const sparkPm  = normalise(data.hourly_aqi.map(v => v * 0.56))
  const sparkTemp = Array.from({ length: 24 }, (_, i) => 0.3 + 0.65 * Math.sin(i / 4))
  const sparkHum  = Array.from({ length: 24 }, (_, i) => 0.4 + 0.28 * Math.cos(i / 5 + 1))
  const sparkWind = Array.from({ length: 24 }, () => Math.random())
  const now       = new Date()

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
        overlayDark={theme.overlay}
        theme={theme}
      />

      {/* Header */}
      <header className="app-header">
        <button className="back-btn" onClick={() => navigate('/')}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M19 12H5M12 5l-7 7 7 7"/>
          </svg>
        </button>

        <div className={styles.cityRow}>
          <div className={styles.livePulse}
            style={{ background: aqiColor, boxShadow: `0 0 10px ${aqiColor}` }} />
          <span className={styles.cityName}>{city || data.city_name}</span>
          <span className="mono-tag" style={{ marginLeft: 6 }}>
            Live · {now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>

        <button className={styles.profileBtn} onClick={() => navigate('/profile')}>
          Check my risk →
        </button>
      </header>

      {/* Content */}
      <div className="content-area">

        {/* ── Left ─────────────────────────────────────────── */}
        <motion.div
          className={styles.leftCol}
          initial={{ opacity: 0, x: -32 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.18, duration: 0.8, ease: [0.16,1,0.3,1] }}
        >
          <div className="eyebrow">Current Air Quality</div>

          {/* AQI number + meta */}
          <div className={styles.aqiHero}>
            <motion.span
              className={styles.aqiNum}
              style={{ color: aqiColor }}
              initial={{ opacity: 0, scale: 0.7 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.32, duration: 1.0, ease: [0.34,1.56,0.64,1] }}
            >
              {data.aqi}
            </motion.span>

            <div className={styles.aqiMeta}>
              <div className={styles.aqiLabel} style={{ color: aqiColor }}>{aqiLabel}</div>
              <div className={styles.aqiScale}>US AQI Scale</div>

              {/* Colour band */}
              <div className={styles.aqiBand}>
                {[
                  { top: 50,  color:'#34D399' },
                  { top: 100, color:'#FBBF24' },
                  { top: 150, color:'#F97316' },
                  { top: 200, color:'#EF4444' },
                  { top: 300, color:'#C026D3' },
                ].map(({ top, color }, i, arr) => {
                  const prev = arr[i-1]?.top ?? 0
                  const active = data.aqi <= top && data.aqi > prev
                  return (
                    <div key={top} className={styles.aqiBandSeg} style={{ background: color }}>
                      {active && <div className={styles.aqiBandPin} />}
                    </div>
                  )
                })}
              </div>

              <div
                className={styles.weatherBadge}
                style={{ color: theme.accent, borderColor: `${theme.accent}55` }}
              >
                {theme.label}
              </div>
            </div>
          </div>

          <p className={styles.aqiDesc}>
            Air is <strong style={{ color: aqiColor }}>{aqiLabel.toLowerCase()}</strong> in{' '}
            {city || data.city_name} right now.{' '}
            {data.aqi > 150
              ? 'Sensitive groups should limit outdoor time during peak hours.'
              : 'Most people can continue normal outdoor activities today.'}
          </p>

          {/* 24h trend */}
          <div className={`${styles.trendCard} panel`}>
            <div className="eyebrow" style={{ marginBottom: 14 }}>24-Hour AQI Forecast</div>
            <div className={styles.trendBars}>
              {data.hourly_aqi.map((v, i) => {
                const h     = (v / 250) * 100
                const isNow = i === now.getHours()
                return (
                  <div key={i} className={styles.trendBar} title={`${i}:00 — AQI ${v}`}>
                    <motion.div
                      className={styles.trendFill}
                      style={{
                        background: isNow ? aqiColor : `${aqiBadgeColor(v)}99`,
                        boxShadow:  isNow ? `0 0 8px ${aqiColor}` : 'none',
                      }}
                      initial={{ height: 0 }}
                      animate={{ height: `${Math.max(h, 3)}%` }}
                      transition={{ delay: 0.4 + i * 0.012, duration: 0.5, ease: [0.16,1,0.3,1] }}
                    />
                    {i % 6 === 0 && <div className={styles.trendTick}>{i}h</div>}
                  </div>
                )
              })}
            </div>
          </div>
        </motion.div>

        {/* ── Right: cards ─────────────────────────────────── */}
        <motion.div
          className={styles.cardsCol}
          variants={STAGGER}
          initial="hidden"
          animate="show"
        >
          {[
            { value: data.temp,       unit:'°C',    label:'Temperature', sublabel: data.temp > 35 ? 'Extreme heat':'Elevated',  color:'#FB923C', spark: sparkTemp, delay:0.28 },
            { value: data.pm25,       unit:'μg/m³', label:'PM 2.5',      sublabel:'WHO limit: 15',                               color: aqiColor, spark: sparkPm,   delay:0.36 },
            { value: data.humidity,   unit:'%',     label:'Humidity',    sublabel:'Relative',                                    color:'#38BDF8', spark: sparkHum,  delay:0.44 },
            { value: data.wind_speed, unit:'km/h',  label:'Wind Speed',  sublabel:'Surface',                                     color:'#A78BFA', spark: sparkWind, delay:0.52 },
          ].map(card => (
            <motion.div key={card.label} variants={CARD_V}>
              <ReadoutCard {...card} />
            </motion.div>
          ))}

          {/* Coordinates — same style as readout cards, spans full width */}
          <motion.div variants={CARD_V} style={{ gridColumn: '1 / -1' }}>
            <div className={styles.coordCard}>
              <div className={styles.coordStripe} />
              <div className={styles.coordPulse}>
                <span className={styles.coordDot} />
              </div>
              <div className={styles.coordBody}>
                <div className={styles.coordValue}>
                  {data.lat?.toFixed(4)}° N &nbsp;·&nbsp; {data.lon?.toFixed(4)}° E
                </div>
                <div className={styles.coordLabel}>
                  📍 {city || data.city_name} &nbsp;·&nbsp; {data.timezone || 'Asia/Kolkata'}
                </div>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </div>

      {/* Footer CTA */}
      <motion.div
        className="app-footer"
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.85, duration: 0.6 }}
      >
        <p style={{ fontSize:14, color:'rgba(255,255,255,0.80)', textShadow:'0 1px 6px rgba(0,0,0,0.3)' }}>
          Real-time data for{' '}
          <strong style={{ color:'#fff' }}>{city || data.city_name}</strong>.
          Now tell us about <strong style={{ color:'#fff' }}>you</strong>{' '}
          for a personalised risk score.
        </p>
        <motion.button
          className="btn-primary"
          style={{ background: aqiColor }}
          onClick={() => navigate('/profile')}
          whileHover={{ scale: 1.04, y: -2 }}
          whileTap={{ scale: 0.97 }}
        >
          Calculate my exposure →
        </motion.button>
      </motion.div>
    </motion.div>
  )
}
