import { createContext, useContext, useState, useEffect } from 'react'
import { authService } from '../services/authService'
// --- FIX 1: Import the vendorService ---
import { vendorService } from '../services/vendorService'

const AuthContext = createContext()

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))
  // --- FIX 2: Add vendorId to your state ---
  const [vendorId, setVendorId] = useState(null)
  const [loading, setLoading] = useState(true)

  // --- FIX 3: Create a helper to fetch vendor data ---
  /**
   * Fetches the vendor profile ID if the user is a vendor.
   */
  const loadVendorData = async (authToken, userData) => {
    // Only fetch if the user is a vendor
    if (userData && userData.role === 'vendor') {
      try {
        // Use the /me endpoint to get the current user's vendor profile
        const vendorProfile = await vendorService.getMe(authToken)
        
        if (vendorProfile) {
          setVendorId(vendorProfile.id) // Set the vendorId from the profile
        } else {
          console.warn('Vendor user has no vendor profile.')
          setVendorId(null) // Ensure it's null if no profile is found
        }
      } catch (err) {
        console.error('Failed to fetch vendor profile:', err)
        setVendorId(null)
      }
    } else {
      // Not a vendor, or no user, so set vendorId to null
      setVendorId(null)
    }
  }

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('token')
      if (storedToken) {
        try {
          const userData = await authService.getCurrentUser(storedToken)
          setUser(userData)
          setToken(storedToken)
          // --- FIX 4: Load vendor data on page refresh ---
          await loadVendorData(storedToken, userData)
        } catch (error) {
          localStorage.removeItem('token')
          setToken(null)
          setUser(null)
          setVendorId(null) // <-- Reset vendorId on error
        }
      }
      setLoading(false)
    }
    initAuth()
  }, [])

  const login = async (email, password) => {
    const response = await authService.login(email, password)
    const { access_token, user: userData } = response
    localStorage.setItem('token', access_token)
    setToken(access_token)
    setUser(userData)
    // --- FIX 5: Load vendor data on new login ---
    await loadVendorData(access_token, userData)
    return response
  }

  const signup = async (email, password, role, fullName) => {
    // Note: After signup, you might want to call login() to get the vendorId
    const userData = await authService.signup(email, password, role, fullName)
    return userData
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
    setVendorId(null) // <-- Reset vendorId on logout
  }

  const value = {
    user,
    token,
    // --- FIX 6: Add vendorId to the context value ---
    vendorId,
    // --- FIX 7: Expose refreshVendorId so components can update it ---
    refreshVendorId: () => loadVendorData(token, user),
    isAuthenticated: !!token,
    loading,
    login,
    signup,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}