/**
 * AQI color + label utilities — single source of truth for all screens
 */

export const AQI_LEVELS = [
  { max: 50,  label: 'Good',            hex: '#34D399', rgb: '52, 211, 153',   cssVar: '--good' },
  { max: 100, label: 'Moderate',        hex: '#FBBF24', rgb: '251, 191, 36',   cssVar: '--mod'  },
  { max: 150, label: 'Unhealthy for SG',hex: '#F97316', rgb: '249, 115, 22',   cssVar: '--usg'  },
  { max: 200, label: 'Unhealthy',       hex: '#EF4444', rgb: '239, 68, 68',    cssVar: '--unh'  },
  { max: 300, label: 'Very Unhealthy',  hex: '#C026D3', rgb: '192, 38, 211',   cssVar: '--vunh' },
  { max: 999, label: 'Hazardous',       hex: '#7C2D12', rgb: '124, 45, 18',    cssVar: '--haz'  },
]

export function getAqiInfo(aqi) {
  return AQI_LEVELS.find(l => aqi <= l.max) || AQI_LEVELS[AQI_LEVELS.length - 1]
}

export function getAqiColor(aqi) {
  return getAqiInfo(aqi).hex
}

export function getAqiLabel(aqi) {
  return getAqiInfo(aqi).label
}

/** Score 0–10 → color */
export function getScoreColor(score) {
  if (score <= 2)  return '#34D399'
  if (score <= 4)  return '#FBBF24'
  if (score <= 6)  return '#F97316'
  if (score <= 8)  return '#EF4444'
  if (score <= 9)  return '#C026D3'
  return '#7C2D12'
}

export function getScoreLabel(score) {
  if (score <= 2)  return 'Low'
  if (score <= 4)  return 'Moderate'
  if (score <= 6)  return 'Elevated'
  if (score <= 8)  return 'High'
  if (score <= 9)  return 'Very High'
  return 'Hazardous'
}

/** Normalize AQI 0–500 → ring fill 0–1 */
export function aqiToRingPct(aqi) {
  return Math.min(aqi / 500, 1)
}

/** Score 0–10 → ring fill 0–1 */
export function scoreToRingPct(score) {
  return Math.min(score / 10, 1)
}
