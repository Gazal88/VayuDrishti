import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import WeatherBackground from '../../components/WeatherBackground/WeatherBackground'
import { useAppState } from '../../hooks/useAppState'
import { useTheme } from '../../hooks/useTheme'
import { fetchExposureScore } from '../../hooks/useApi'
import styles from './ProfilePage.module.css'

const AGE_GROUPS = [
  { value: '18-30', label: '18 – 30', sub: 'Young adult',  icon: '🧑' },
  { value: '31-50', label: '31 – 50', sub: 'Adult',        icon: '👤' },
  { value: '51-65', label: '51 – 65', sub: 'Middle-aged',  icon: '🧔' },
  { value: '65+',   label: '65+',     sub: 'Senior',       icon: '🧓' },
]

// Multi-select — user can pick more than one condition
// Backend only accepts one; we send the highest-risk one
const CONDITIONS = [
  { value: 'none',            label: 'None',            icon: '✓',  risk: 0 },
  { value: 'asthma',          label: 'Asthma',          icon: '🫁', risk: 5 },
  { value: 'heart_condition', label: 'Heart Condition',  icon: '❤️', risk: 5 },
  { value: 'pregnant',        label: 'Pregnancy',        icon: '🤰', risk: 4 },
  { value: 'other',           label: 'Other / Chronic',  icon: '💊', risk: 2 },
]

const OCCUPATIONS = [
  { value: 'desk_job',          label: 'Desk Job',          sub: 'Mostly indoors, low exposure'      },
  { value: 'student',           label: 'Student',           sub: 'Campus / mostly indoors'           },
  { value: 'outdoor_worker',    label: 'Outdoor Worker',    sub: 'Sustained outdoor exposure'        },
  { value: 'elderly_caregiver', label: 'Elderly Caregiver', sub: 'Mixed indoor/outdoor'              },
  { value: 'commuter',          label: 'Daily Commuter',    sub: 'Regular transit exposure'          },
  { value: 'athlete',           label: 'Athlete / Fitness', sub: 'High exertion, outdoor activity'  },
  { value: 'construction',      label: 'Construction',      sub: 'Heavy outdoor physical work'       },
  { value: 'homemaker',         label: 'Homemaker',         sub: 'Mostly indoors'                    },
]

// Map extra occupation values to backend-accepted ones
const OCC_BACKEND_MAP = {
  commuter:     'outdoor_worker',
  athlete:      'outdoor_worker',
  construction: 'outdoor_worker',
  homemaker:    'desk_job',
}

