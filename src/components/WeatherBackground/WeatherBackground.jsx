import { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import styles from './WeatherBackground.module.css'

/**
 * WeatherBackground
 * Props:
 *   bgImage      — imported image URL (from weatherMap)
 *   overlayType  — 'rain' | 'dust' | 'haze' | 'cloud' | 'none'
 *   overlayDark  — 0–1 darkness of image overlay
 *   theme        — full theme object (for tint colors)
 */
export default function WeatherBackground({ bgImage, overlayType = 'none', overlayDark = 0.45, theme }) {
  const canvasRef = useRef(null)
  const rafRef    = useRef(null)
  const [currentBg, setCurrentBg]   = useState(bgImage)
  const [prevBg,    setPrevBg]      = useState(null)
  const [crossfade, setCrossfade]   = useState(false)

  // Crossfade when bgImage changes
  useEffect(() => {
    if (bgImage === currentBg) return
    setPrevBg(currentBg)
    setCurrentBg(bgImage)
    setCrossfade(true)
    const t = setTimeout(() => { setPrevBg(null); setCrossfade(false) }, 1200)
    return () => clearTimeout(t)
  }, [bgImage])

  // Canvas weather overlay
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')

    function resize() {
      canvas.width  = window.innerWidth
      canvas.height = window.innerHeight
    }
    resize()
    window.addEventListener('resize', resize)

    let particles = []

    // ── Rain ──────────────────────────────────────────────────
    function initRain() {
      particles = Array.from({ length: 220 }, () => ({
        x:     Math.random() * canvas.width,
        y:     Math.random() * canvas.height,
        len:   12 + Math.random() * 22,
        speed: 18 + Math.random() * 14,
        opacity: 0.08 + Math.random() * 0.18,
        width: 0.6 + Math.random() * 0.8,
      }))
    }

    function drawRain() {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      ctx.strokeStyle = '#a8d8ea'
      particles.forEach(p => {
        ctx.globalAlpha = p.opacity
        ctx.lineWidth   = p.width
        ctx.beginPath()
        // slight angle
        ctx.moveTo(p.x, p.y)
        ctx.lineTo(p.x + p.len * 0.18, p.y + p.len)
        ctx.stroke()
        p.y += p.speed
        p.x += p.speed * 0.18
        if (p.y > canvas.height + 30) {
          p.y = -p.len
          p.x = Math.random() * canvas.width
        }
      })
      ctx.globalAlpha = 1
    }

    // ── Dust / smog drifting particles ────────────────────────
    function initDust() {
      particles = Array.from({ length: 160 }, () => ({
        x:       Math.random() * canvas.width,
        y:       Math.random() * canvas.height,
        r:       1.5 + Math.random() * 4,
        speedX:  0.15 + Math.random() * 0.4,
        speedY: (Math.random() - 0.5) * 0.15,
        opacity: 0.04 + Math.random() * 0.14,
        phase:   Math.random() * Math.PI * 2,
      }))
    }

    function drawDust(t) {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      const color = theme?.accent || '#D4A84B'
      particles.forEach(p => {
        ctx.globalAlpha = p.opacity * (0.7 + 0.3 * Math.sin(t * 0.0005 + p.phase))
        ctx.fillStyle   = color
        ctx.beginPath()
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
        ctx.fill()
        p.x += p.speedX
        p.y += p.speedY + Math.sin(t * 0.0004 + p.phase) * 0.12
        if (p.x > canvas.width + 10)  p.x = -10
        if (p.y > canvas.height + 10) p.y = -10
        if (p.y < -10) p.y = canvas.height + 10
      })
      ctx.globalAlpha = 1
    }

    // ── Haze: slow large soft blobs ───────────────────────────
    function initHaze() {
      particles = Array.from({ length: 12 }, () => ({
        x:       Math.random() * canvas.width,
        y:       Math.random() * canvas.height,
        r:       80 + Math.random() * 160,
        speedX:  0.08 + Math.random() * 0.14,
        opacity: 0.03 + Math.random() * 0.07,
        phase:   Math.random() * Math.PI * 2,
      }))
    }

    function drawHaze(t) {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      particles.forEach(p => {
        const alpha = p.opacity * (0.6 + 0.4 * Math.sin(t * 0.0003 + p.phase))
        const grad = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r)
        grad.addColorStop(0, `rgba(210,190,120,${alpha})`)
        grad.addColorStop(1, 'rgba(210,190,120,0)')
        ctx.fillStyle = grad
        ctx.beginPath()
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
        ctx.fill()
        p.x += p.speedX
        if (p.x > canvas.width + p.r) p.x = -p.r
      })
    }

    // ── Cloud parallax: layered soft cloud drift ───────────────
    function initCloud() {
      particles = Array.from({ length: 8 }, () => ({
        x:       Math.random() * canvas.width * 1.5,
        y:       20 + Math.random() * canvas.height * 0.5,
        w:       200 + Math.random() * 300,
        h:       60  + Math.random() * 80,
        speed:   0.1 + Math.random() * 0.2,
        opacity: 0.03 + Math.random() * 0.07,
      }))
    }

    function drawCloud() {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      particles.forEach(p => {
        const grad = ctx.createRadialGradient(
          p.x + p.w / 2, p.y + p.h / 2, 0,
          p.x + p.w / 2, p.y + p.h / 2, p.w / 2
        )
        grad.addColorStop(0, `rgba(200,210,220,${p.opacity})`)
        grad.addColorStop(1, 'rgba(200,210,220,0)')
        ctx.fillStyle = grad
        ctx.beginPath()
        ctx.ellipse(p.x + p.w / 2, p.y + p.h / 2, p.w / 2, p.h / 2, 0, 0, Math.PI * 2)
        ctx.fill()
        p.x += p.speed
        if (p.x > canvas.width + p.w) p.x = -p.w
      })
    }

    // ── Init + loop ───────────────────────────────────────────
    if (overlayType === 'rain')  initRain()
    if (overlayType === 'dust')  initDust()
    if (overlayType === 'haze')  initHaze()
    if (overlayType === 'cloud') initCloud()

    let startTime = performance.now()

    function loop() {
      const t = performance.now() - startTime
      if (overlayType === 'rain')  drawRain()
      if (overlayType === 'dust')  drawDust(t)
      if (overlayType === 'haze')  drawHaze(t)
      if (overlayType === 'cloud') drawCloud()
      if (overlayType === 'none')  ctx.clearRect(0, 0, canvas.width, canvas.height)
      rafRef.current = requestAnimationFrame(loop)
    }
    loop()

    return () => {
      cancelAnimationFrame(rafRef.current)
      window.removeEventListener('resize', resize)
    }
  }, [overlayType, theme?.accent])

  return (
    <div className={styles.root}>
      {/* Previous bg fading out */}
      <AnimatePresence>
        {prevBg && (
          <motion.div
            key={prevBg}
            className={styles.layer}
            style={{ backgroundImage: `url(${prevBg})` }}
            initial={{ opacity: 1 }}
            animate={{ opacity: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1.1, ease: 'easeInOut' }}
          />
        )}
      </AnimatePresence>

      {/* Current bg fading in */}
      <motion.div
        key={currentBg}
        className={styles.layer}
        style={{ backgroundImage: `url(${currentBg})` }}
        initial={{ opacity: crossfade ? 0 : 1 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1.1, ease: 'easeInOut' }}
      />

      {/* Dark overlay — keeps text readable */}
      <div
        className={styles.overlay}
        style={{ opacity: overlayDark }}
      />

      {/* Vignette — natural edge darkening */}
      <div className={styles.vignette} />

      {/* Horizontal gradient — left panel legibility */}
      <div className={styles.leftFade} />

      {/* Canvas weather FX */}
      <canvas ref={canvasRef} className={styles.canvas} />
    </div>
  )
}
