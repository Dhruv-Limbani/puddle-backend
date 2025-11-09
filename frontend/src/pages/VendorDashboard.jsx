import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { vendorService } from '../services/vendorService'
import { datasetService } from '../services/datasetService'
import { agentService } from '../services/agentService'
import DatasetManager from '../components/DatasetManager'
import AgentManager from '../components/AgentManager'
import './VendorDashboard.css'

const EMPTY_VENDOR_FORM = {
  name: '',
  industry_focus: '',
  description: '',
  contact_email: '',
  contact_phone: '',
  website_url: '',
  logo_url: '',
  country: '',
  region: '',
  city: '',
  address: '',
  organization_type: '',
  founded_year: '',
}

export default function VendorDashboard() {
  const { user, token, logout } = useAuth()
  const navigate = useNavigate()

  const [vendorList, setVendorList] = useState([])
  const [vendorProfile, setVendorProfile] = useState(null)
  const [datasets, setDatasets] = useState([])
  const [agents, setAgents] = useState([])
  const [formData, setFormData] = useState(EMPTY_VENDOR_FORM)

  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const isVendorOrAdmin = useMemo(
    () => user?.role === 'vendor' || user?.role === 'admin',
    [user?.role],
  )

  useEffect(() => {
    if (!token) {
      navigate('/login')
      return
    }

    if (!isVendorOrAdmin) {
      navigate('/dashboard')
      return
    }

    loadVendorData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, user?.id])

  const loadVendorData = async () => {
    setLoading(true)
    setError('')
    setMessage('')

    try {
      const vendors = await vendorService.list(token)
      setVendorList(vendors)
      const ownVendor = vendors.find((item) => item.user_id === user?.id) || null
      setVendorProfile(ownVendor)

      if (ownVendor) {
        setFormData({
          ...EMPTY_VENDOR_FORM,
          ...Object.fromEntries(
            Object.entries(ownVendor).filter(([key]) => key in EMPTY_VENDOR_FORM),
          ),
          founded_year: ownVendor.founded_year ? String(ownVendor.founded_year) : '',
        })

        const [allDatasets, vendorAgents] = await Promise.all([
          datasetService.list(token, { limit: 200 }),
          agentService.list(token, { vendorId: ownVendor.id }),
        ])

        setDatasets(allDatasets.filter((dataset) => dataset.vendor_id === ownVendor.id))
        setAgents(vendorAgents)
      } else {
        setFormData(EMPTY_VENDOR_FORM)
        setDatasets([])
        setAgents([])
      }
    } catch (err) {
      setError(err.message || 'Failed to load vendor information')
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (event) => {
    const { name, value } = event.target
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'founded_year' ? value.replace(/[^0-9]/g, '') : value,
    }))
  }

  const preparePayload = () => {
    const payload = {}

    Object.entries(formData).forEach(([key, value]) => {
      if (value === '') {
        return
      }

      if (key === 'founded_year') {
        const year = parseInt(value, 10)
        if (!Number.isNaN(year)) {
          payload[key] = year
        }
        return
      }

      payload[key] = value
    })

    return payload
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setSaving(true)
    setMessage('')
    setError('')

    const payload = preparePayload()

    if (!payload.name) {
      setError('Vendor name is required')
      setSaving(false)
      return
    }

    try {
      if (vendorProfile) {
        await vendorService.update(token, vendorProfile.id, payload)
        setMessage('Vendor profile updated successfully')
      } else {
        await vendorService.create(token, payload)
        setMessage('Vendor profile created successfully')
      }

      await loadVendorData()
    } catch (err) {
      setError(err.message || 'Failed to save vendor profile')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!vendorProfile) return
    if (!window.confirm('Delete your vendor profile? This cannot be undone.')) {
      return
    }

    setDeleting(true)
    setMessage('')
    setError('')

    try {
      await vendorService.remove(token, vendorProfile.id)
      setMessage('Vendor profile deleted')
      setVendorProfile(null)
      setDatasets([])
      setAgents([])
      setFormData(EMPTY_VENDOR_FORM)
      await loadVendorData()
    } catch (err) {
      setError(err.message || 'Failed to delete vendor profile')
    } finally {
      setDeleting(false)
    }
  }

  const handleRefresh = () => {
    loadVendorData()
  }

  const myVendorName = vendorProfile?.name || 'Your Vendor Profile'

  return (
    <div className="vendor-dashboard">
      <header className="vendor-dashboard__top">
        <div>
          <h1>{myVendorName}</h1>
          <p className="vendor-dashboard__subtitle">
            Manage your vendor presence, datasets, and AI agents
          </p>
        </div>
        <div className="vendor-dashboard__actions">
          <button className="secondary" onClick={handleRefresh} disabled={loading}>
            Refresh
          </button>
          <button className="secondary" onClick={() => navigate('/dashboard')}>
            Back to Account
          </button>
          <button className="danger" onClick={logout}>
            Logout
          </button>
        </div>
      </header>

      {(message || error) && (
        <div className="vendor-dashboard__alerts">
          {message && <div className="success">{message}</div>}
          {error && <div className="error">{error}</div>}
        </div>
      )}

      <section className="vendor-dashboard__panel">
        <div className="panel-header">
          <h2>{vendorProfile ? 'Update Vendor Profile' : 'Create Vendor Profile'}</h2>
          <p>Share your brand story so buyers can find and trust you.</p>
        </div>

        <form className="vendor-form" onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="form-group full">
              <label htmlFor="name">
                Vendor Name <span>*</span>
              </label>
              <input
                id="name"
                name="name"
                type="text"
                required
                value={formData.name}
                onChange={handleInputChange}
                disabled={saving || loading}
                placeholder="Example Data Corp"
              />
            </div>

            <div className="form-group">
              <label htmlFor="industry_focus">Industry Focus</label>
              <input
                id="industry_focus"
                name="industry_focus"
                type="text"
                value={formData.industry_focus}
                onChange={handleInputChange}
                disabled={saving || loading}
                placeholder="Finance, Healthcare, Retail..."
              />
            </div>

            <div className="form-group">
              <label htmlFor="organization_type">Organization Type</label>
              <input
                id="organization_type"
                name="organization_type"
                type="text"
                value={formData.organization_type}
                onChange={handleInputChange}
                disabled={saving || loading}
                placeholder="Private Company, Non-profit..."
              />
            </div>

            <div className="form-group">
              <label htmlFor="founded_year">Founded Year</label>
              <input
                id="founded_year"
                name="founded_year"
                type="text"
                inputMode="numeric"
                value={formData.founded_year}
                onChange={handleInputChange}
                disabled={saving || loading}
                placeholder="2022"
                maxLength={4}
              />
            </div>

            <div className="form-group full">
              <label htmlFor="description">Description</label>
              <textarea
                id="description"
                name="description"
                rows={3}
                value={formData.description}
                onChange={handleInputChange}
                disabled={saving || loading}
                placeholder="Tell buyers about your datasets and strengths"
              />
            </div>

            <div className="form-group">
              <label htmlFor="contact_email">Contact Email</label>
              <input
                id="contact_email"
                name="contact_email"
                type="email"
                value={formData.contact_email}
                onChange={handleInputChange}
                disabled={saving || loading}
                placeholder="data@example.com"
              />
            </div>

            <div className="form-group">
              <label htmlFor="contact_phone">Contact Phone</label>
              <input
                id="contact_phone"
                name="contact_phone"
                type="text"
                value={formData.contact_phone}
                onChange={handleInputChange}
                disabled={saving || loading}
                placeholder="+1-555-0100"
              />
            </div>

            <div className="form-group">
              <label htmlFor="website_url">Website URL</label>
              <input
                id="website_url"
                name="website_url"
                type="url"
                value={formData.website_url}
                onChange={handleInputChange}
                disabled={saving || loading}
                placeholder="https://example.com"
              />
            </div>

            <div className="form-group">
              <label htmlFor="logo_url">Logo URL</label>
              <input
                id="logo_url"
                name="logo_url"
                type="url"
                value={formData.logo_url}
                onChange={handleInputChange}
                disabled={saving || loading}
                placeholder="https://example.com/logo.png"
              />
            </div>

            <div className="form-group">
              <label htmlFor="country">Country</label>
              <input
                id="country"
                name="country"
                type="text"
                value={formData.country}
                onChange={handleInputChange}
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
                onChange={handleInputChange}
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
                onChange={handleInputChange}
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
                onChange={handleInputChange}
                disabled={saving || loading}
                placeholder="123 Market St"
              />
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="primary" disabled={saving || loading}>
              {saving ? 'Saving...' : vendorProfile ? 'Update Profile' : 'Create Profile'}
            </button>
            {vendorProfile && (
              <button
                type="button"
                className="danger"
                disabled={deleting || loading}
                onClick={handleDelete}
              >
                {deleting ? 'Deleting...' : 'Delete Profile'}
              </button>
            )}
          </div>
        </form>
      </section>

      <div className="vendor-dashboard__grid">
        <section className="vendor-dashboard__panel">
          {loading && !vendorProfile ? (
            <div className="panel-empty">Loading datasets...</div>
          ) : (
            <DatasetManager
              token={token}
              vendorProfile={vendorProfile}
              datasets={datasets}
              onRefresh={loadVendorData}
            />
          )}
        </section>

        <section className="vendor-dashboard__panel">
          {loading && !vendorProfile ? (
            <div className="panel-empty">Loading agents...</div>
          ) : (
            <AgentManager
              token={token}
              vendorProfile={vendorProfile}
              agents={agents}
              onRefresh={loadVendorData}
            />
          )}
        </section>
      </div>

      <section className="vendor-dashboard__panel">
        <div className="panel-header">
          <h2>Marketplace Vendors</h2>
          <p>Explore other vendors to understand positioning and offerings.</p>
        </div>

        {loading ? (
          <div className="panel-empty">Loading vendors...</div>
        ) : vendorList.length === 0 ? (
          <div className="panel-empty">No vendors found.</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Industry</th>
                <th>Location</th>
                <th>Contact</th>
              </tr>
            </thead>
            <tbody>
              {vendorList.map((vendor) => (
                <tr key={vendor.id} className={vendor.id === vendorProfile?.id ? 'highlight' : ''}>
                  <td>{vendor.name}</td>
                  <td>{vendor.industry_focus || '—'}</td>
                  <td>
                    {[vendor.city, vendor.region, vendor.country]
                      .filter(Boolean)
                      .join(', ') || '—'}
                  </td>
                  <td>{vendor.contact_email || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  )
}
