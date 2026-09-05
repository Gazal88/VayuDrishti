import { useEffect } from 'react'

export function useTheme(theme) {
  useEffect(() => {
    if (!theme) return
    const r = document.documentElement.style
    r.setProperty('--accent',         theme.accent)
    r.setProperty('--accent-rgb',     theme.accentRgb)
    r.setProperty('--glow',           theme.glow)
    r.setProperty('--panel-border',   theme.panelBorder)
    r.setProperty('--panel-bg',       theme.panelBg)
    r.setProperty('--panel-bg-mid',   theme.panelBgMid  ?? theme.panelBg)
    r.setProperty('--text-primary',   theme.textPrimary)
    r.setProperty('--text-secondary', theme.textSecondary ?? theme.textPrimary)
    r.setProperty('--text-muted',     theme.textMuted)
    r.setProperty('--text-faint',     theme.textFaint   ?? 'rgba(255,255,255,0.38)')
  }, [theme])
}
