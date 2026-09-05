/**
 * weatherMap.js
 * Maps Open-Meteo weather_code + AQI → background image + full UI theme.
 *
 * Open-Meteo WMO weather codes:
 *   0        Clear sky
 *   1,2,3    Mainly clear / partly cloudy / overcast
 *   45,48    Fog
 *   51-57    Drizzle
 *   61-67    Rain
 *   71-77    Snow
 *   80-82    Rain showers
 *   85,86    Snow showers
 *   95       Thunderstorm
 *   96,99    Thunderstorm with hail
 */

import bgClear        from '../assets/backgrounds/bg-clear.jpeg'
import bgCloudy       from '../assets/backgrounds/bg-cloudy.png'
import bgHaze         from '../assets/backgrounds/bg-haze.png'
import bgPolluted     from '../assets/backgrounds/bg-polluted.png'
import bgVeryPolluted from '../assets/backgrounds/bg-very-polluted.png'
import bgRain         from '../assets/backgrounds/bg-rain.png'
import bgStorm        from '../assets/backgrounds/bg-storm.png'

/**
 * Theme palette per condition. Every screen reads from these tokens
 * instead of hardcoded hex values.
 *
 * accent      — primary interactive color (buttons, highlights, active states)
 * accentRgb   — for rgba() use
 * glow        — background radial glow tint
 * panelBorder — card / panel border tint
 * panelBg     — card background
 * textPrimary — main readable text
 * textMuted   — secondary text
 * overlay     — dark overlay over bg image (opacity fraction, 0–1)
 * overlayType — 'rain' | 'dust' | 'haze' | 'cloud' | 'none'
 */

export const THEMES = {
  clear: {
    bg: bgClear,
    accent: '#0EA5E9',
    accentRgb: '14,165,233',
    glow: 'rgba(14,165,233,0.20)',
    // White-tinted frosted glass — photo shows through
    panelBorder: 'rgba(255,255,255,0.32)',
    panelBg:     'rgba(255,255,255,0.18)',
    panelBgMid:  'rgba(255,255,255,0.10)',
    textPrimary: '#FFFFFF',
    textSecondary: '#E0F2FE',
    textMuted:   'rgba(255,255,255,0.68)',
    textFaint:   'rgba(255,255,255,0.40)',
    // Overlay very light — let the blue sky breathe
    overlay: 0.18,
    overlayType: 'none',
    label: 'Clear',
  },
  cloudy: {
    bg: bgCloudy,
    accent: '#BAC8D3',
    accentRgb: '186,200,211',
    glow: 'rgba(186,200,211,0.18)',
    panelBorder: 'rgba(255,255,255,0.28)',
    panelBg:     'rgba(255,255,255,0.16)',
    panelBgMid:  'rgba(255,255,255,0.09)',
    textPrimary: '#FFFFFF',
    textSecondary: '#E2EAF0',
    textMuted:   'rgba(255,255,255,0.65)',
    textFaint:   'rgba(255,255,255,0.38)',
    overlay: 0.22,
    overlayType: 'cloud',
    label: 'Cloudy',
  },
  haze: {
    bg: bgHaze,
    accent: '#F59E0B',
    accentRgb: '245,158,11',
    glow: 'rgba(245,158,11,0.22)',
    panelBorder: 'rgba(255,255,255,0.30)',
    panelBg:     'rgba(255,248,230,0.20)',
    panelBgMid:  'rgba(255,245,210,0.12)',
    textPrimary: '#FFFFFF',
    textSecondary: '#FEF3C7',
    textMuted:   'rgba(255,255,255,0.68)',
    textFaint:   'rgba(255,255,255,0.40)',
    overlay: 0.20,
    overlayType: 'haze',
    label: 'Hazy',
  },
  polluted: {
    bg: bgPolluted,
    accent: '#FB923C',
    accentRgb: '251,146,60',
    glow: 'rgba(251,146,60,0.22)',
    panelBorder: 'rgba(255,255,255,0.28)',
    panelBg:     'rgba(255,240,220,0.18)',
    panelBgMid:  'rgba(255,235,200,0.10)',
    textPrimary: '#FFFFFF',
    textSecondary: '#FFEDD5',
    textMuted:   'rgba(255,255,255,0.68)',
    textFaint:   'rgba(255,255,255,0.40)',
    overlay: 0.25,
    overlayType: 'dust',
    label: 'Polluted',
  },
  veryPolluted: {
    bg: bgVeryPolluted,
    accent: '#EF4444',
    accentRgb: '239,68,68',
    glow: 'rgba(239,68,68,0.22)',
    panelBorder: 'rgba(255,255,255,0.25)',
    panelBg:     'rgba(255,230,220,0.16)',
    panelBgMid:  'rgba(255,220,210,0.09)',
    textPrimary: '#FFFFFF',
    textSecondary: '#FEE2E2',
    textMuted:   'rgba(255,255,255,0.65)',
    textFaint:   'rgba(255,255,255,0.38)',
    overlay: 0.30,
    overlayType: 'dust',
    label: 'Very Polluted',
  },
  rain: {
    bg: bgRain,
    accent: '#10B981',
    accentRgb: '16,185,129',
    glow: 'rgba(16,185,129,0.20)',
    panelBorder: 'rgba(255,255,255,0.28)',
    panelBg:     'rgba(230,255,245,0.16)',
    panelBgMid:  'rgba(210,255,240,0.09)',
    textPrimary: '#FFFFFF',
    textSecondary: '#D1FAE5',
    textMuted:   'rgba(255,255,255,0.68)',
    textFaint:   'rgba(255,255,255,0.40)',
    overlay: 0.22,
    overlayType: 'rain',
    label: 'Rainy',
  },
  storm: {
    bg: bgStorm,
    accent: '#A78BFA',
    accentRgb: '167,139,250',
    glow: 'rgba(167,139,250,0.22)',
    panelBorder: 'rgba(255,255,255,0.26)',
    panelBg:     'rgba(235,228,255,0.16)',
    panelBgMid:  'rgba(220,210,255,0.09)',
    textPrimary: '#FFFFFF',
    textSecondary: '#EDE9FE',
    textMuted:   'rgba(255,255,255,0.66)',
    textFaint:   'rgba(255,255,255,0.38)',
    overlay: 0.28,
    overlayType: 'rain',
    label: 'Storm',
  },
}

