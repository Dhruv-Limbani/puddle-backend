import { useAuth } from '../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'
import './Dashboard.css'

export default function Dashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const isVendorOrAdmin = user?.role === 'vendor' || user?.role === 'admin'
  const isBuyer = user?.role === 'buyer'

  return (
    <div className="dashboard-container">
      <div className="dashboard-card">
        <div className="dashboard-header">
          <h1>Welcome, {user?.full_name || user?.email}!</h1>
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>

        <div className="user-info">
          <div className="info-item">
            <span className="info-label">Email:</span>
            <span className="info-value">{user?.email}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Role:</span>
            <span className="info-value role-badge">{user?.role}</span>
          </div>
          {user?.full_name && (
            <div className="info-item">
              <span className="info-label">Full Name:</span>
              <span className="info-value">{user?.full_name}</span>
            </div>
          )}
          <div className="info-item">
            <span className="info-label">Status:</span>
            <span className={`info-value ${user?.is_active ? 'active' : 'inactive'}`}>
              {user?.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>
        </div>

        <div className="dashboard-content">
          <p>Authentication successful! You are now logged in.</p>
          <p>This is your dashboard. More features coming soon...</p>

          <div className="dashboard-actions">
            <button className="primary-action ghost" onClick={() => navigate('/marketplace')}>
              Browse Marketplace
            </button>
            {isVendorOrAdmin && (
              <button className="primary-action" onClick={() => navigate('/vendor-dashboard')}>
                Open Vendor Dashboard
              </button>
            )}
            {isBuyer && (
              <button className="primary-action outline" onClick={() => navigate('/buyer-dashboard')}>
                Open Buyer Dashboard
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