export default function ProfilePage() {
  const navigate = useNavigate()
  const { setProfile, setExposureResult, dashboard, city, theme } = useAppState()
  useTheme(theme)

  const [age,         setAge]         = useState('')
  const [conditions,  setConditions]  = useState([])   // multi-select array
  const [occupation,  setOccupation]  = useState('')
  const [loading,     setLoading]     = useState(false)
  const [step,        setStep]        = useState(0)

  // Toggle a condition — selecting 'none' clears everything else
  function toggleCondition(val) {
    if (val === 'none') {
      setConditions(['none'])
      setStep(2)
      return
    }
    setConditions(prev => {
      const without = prev.filter(c => c !== 'none')
      if (without.includes(val)) {
        const next = without.filter(c => c !== val)
        return next.length === 0 ? ['none'] : next
      }
      return [...without, val]
    })
  }

  // Pick the highest-risk condition to send to backend
  function resolveCondition() {
    if (!conditions.length || conditions[0] === 'none') return 'none'
    return conditions.reduce((best, c) => {
      const cRisk = CONDITIONS.find(x => x.value === c)?.risk ?? 0
      const bRisk = CONDITIONS.find(x => x.value === best)?.risk ?? 0
      return cRisk > bRisk ? c : best
    }, conditions[0])
  }

  // Map occupation to backend enum
  function resolveOccupation() {
    return OCC_BACKEND_MAP[occupation] ?? occupation
  }

  const conditionDone = conditions.length > 0

  async function handleSubmit() {
    const resolvedCondition  = resolveCondition()
    const resolvedOccupation = resolveOccupation()

    setProfile({
      age_group:        age,
      health_condition: resolvedCondition,
      occupation:       resolvedOccupation,
      // keep display-friendly originals for UI
      _conditions_display: conditions,
      _occupation_display: occupation,
    })
    setLoading(true)
    try {
      const result = await fetchExposureScore({
        age_group:        age,
        health_condition: resolvedCondition,
        occupation:       resolvedOccupation,
        city:  city ?? null,
        aqi:   dashboard?.aqi  ?? 160,
        pm25:  dashboard?.pm25 ?? 89,
        temp:  dashboard?.temp ?? 38,
      })
      setExposureResult(result)
      navigate('/exposure')
    } finally { setLoading(false) }
  }

  return (
    <motion.div
      className="page"
      style={{ overflow: 'hidden' }}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, x: -24 }}
      transition={{ duration: 0.45 }}
    >
      <WeatherBackground
        bgImage={theme.bg}
        overlayType={theme.overlayType}
        overlayDark={Math.min(theme.overlay + 0.06, 0.42)}
        theme={theme}
      />

      {/* Header */}
      <header className="app-header" style={{ flexShrink: 0 }}>
        <button className="back-btn" onClick={() => navigate('/dashboard')}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M19 12H5M12 5l-7 7 7 7"/>
          </svg>
        </button>
        <span style={{ fontSize:15, fontWeight:600, color:'#fff', textShadow:'0 1px 8px rgba(0,0,0,0.3)' }}>
          Your Health Profile
        </span>
        <div className={styles.stepDots}>
          {[0,1,2].map(i => (
            <div
              key={i}
              className={styles.stepDot}
              style={{ background: i <= step ? 'var(--accent)' : 'rgba(255,255,255,0.22)' }}
            />
          ))}
        </div>
      </header>

      {/* Scrollable form — this div must scroll, not the page */}
      <div className={styles.scroll}>
        <motion.div
          className={styles.formWrap}
          initial={{ opacity: 0, y: 28 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15, duration: 0.7, ease: [0.16,1,0.3,1] }}
        >
          <div className={styles.formHeader}>
            <h2 className={styles.formTitle}>Tell us about yourself</h2>
            <p className={styles.formSubtitle}>
              The same AQI hits different people differently.
              Your score is built for your body — not a generic average.
            </p>
          </div>

          {/* 01 Age */}
          <Accordion title="01 — Age Group" done={!!age}
            open={step === 0} onOpen={() => setStep(0)}>
            <div className={styles.optionGrid}>
              {AGE_GROUPS.map(opt => (
                <OptionCard key={opt.value} {...opt}
                  selected={age === opt.value}
                  onClick={() => { setAge(opt.value); setStep(1) }} />
              ))}
            </div>
          </Accordion>

          {/* 02 Health — multi-select */}
          <Accordion
            title="02 — Health Condition"
            done={conditionDone}
            open={step === 1}
            onOpen={() => setStep(1)}
            hint="Select all that apply"
          >
            <div className={styles.optionGrid}>
              {CONDITIONS.map(opt => (
                <OptionCard key={opt.value} {...opt}
                  selected={conditions.includes(opt.value)}
                  multi
                  onClick={() => toggleCondition(opt.value)} />
              ))}
            </div>
            {conditionDone && conditions[0] !== 'none' && (
              <motion.div
                className={styles.multiHint}
                initial={{ opacity:0 }} animate={{ opacity:1 }}
              >
                Selected: {conditions.map(c => CONDITIONS.find(x=>x.value===c)?.label).join(', ')}
                &nbsp;·&nbsp;
                <button className={styles.nextBtn} onClick={() => setStep(2)}>
                  Next →
                </button>
              </motion.div>
            )}
          </Accordion>

          {/* 03 Occupation */}
          <Accordion title="03 — Occupation / Exposure Type" done={!!occupation}
            open={step === 2} onOpen={() => setStep(2)}>
            <div className={styles.optionList}>
              {OCCUPATIONS.map(opt => (
                <OccRow key={opt.value} {...opt}
                  selected={occupation === opt.value}
                  onClick={() => setOccupation(opt.value)} />
              ))}
            </div>
          </Accordion>

          {/* Submit */}
          <AnimatePresence>
            {age && conditionDone && occupation && (
              <motion.div
                className={styles.submitWrap}
                initial={{ opacity: 0, y: 14 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.38 }}
              >
                <p className={styles.profileSummary}>
                  {AGE_GROUPS.find(a=>a.value===age)?.label}
                  <span className={styles.dot}> · </span>
                  {conditions.map(c => CONDITIONS.find(x=>x.value===c)?.label).join(' + ')}
                  <span className={styles.dot}> · </span>
                  {OCCUPATIONS.find(o=>o.value===occupation)?.label}
                </p>
                <motion.button
                  className={styles.submitBtn}
                  onClick={handleSubmit}
                  disabled={loading}
                  whileHover={{ scale: 1.02, y: -2 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {loading
                    ? <><span className="spinner" /> Calculating score…</>
                    : 'Calculate my exposure score →'
                  }
                </motion.button>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </motion.div>
  )
}

/* ── Sub-components ──────────────────────────────────────────────────────── */
function Accordion({ title, done, open, onOpen, children, hint }) {
  return (
    <motion.div
      className={`${styles.accordion} ${open ? styles.accordionOpen : ''} ${done ? styles.accordionDone : ''}`}
      layout="position"
    >
      <div className={styles.accHeader} onClick={onOpen}>
        <span className={styles.accTitle}>
          {done && <span className={styles.check}>✓</span>}
          {title}
          {hint && !done && <span className={styles.accHint}>{hint}</span>}
        </span>
        <svg
          className={`${styles.chevron} ${open ? styles.chevronOpen : ''}`}
          viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
        ><path d="M6 9l6 6 6-6"/></svg>
      </div>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            className={styles.accBody}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.32, ease: [0.16,1,0.3,1] }}
            style={{ overflow: 'hidden' }}
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

function OptionCard({ icon, label, sub, selected, onClick, multi }) {
  return (
    <motion.button
      className={`${styles.optCard} ${selected ? styles.optSelected : ''}`}
      onClick={onClick}
      whileHover={{ y: -3, scale: 1.03 }}
      whileTap={{ scale: 0.96 }}
    >
      {multi && (
        <div className={`${styles.checkbox} ${selected ? styles.checkboxChecked : ''}`}>
          {selected && '✓'}
        </div>
      )}
      <span className={styles.optIcon}>{icon}</span>
      <span className={styles.optLabel}>{label}</span>
      {sub && <span className={styles.optSub}>{sub}</span>}
    </motion.button>
  )
}

function OccRow({ label, sub, selected, onClick }) {
  return (
    <motion.button
      className={`${styles.occRow} ${selected ? styles.optSelected : ''}`}
      onClick={onClick}
      whileHover={{ x: 4 }}
      whileTap={{ scale: 0.99 }}
    >
      <div style={{ textAlign: 'left' }}>
        <div className={styles.occLabel}>{label}</div>
        <div className={styles.occSub}>{sub}</div>
      </div>
      <div className={`${styles.occCheck} ${selected ? styles.occCheckActive : ''}`}>
        {selected ? '✓' : '›'}
      </div>
    </motion.button>
  )
}
