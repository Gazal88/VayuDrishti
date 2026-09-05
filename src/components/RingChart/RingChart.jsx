import { useEffect, useRef } from 'react'
import { motion, useMotionValue, useTransform, animate } from 'framer-motion'
import styles from './RingChart.module.css'

const R = 54
const CIRC = 2 * Math.PI * R
const SIZE = 130

export default function RingChart({ pct = 0, color = '#EF4444', label, sublabel, size = SIZE }) {
  const progress = useMotionValue(0)
  const dashOffset = useTransform(progress, p => CIRC * (1 - p))

  useEffect(() => {
    const ctrl = animate(progress, pct, { duration: 1.4, ease: [0.16, 1, 0.3, 1] })
    return ctrl.stop
  }, [pct])

  const scale = size / SIZE

  return (
    <div className={styles.wrap} style={{ width: size, height: size }}>
      <svg
        width={SIZE}
        height={SIZE}
        viewBox={`0 0 ${SIZE} ${SIZE}`}
        style={{ transform: `rotate(-90deg) scale(${scale})`, transformOrigin: 'center' }}
      >
        <defs>
          <filter id="ring-glow">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
          <linearGradient id="ring-grad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor={color} stopOpacity="0.6" />
            <stop offset="100%" stopColor={color} />
          </linearGradient>
        </defs>

        {/* Track */}
        <circle
          cx={SIZE / 2} cy={SIZE / 2} r={R}
          fill="none"
          stroke="rgba(255,255,255,0.05)"
          strokeWidth="6"
        />
        {/* Tick marks */}
        {Array.from({ length: 24 }).map((_, i) => {
          const angle = (i / 24) * 2 * Math.PI - Math.PI / 2
          const x1 = SIZE/2 + (R - 10) * Math.cos(angle)
          const y1 = SIZE/2 + (R - 10) * Math.sin(angle)
          const x2 = SIZE/2 + (R - 7)  * Math.cos(angle)
          const y2 = SIZE/2 + (R - 7)  * Math.sin(angle)
          return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke="rgba(255,255,255,0.08)" strokeWidth="1" />
        })}

        {/* Fill arc */}
        <motion.circle
          cx={SIZE / 2} cy={SIZE / 2} r={R}
          fill="none"
          stroke="url(#ring-grad)"
          strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray={CIRC}
          style={{ strokeDashoffset: dashOffset }}
          filter="url(#ring-glow)"
        />
      </svg>

      {/* Center text */}
      <div className={styles.center}>
        {label    && <div className={styles.label}    style={{ color }}>{label}</div>}
        {sublabel && <div className={styles.sublabel}>{sublabel}</div>}
      </div>
    </div>
  )
}
