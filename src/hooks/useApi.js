import axios from 'axios'
import { DUMMY_DASHBOARD, DUMMY_SCORE, DUMMY_ADVISORY } from './useAppState'

const BASE = import.meta.env.VITE_API_URL
  ? import.meta.env.VITE_API_URL.replace(/\/$/, '')  // Railway URL in production
  : '/api'                                            // Vite proxy in local dev
export const USE_DUMMY = false

function delay(ms) {
  return new Promise(res => setTimeout(res, ms))
}

function normaliseDashboard(raw) {
  return {
    city_name:           raw.city_name,
    country:             raw.country      ?? null,
    temp:                raw.temperature  ?? raw.temp,
    lat:                 raw.latitude     ?? raw.lat,
    lon:                 raw.longitude    ?? raw.lon,
    aqi:                 raw.aqi          ?? 0,
    pm25:                raw.pm25         ?? 0,
    pm10:                raw.pm10         ?? 0,
    humidity:            raw.humidity     ?? 0,
    wind_speed:          raw.wind_speed   ?? 0,
    weather_code:        raw.weather_code ?? 0,
    weather_description: raw.weather_description ?? '',
    timezone:            raw.timezone     ?? null,
    hourly_aqi:          raw.hourly_aqi   ?? Array(24).fill(raw.aqi ?? 0),
    temperature:         raw.temperature,
    latitude:            raw.latitude,
    longitude:           raw.longitude,
  }
}

function normaliseExposure(raw) {
  const win = raw.best_window
  return {
    score:     raw.score,
    label:     raw.label,
    breakdown: raw.breakdown ?? null,
    city_name: raw.city_name ?? null,
    best_window: win
      ? {
          start:         new Date(win.start).getHours(),
          end:           new Date(win.end).getHours(),
          label:         win.label,
          average_score: win.average_score,
          average_label: win.average_label,
        }
      : { start: 19, end: 21, label: '7 PM – 9 PM' },
  }
}

export async function fetchDashboard(city) {
  if (USE_DUMMY) {
    await delay(700)
    return { ...DUMMY_DASHBOARD, city_name: city }
  }
  const { data } = await axios.get(`${BASE}/dashboard`, { params: { city } })
  return normaliseDashboard(data)
}

export async function fetchExposureScore(payload) {
  if (USE_DUMMY) {
    await delay(600)
    const highRisk =
      payload.health_condition !== 'none' ||
      payload.occupation === 'outdoor_worker'
    return highRisk
      ? { score: 9.6, label: 'Very High',
          best_window: { start: 19, end: 21, label: '7 PM – 9 PM' } }
      : DUMMY_SCORE
  }

  const body = {
    city:                payload.city ?? null,
    aqi:                 payload.aqi  ?? null,
    pm25:                payload.pm25 ?? null,
    temperature:         payload.temp ?? payload.temperature ?? null,
    include_best_window: true,
    profile: {
      age_group:        payload.age_group,
      health_condition: payload.health_condition,
      occupation:       payload.occupation,
    },
  }

  const { data } = await axios.post(`${BASE}/exposure-score`, body)
  return normaliseExposure(data)
}

export async function fetchAdvisory(payload) {
  if (USE_DUMMY) {
    await delay(1200)
    return payload.score >= 7
      ? `Same air, very different risk — your profile pushes you into very high territory. Shift heavy outdoor tasks to ${payload.window} and keep a reliever on hand. Avoid the 3–6 PM window entirely.`
      : DUMMY_ADVISORY
  }

  const { conditions, profile, score, label, window: win } = payload

  const labelMap = {
    'Low':       'Low',
    'Moderate':  'Moderate',
    'Elevated':  'Moderate',
    'High':      'High',
    'Very High': 'Very High',
    'Hazardous': 'Very High',
  }

  const body = {
    temperature: conditions.temp ?? conditions.temperature ?? 30,
    aqi:         conditions.aqi  ?? 0,
    pm25:        conditions.pm25 ?? 0,
    profile: {
      age_group:        profile.age_group,
      health_condition: profile.health_condition,
      occupation:       profile.occupation,
    },
    score,
    label:  labelMap[label] ?? 'Moderate',
    window: win ?? 'Not available',
  }

  const { data } = await axios.post(`${BASE}/advisory`, body)
  return data.advisory_text
}

export async function fetchAnalyze(city, profile) {
  if (USE_DUMMY) {
    await delay(1500)
    return {
      dashboard:     normaliseDashboard({ ...DUMMY_DASHBOARD, city_name: city }),
      exposure:      DUMMY_SCORE,
      advisory_text: DUMMY_ADVISORY,
    }
  }

  const body = {
    city,
    profile: {
      age_group:        profile.age_group,
      health_condition: profile.health_condition,
      occupation:       profile.occupation,
    },
    include_advisory: true,
    include_hourly:   false,
  }

  const { data } = await axios.post(`${BASE}/analyze`, body)
  return {
    dashboard:     normaliseDashboard(data.dashboard),
    exposure:      normaliseExposure(data.exposure),
    advisory_text: data.advisory?.advisory_text ?? null,
  }
}
