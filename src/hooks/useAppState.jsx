import { createContext, useContext, useState, useMemo } from 'react'
import { resolveTheme } from '../utils/weatherMap'

const AppContext = createContext(null)

export const DUMMY_DASHBOARD = {
  city_name:           'New Delhi',
  country:             'India',
  temp:                38,
  lat:                 28.6139,
  lon:                 77.2090,
  temperature:         38,
  latitude:            28.6139,
  longitude:           77.2090,
  aqi:                 160,
  pm25:                89,
  pm10:                110,
  humidity:            52,
  wind_speed:          11,
  weather_code:        3,
  weather_description: 'Overcast',
  timezone:            'Asia/Kolkata',
  hourly_aqi: [142,138,130,125,120,118,122,135,155,168,175,172,
               165,160,162,170,178,175,165,148,132,118,108,102],
}

export const DUMMY_SCORE = {
  score:       4.2,
  label:       'Moderate',
  best_window: { start: 19, end: 21, label: '7 PM – 9 PM' },
}

export const DUMMY_ADVISORY = `Conditions today sit at moderate risk for your profile. Particulate matter is elevated but not severe — indoor time carries little concern. If you head out, the 7–9 PM window gives you the cleanest air of the day. Avoid sustained outdoor exertion during afternoon peak hours (3–6 PM).`

export function AppProvider({ children }) {
  const [city,           setCity]           = useState(null)
  const [dashboard,      setDashboard]      = useState(null)
  const [profile,        setProfile]        = useState(null)
  const [exposureResult, setExposureResult] = useState(null)
  const [advisory,       setAdvisory]       = useState(null)
  const [loading,        setLoading]        = useState(false)

  const theme = useMemo(() => {
    const d = dashboard || DUMMY_DASHBOARD
    return resolveTheme(d.aqi, d.weather_code)
  }, [dashboard])

  return (
    <AppContext.Provider value={{
      city,           setCity,
      dashboard,      setDashboard,
      profile,        setProfile,
      exposureResult, setExposureResult,
      advisory,       setAdvisory,
      loading,        setLoading,
      theme,
    }}>
      {children}
    </AppContext.Provider>
  )
}

export function useAppState() {
  const ctx = useContext(AppContext)
  if (!ctx) throw new Error('useAppState must be inside AppProvider')
  return ctx
}