/**
 * Primary resolver: AQI takes priority for pollution conditions;
 * weather_code takes priority for rain/storm/clear.
 */
export function resolveTheme(aqi = 0, weatherCode = 0) {
  // Rain / storm always wins visually — rain washes the air
  if (weatherCode === 95 || weatherCode === 96 || weatherCode === 99) return THEMES.storm
  if ((weatherCode >= 51 && weatherCode <= 67) || (weatherCode >= 80 && weatherCode <= 82)) return THEMES.rain

  // Fog/haze as weather
  if (weatherCode === 45 || weatherCode === 48) return THEMES.haze

  // AQI-driven pollution backgrounds
  if (aqi > 200) return THEMES.veryPolluted
  if (aqi > 100) return THEMES.polluted
  if (aqi > 60)  return THEMES.haze

  // Low AQI — use weather
  if (weatherCode >= 1 && weatherCode <= 3) return THEMES.cloudy
  return THEMES.clear
}

/**
 * Expose AQI badge color separately (for rings, labels — not the whole theme)
 */
export function aqiBadgeColor(aqi) {
  if (aqi <= 50)  return '#34D399'
  if (aqi <= 100) return '#FBBF24'
  if (aqi <= 150) return '#F97316'
  if (aqi <= 200) return '#EF4444'
  if (aqi <= 300) return '#C026D3'
  return '#7C2D12'
}

export function aqiBadgeLabel(aqi) {
  if (aqi <= 50)  return 'Good'
  if (aqi <= 100) return 'Moderate'
  if (aqi <= 150) return 'Unhealthy for SG'
  if (aqi <= 200) return 'Unhealthy'
  if (aqi <= 300) return 'Very Unhealthy'
  return 'Hazardous'
}
