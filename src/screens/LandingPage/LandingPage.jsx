import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import WeatherBackground from '../../components/WeatherBackground/WeatherBackground'
import { useAppState } from '../../hooks/useAppState'
import { useTheme } from '../../hooks/useTheme'
import { fetchDashboard } from '../../hooks/useApi'
import { resolveTheme } from '../../utils/weatherMap'
import styles from './LandingPage.module.css'

const CITIES = ['New Delhi','Mumbai','Bengaluru','Hyderabad','Chennai','Kolkata','Pune','Ahmedabad']

export default function LandingPage() {
  const navigate = useNavigate()
  const { setCity, setDashboard, setLoading } = useAppState()
  const theme = resolveTheme(0, 0)
  useTheme(theme)

  const [query,     setQuery]     = useState('')
  const [focused,   setFocused]   = useState(false)
  const [searching, setSearching] = useState(false)
  const [error,     setError]     = useState('')
  const inputRef = useRef(null)

  const filtered = CITIES.filter(s =>
    query.length > 0 && s.toLowerCase().startsWith(query.toLowerCase())
  )

  async function handleSearch(city) {
    if (!city.trim()) return
    setSearching(true); setError('')
    try {
      setLoading(true)
      const data = await fetchDashboard(city)
      setCity(city); setDashboard(data)
      navigate('/dashboard')
    } catch (err) {
      const detail = err?.response?.data?.detail
      setError(detail || 'Could not find that city. Try another.')
    } finally {
      setSearching(false); setLoading(false)
    }
  }

  return (
    <motion.div
      className={`page ${styles.page}`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <WeatherBackground
        bgImage={theme.bg}
        overlayType={theme.overlayType}
        overlayDark={0.42}
        theme={theme}
      />

      {/* ── Header ─────────────────────────────────────── */}
      <header className={styles.header}>
        <div className={styles.logo}>
          <div className={styles.logoDot} />
          VayuDrishti
        </div>
        <span className={styles.headerTag}>Air Intelligence · India</span>
      </header>

      {/* ── Centred hero ──────────────────────────────── */}
      <div className={styles.hero}>

        {/* Live pill */}
        <motion.div
          className={styles.livePill}
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.6 }}
        >
          <span className={styles.liveDot} />
          Live · Real-time AQI across India
        </motion.div>

        {/* Headline */}
        <motion.h1
          className={styles.headline}
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.42, duration: 0.9, ease: [0.16,1,0.3,1] }}
        >
          Know the air<br />
          you're breathing<br />
          <span className={styles.accent}>right now.</span>
        </motion.h1>

        {/* Subline */}
        <motion.p
          className={styles.subline}
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.58, duration: 0.7 }}
        >
          Personalised exposure scores for your age, health,
          and occupation — not a generic AQI alert.
        </motion.p>

        {/* Search */}
        <motion.div
          className={styles.searchWrap}
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.70, duration: 0.7 }}
        >
          <div className={`${styles.searchBox} ${focused ? styles.focused : ''}`}>
            <svg className={styles.searchIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
            </svg>
            <input
              ref={inputRef}
              className={styles.searchInput}
              type="text"
              placeholder="Delhi, Mumbai, Bengaluru, Hyderabad…"
              value={query}
              onChange={e => setQuery(e.target.value)}
              onFocus={() => setFocused(true)}
              onBlur={() => setTimeout(() => setFocused(false), 160)}
              onKeyDown={e => e.key === 'Enter' && handleSearch(query)}
              autoComplete="off"
            />
            <button
              className={styles.searchBtn}
              onClick={() => handleSearch(query)}
              disabled={searching}
            >
              {searching ? <span className="spinner" style={{borderTopColor:'#1a1a1a'}} /> : 'Check →'}
            </button>
          </div>

          <AnimatePresence>
            {focused && filtered.length > 0 && (
              <motion.ul
                className={styles.dropdown}
                initial={{ opacity: 0, y: -6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -4 }}
                transition={{ duration: 0.14 }}
              >
                {filtered.map((s, i) => (
                  <motion.li
                    key={s}
                    className={styles.dropdownItem}
                    initial={{ opacity: 0, x: -6 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.04 }}
                    onMouseDown={() => { setQuery(s); handleSearch(s) }}
                  >
                    <svg viewBox="0 0 24 24" fill="currentColor" style={{ width:11, height:11, opacity:0.5, flexShrink:0 }}>
                      <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5S10.62 6.5 12 6.5s2.5 1.12 2.5 2.5S13.38 11.5 12 11.5z"/>
                    </svg>
                    {s}
                  </motion.li>
                ))}
              </motion.ul>
            )}
          </AnimatePresence>

          {error && (
            <motion.p className={styles.error} initial={{ opacity:0 }} animate={{ opacity:1 }}>
              {error}
            </motion.p>
          )}
        </motion.div>

        {/* City chips */}
        <motion.div
          className={styles.chips}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.86 }}
        >
          <span className={styles.chipsLabel}>Popular:</span>
          {CITIES.slice(0, 6).map((city, i) => (
            <motion.button
              key={city}
              className={styles.chip}
              onClick={() => handleSearch(city)}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.90 + i * 0.05 }}
              whileHover={{ y: -2 }}
              whileTap={{ scale: 0.97 }}
            >
              {city}
            </motion.button>
          ))}
        </motion.div>

      </div>
    </motion.div>
  )
}
