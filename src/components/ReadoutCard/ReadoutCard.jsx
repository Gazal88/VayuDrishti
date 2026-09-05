import { useRef } from 'react'
import { motion, useMotionValue, useTransform, useSpring } from 'framer-motion'
import styles from './ReadoutCard.module.css'

/**
 * ReadoutCard — frosted glass card with 3D tilt, sparkline, pulse dot.
 * Props: value, unit, label, sublabel, color, sparkData (0–1 array), delay
 */
export default function ReadoutCard({ value, unit = '', label, sublabel, color = '#38BDF8', sparkData = [], delay = 0 }) {
  const cardRef = useRef(null)

  // 3-D tilt via mouse position
  const x = useMotionValue(0)
  const y = useMotionValue(0)
  const rotX = useSpring(useTransform(y, [-0.5, 0.5], [6, -6]),  { stiffness: 200, damping: 20 })
  const rotY = useSpring(useTransform(x, [-0.5, 0.5], [-6, 6]), { stiffness: 200, damping: 20 })

  function handleMouseMove(e) {
    const rect = cardRef.current?.getBoundingClientRect()
    if (!rect) return
    x.set((e.clientX - rect.left) / rect.width  - 0.5)
    y.set((e.clientY - rect.top)  / rect.height - 0.5)
  }
  function handleMouseLeave() { x.set(0); y.set(0) }

  // Sparkline path
  const svgW = 76, svgH = 26
  const points = sparkData.length > 1
    ? sparkData.map((v, i) => {
        const px = (i / (sparkData.length - 1)) * svgW
        const py = svgH - Math.max(v, 0) * svgH * 0.88 - 1
        return `${px},${py}`
      }).join(' ')
    : null

  return (
    <motion.div
      ref={cardRef}
      className={styles.card}
      style={{ '--c': color, rotateX: rotX, rotateY: rotY, transformStyle: 'preserve-3d', transformPerspective: 800 }}
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0,  scale: 1 }}
      transition={{ duration: 0.6, delay, ease: [0.16, 1, 0.3, 1] }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      whileHover={{ scale: 1.03 }}
    >
      {/* Top-left color accent stripe */}
      <div className={styles.stripe} style={{ background: color }} />

      {/* Live pulse */}
      <div className={styles.pulse}>
        <span className={styles.pulseDot} style={{ background: color, boxShadow: `0 0 6px ${color}` }} />
        <span className={styles.pulseRing} style={{ borderColor: color }} />
      </div>

      {/* Value */}
      <motion.div
        className={styles.value}
        style={{ color }}
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: delay + 0.15 }}
      >
        {value}
        {unit && <span className={styles.unit}>{unit}</span>}
      </motion.div>

      <div className={styles.label}>{label}</div>
      {sublabel && <div className={styles.sublabel}>{sublabel}</div>}

      {/* Sparkline */}
      {points && (
        <svg className={styles.spark} width={svgW} height={svgH} viewBox={`0 0 ${svgW} ${svgH}`}>
          <defs>
            <linearGradient id={`sg-${label}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={color} stopOpacity="0.25" />
              <stop offset="100%" stopColor={color} stopOpacity="0" />
            </linearGradient>
          </defs>
          {/* Fill area under line */}
          <polyline
            points={`0,${svgH} ${points} ${svgW},${svgH}`}
            fill={`url(#sg-${label})`}
            stroke="none"
          />
          {/* Line */}
          <polyline
            points={points}
            fill="none"
            stroke={color}
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      )}

      {/* Glint on hover */}
      <div className={styles.glint} />
    </motion.div>
  )
}
