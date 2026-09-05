import { Routes, Route, useLocation } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import { AppProvider } from './hooks/useAppState'
import LandingPage    from './screens/LandingPage/LandingPage'
import DashboardPage  from './screens/Dashboard/DashboardPage'
import ProfilePage    from './screens/Profile/ProfilePage'
import ExposurePage   from './screens/Exposure/ExposurePage'
import AdvisoryPage   from './screens/Advisory/AdvisoryPage'

export default function App() {
  const location = useLocation()

  return (
    <AppProvider>
      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          <Route path="/"          element={<LandingPage  />} />
          <Route path="/dashboard" element={<DashboardPage/>} />
          <Route path="/profile"   element={<ProfilePage  />} />
          <Route path="/exposure"  element={<ExposurePage />} />
          <Route path="/advisory"  element={<AdvisoryPage />} />
        </Routes>
      </AnimatePresence>
    </AppProvider>
  )
}
