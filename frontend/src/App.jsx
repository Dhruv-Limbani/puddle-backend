import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Auth from './pages/Auth'
import VendorDashboard from './pages/VendorDashboard'
import BuyerDashboard from './pages/BuyerDashboard'
import Marketplace from './pages/Marketplace'
import DatasetProfilePage from './pages/DatasetProfilePage'
import VendorProfilePage from './pages/VendorProfilePage'

function PrivateRoute({ children }) {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? children : <Navigate to="/login" />
}

function VendorRoute({ children }) {
  const { isAuthenticated, user } = useAuth()

  if (!isAuthenticated) {
    return <Navigate to="/login" />
  }

  if (user?.role !== 'vendor' && user?.role !== 'admin') {
    return <Navigate to="/login" />
  }

  return children
}

function BuyerRoute({ children }) {
  const { isAuthenticated, user } = useAuth()

  if (!isAuthenticated) {
    return <Navigate to="/login" />
  }

  if (user?.role !== 'buyer') {
    return <Navigate to="/login" />
  }

  return children
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Auth />} />
          <Route path="/signup" element={<Auth />} />
          <Route
            path="/vendor-dashboard"
            element={
              <VendorRoute>
                <VendorDashboard />
              </VendorRoute>
            }
          />
          <Route
            path="/buyer-dashboard"
            element={
              <BuyerRoute>
                <BuyerDashboard />
              </BuyerRoute>
            }
          />
          <Route
            path="/marketplace"
            element={
              <PrivateRoute>
                <Marketplace />
              </PrivateRoute>
            }
          />
          <Route
            path="/marketplace/dataset/:datasetId"
            element={
              <PrivateRoute>
                <DatasetProfilePage />
              </PrivateRoute>
            }
          />
          <Route
            path="/marketplace/vendor/:vendorId"
            element={
              <PrivateRoute>
                <VendorProfilePage />
              </PrivateRoute>
            }
          />
          <Route path="/" element={<Navigate to="/login" />} />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App

