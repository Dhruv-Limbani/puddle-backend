import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { buyerService } from '../services/buyerService'
import './BuyerDashboard.css'

const EMPTY_FORM = {
  name: '',
  organization: '',
  contact_email: '',
  contact_phone: '',
  country: '',
  region: '',
  city: '',
  address: '',
  organization_type: '',
  job_title: '',
  industry: '',
  use_case_focus: '',
}

export default function BuyerDashboard() {
  const { user, token, logout } = useAuth()
  const navigate = useNavigate()

  const [profile, setProfile] = useState(null)
  const [formData, setFormData] = useState(EMPTY_FORM)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const isBuyer = useMemo(() => user?.role === 'buyer', [user?.role])

  useEffect(() => {
    if (!token) {
      navigate('/login')
      return
    }

    if (!isBuyer) {
      navigate('/dashboard')
      return
    }

    loadProfile()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, user?.id])

  const loadProfile = async () => {
    setLoading(true)
    setError('')
    setMessage('')

    try {
      const buyer = await buyerService.getProfile(token)
      setProfile(buyer)
      if (buyer) {
        setFormData({
          name: buyer.name || '',
          organization: buyer.organization || '',
          contact_email: buyer.contact_email || '',
          contact_phone: buyer.contact_phone || '',
          country: buyer.country || '',
          region: buyer.region || '',
          city: buyer.city || '',
          address: buyer.address || '',
          organization_type: buyer.organization_type || '',
          job_title: buyer.job_title || '',
          industry: buyer.industry || '',
          use_case_focus: buyer.use_case_focus || '',
        })
      } else {
        setFormData(EMPTY_FORM)
      }
    } catch (err) {
      setError(err.message || 'Failed to load buyer profile')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (event) => {
    const { name, value } = event.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setSaving(true)
    setError('')
    setMessage('')

    if (!formData.name.trim()) {
      setError('Name is required')
      setSaving(false)
      return
    }

    const payload = {}
    Object.entries(formData).forEach(([key, value]) => {
      if (value !== '') {
        payload[key] = value
      }
    })

    try {
      if (profile) {
        await buyerService.updateProfile(token, payload)
        setMessage('Buyer profile updated successfully')
      } else {
        await buyerService.createProfile(token, payload)
        setMessage('Buyer profile created successfully')
      }
      await loadProfile()
    } catch (err) {
      setError(err.message || 'Failed to save buyer profile')
    } finally {
      setSaving(false)
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const headerTitle = profile ? `Welcome, ${profile.name}` : 'Create Buyer Profile'

  return (
    <div className="buyer-dashboard-container">
      <div className="buyer-dashboard-card">
        <div className="buyer-dashboard-header">
          <div>
            <h1>{headerTitle}</h1>
            <p>Manage your buyer presence on Puddle.</p>
          </div>
          <div className="buyer-dashboard-actions">
            <button className="secondary" onClick={() => navigate('/dashboard')}>
              Back to Account
            </button>
            <button className="danger" onClick={handleLogout}>
              Logout
            </button>
          </div>
        </div>

        {(message || error) && (
          <div className="buyer-alerts">
            {message && <div className="success">{message}</div>}
            {error && <div className="error">{error}</div>}
          </div>
        )}

        <form className="buyer-form" onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="form-group full">
              <label htmlFor="name">
                Full Name <span>*</span>
              </label>
              <input
                id="name"
                name="name"
                type="text"
                value={formData.name}
                onChange={handleChange}
                required
                disabled={saving || loading}
                placeholder="Jane Doe"
              />
            </div>

            <div className="form-group">
              <label htmlFor="organization">Organization</label>
              <input
                id="organization"
                name="organization"
                type="text"
                value={formData.organization}
                onChange={handleChange}
                disabled={saving || loading}
                placeholder="Research Institute"
              />
            </div>

            <div className="form-group">
              <label htmlFor="job_title">Job Title</label>
              <input
                id="job_title"
                name="job_title"
                type="text"
                value={formData.job_title}
                onChange={handleChange}
                disabled={saving || loading}
                placeholder="Data Scientist"
              />
            </div>

            <div className="form-group">
              <label htmlFor="industry">Industry</label>
              <input
                id="industry"
                name="industry"
                type="text"
                value={formData.industry}
                onChange={handleChange}
                disabled={saving || loading}
                placeholder="Research"
              />
            </div>

            <div className="form-group">
              <label htmlFor="organization_type">Organization Type</label>
              <input
                id="organization_type"
                name="organization_type"
                type="text"
                value={formData.organization_type}
                onChange={handleChange}
                disabled={saving || loading}
                placeholder="Non-profit"
              />
            </div>

            <div className="form-group">
              <label htmlFor="contact_email">Contact Email</label>
              <input
                id="contact_email"
                name="contact_email"
                type="email"
                value={formData.contact_email}
                onChange={handleChange}
                disabled={saving || loading}
                placeholder="you@example.com"
              />
            </div>

            <div className="form-group">
              <label htmlFor="contact_phone">Contact Phone</label>
              <input
                id="contact_phone"
                name="contact_phone"
                type="text"
                value={formData.contact_phone}
                onChange={handleChange}
                disabled={saving || loading}
                placeholder="+1-555-0100"
              />
            </div>

            <div className="form-group">
              <label htmlFor="country">Country</label>
              <input
                id="country"
                name="country"
                type="text"
                value={formData.country}
                onChange={handleChange}
                disabled={saving || loading}
                placeholder="United States"
              />
            </div>

            <div className="form-group">
              <label htmlFor="region">Region / State</label>
              <input
                id="region"
                name="region"
                type="text"
                value={formData.region}
                onChange={handleChange}
                disabled={saving || loading}
                placeholder="California"
              />
            </div>

            <div className="form-group">
              <label htmlFor="city">City</label>
              <input
                id="city"
                name="city"
                type="text"
                value={formData.city}
                onChange={handleChange}
                disabled={saving || loading}
                placeholder="San Francisco"
              />
            </div>

            <div className="form-group">
              <label htmlFor="address">Address</label>
              <input
                id="address"
                name="address"
                type="text"
                value={formData.address}
                onChange={handleChange}
                disabled={saving || loading}
                placeholder="123 Market St"
              />
            </div>

            <div className="form-group full">
              <label htmlFor="use_case_focus">Use Case Focus</label>
              <textarea
                id="use_case_focus"
                name="use_case_focus"
                rows={3}
                value={formData.use_case_focus}
                onChange={handleChange}
                disabled={saving || loading}
                placeholder="Describe the key datasets or insights you're looking for"
              />
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="primary" disabled={saving || loading}>
              {saving ? 'Saving...' : profile ? 'Update Profile' : 'Create Profile'}
            </button>
            {profile && (
              <button type="button" className="secondary" onClick={loadProfile} disabled={saving || loading}>
                Reset
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  )
}

