import { useEffect, useRef } from 'react'
import * as THREE from 'three'
import styles from './ParticleField.module.css'

/**
 * Full-screen Three.js particle field.
 * accentHex: hex string like '#EF4444' — particles + glow tint to match AQI status
 * density: 0–1 — scales particle count & opacity (maps to PM2.5 severity)
 */
export default function ParticleField({ accentHex = '#EF4444', density = 0.5 }) {
  const mountRef = useRef(null)
  const stateRef = useRef({})

  useEffect(() => {
    const mount = mountRef.current
    const W = window.innerWidth
    const H = window.innerHeight

    // ── Renderer ──────────────────────────────────────────────
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
    renderer.setSize(W, H)
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    renderer.setClearColor(0x000000, 0)
    mount.appendChild(renderer.domElement)

    const scene = new THREE.Scene()
    const camera = new THREE.PerspectiveCamera(60, W / H, 0.1, 1000)
    camera.position.z = 55

    // ── Animated gradient mesh (aurora backdrop) ──────────────
    const auroraGeo = new THREE.PlaneGeometry(300, 300, 64, 64)
    const auroraMat = new THREE.ShaderMaterial({
      uniforms: {
        uTime:    { value: 0 },
        uColor1:  { value: new THREE.Color(accentHex) },
        uColor2:  { value: new THREE.Color('#0D1220') },
        uDensity: { value: density },
      },
      vertexShader: `
        uniform float uTime;
        varying vec2 vUv;
        varying float vElevation;
        void main() {
          vUv = uv;
          vec3 pos = position;
          float wave1 = sin(pos.x * 0.03 + uTime * 0.4) * 4.0;
          float wave2 = sin(pos.y * 0.025 + uTime * 0.3) * 3.0;
          float wave3 = cos((pos.x + pos.y) * 0.02 + uTime * 0.2) * 2.5;
          pos.z += wave1 + wave2 + wave3;
          vElevation = pos.z;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
        }
      `,
      fragmentShader: `
        uniform vec3 uColor1;
        uniform vec3 uColor2;
        uniform float uDensity;
        varying vec2 vUv;
        varying float vElevation;
        void main() {
          float mixFactor = smoothstep(-6.0, 6.0, vElevation);
          vec3 col = mix(uColor2, uColor1, mixFactor * uDensity * 0.6);
          float edgeFade = smoothstep(0.0, 0.3, vUv.x) * smoothstep(1.0, 0.7, vUv.x)
                         * smoothstep(0.0, 0.3, vUv.y) * smoothstep(1.0, 0.7, vUv.y);
          gl_FragColor = vec4(col, edgeFade * 0.35 * uDensity);
        }
      `,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    })
    const aurora = new THREE.Mesh(auroraGeo, auroraMat)
    aurora.position.z = -80
    scene.add(aurora)

    // ── Particle Layers ────────────────────────────────────────
    function makeParticleLayer({ count, spread, zRange, size, opacity, speedRange, color }) {
      const geo = new THREE.BufferGeometry()
      const positions = new Float32Array(count * 3)
      const speeds = new Float32Array(count)
      const phases = new Float32Array(count)

      for (let i = 0; i < count; i++) {
        positions[i * 3]     = (Math.random() - 0.3) * spread
        positions[i * 3 + 1] = (Math.random() - 0.5) * spread * 0.7
        positions[i * 3 + 2] = zRange[0] + Math.random() * (zRange[1] - zRange[0])
        speeds[i]  = speedRange[0] + Math.random() * (speedRange[1] - speedRange[0])
        phases[i]  = Math.random() * Math.PI * 2
      }

      geo.setAttribute('position', new THREE.BufferAttribute(positions, 3))
      const mat = new THREE.PointsMaterial({
        color,
        size,
        transparent: true,
        opacity: opacity * (0.4 + density * 0.6),
        depthWrite: false,
        blending: THREE.AdditiveBlending,
        sizeAttenuation: true,
      })

      const pts = new THREE.Points(geo, mat)
      scene.add(pts)
      return { pts, geo, speeds, phases, count, spread }
    }

    const hexColor = parseInt(accentHex.replace('#', ''), 16)
    const speedScale = 0.6 + density * 1.4

    const layerFar  = makeParticleLayer({ count: 800,  spread: 240, zRange: [-100,-50], size: 1.1, opacity: 0.18, speedRange: [0.01, 0.025], color: hexColor })
    const layerMid  = makeParticleLayer({ count: 1200, spread: 180, zRange: [-40, 0],   size: 0.65, opacity: 0.5,  speedRange: [0.03, 0.07],  color: hexColor })
    const layerNear = makeParticleLayer({ count: 400,  spread: 130, zRange: [5,  40],   size: 0.4, opacity: 0.85, speedRange: [0.07, 0.13],  color: hexColor })
    const layers = [layerFar, layerMid, layerNear]

    // ── Floating dust motes (large slow blobs) ─────────────────
    const moteGeo = new THREE.BufferGeometry()
    const moteCount = 18
    const motePos = new Float32Array(moteCount * 3)
    for (let i = 0; i < moteCount; i++) {
      motePos[i * 3]     = (Math.random() - 0.5) * 200
      motePos[i * 3 + 1] = (Math.random() - 0.5) * 120
      motePos[i * 3 + 2] = -10 + Math.random() * 30
    }
    moteGeo.setAttribute('position', new THREE.BufferAttribute(motePos, 3))
    const moteMat = new THREE.PointsMaterial({
      color: hexColor,
      size: 3.5,
      transparent: true,
      opacity: 0.12,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    })
    const motes = new THREE.Points(moteGeo, moteMat)
    scene.add(motes)

    // ── Mouse parallax ─────────────────────────────────────────
    let mouseX = 0, mouseY = 0
    let targetX = 0, targetY = 0

    const onMouseMove = (e) => {
      mouseX = (e.clientX / window.innerWidth  - 0.5) * 2
      mouseY = (e.clientY / window.innerHeight - 0.5) * 2
    }
    window.addEventListener('mousemove', onMouseMove)

    // ── Animate ────────────────────────────────────────────────
    let rafId
    let startTime = Date.now()

    function animate() {
      rafId = requestAnimationFrame(animate)
      const elapsed = (Date.now() - startTime) * 0.001

      // aurora wave
      auroraMat.uniforms.uTime.value = elapsed

      // parallax lerp
      targetX += (mouseX * 0.3 - targetX) * 0.03
      targetY += (mouseY * 0.22 - targetY) * 0.03
      camera.position.x = targetX * 8
      camera.position.y = -targetY * 6
      camera.position.z = 55 + Math.sin(elapsed * 0.18) * 5
      camera.lookAt(0, 0, 0)

      // drift particles
      layers.forEach(layer => {
        const pos = layer.geo.attributes.position.array
        for (let i = 0; i < layer.count; i++) {
          pos[i * 3]     -= layer.speeds[i] * speedScale
          pos[i * 3 + 1] += Math.sin(elapsed * 0.4 + layer.phases[i]) * 0.006
          if (pos[i * 3] < -layer.spread * 0.6) {
            pos[i * 3] = layer.spread * 0.6
          }
        }
        layer.geo.attributes.position.needsUpdate = true
        layer.pts.rotation.y += 0.00015
      })

      // motes bob
      const moteArr = moteGeo.attributes.position.array
      for (let i = 0; i < moteCount; i++) {
        moteArr[i * 3 + 1] += Math.sin(elapsed * 0.3 + i * 1.3) * 0.01
      }
      moteGeo.attributes.position.needsUpdate = true

      renderer.render(scene, camera)
    }
    animate()

    // ── Resize ─────────────────────────────────────────────────
    const onResize = () => {
      const w = window.innerWidth
      const h = window.innerHeight
      camera.aspect = w / h
      camera.updateProjectionMatrix()
      renderer.setSize(w, h)
    }
    window.addEventListener('resize', onResize)

    // store refs for accent update
    stateRef.current = { auroraMat, layers, moteMat }

    // ── Cleanup ────────────────────────────────────────────────
    return () => {
      cancelAnimationFrame(rafId)
      window.removeEventListener('mousemove', onMouseMove)
      window.removeEventListener('resize', onResize)
      renderer.dispose()
      if (mount.contains(renderer.domElement)) mount.removeChild(renderer.domElement)
    }
  }, []) // run once on mount

  // Update colors when accentHex / density changes (without full remount)
  useEffect(() => {
    const { auroraMat, layers, moteMat } = stateRef.current
    if (!auroraMat) return
    const hexColor = parseInt(accentHex.replace('#', ''), 16)
    auroraMat.uniforms.uColor1.value.set(accentHex)
    auroraMat.uniforms.uDensity.value = density
    layers?.forEach(layer => {
      layer.pts.material.color.setHex(hexColor)
      layer.pts.material.opacity = (layer === layers[0] ? 0.18 : layer === layers[1] ? 0.5 : 0.85) * (0.4 + density * 0.6)
    })
    if (moteMat) moteMat.color.setHex(hexColor)
  }, [accentHex, density])

  return <div ref={mountRef} className={styles.canvas} />
}
