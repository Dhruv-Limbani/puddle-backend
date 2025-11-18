import React, { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { vendorService } from '../services/vendorService'
import { datasetService } from '../services/datasetService'
import { useNavigate } from 'react-router-dom'

// Props:
// - vendorId: id to load
// - onBack: optional callback used to return to marketplace list
// - onOpenDataset: optional callback to open a dataset profile internally
export default function PublicVendorProfile({ vendorId, onBack, onOpenDataset }) {
  const { token } = useAuth()
  const navigate = useNavigate()
  const [vendor, setVendor] = useState(null)
  const [datasets, setDatasets] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      setError('')
      try {
        const v = await vendorService.get(token, vendorId)
        setVendor(v)
        const all = await datasetService.list(token, { limit: 200 })
        const own = Array.isArray(all) ? all.filter(d => String(d.vendor_id) === String(v.id)) : []
        setDatasets(own)
      } catch (err) {
        setError(err.message || 'Failed to load vendor profile')
      } finally {
        setLoading(false)
      }
    }

    load()
  }, [token, vendorId])

  if (loading) {
    return (
      <div className="loading-state">
        <div className="loading-spinner"></div>
        <p>Loading vendor profile...</p>
      </div>
    )
  }

  if (error) return <div className="alert alert-error">{error}</div>
  if (!vendor) return <div className="marketplace-empty">Vendor not found.</div>

  return (
    <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Back Button */}
      <button
        onClick={onBack}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: '40px',
          height: '40px',
          background: '#0077B6',
          border: 'none',
          borderRadius: '50%',
          color: 'white',
          fontSize: '18px',
          fontWeight: 600,
          cursor: 'pointer',
          transition: 'all 0.2s ease',
          boxShadow: '0 2px 8px rgba(0, 119, 182, 0.2)'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = '#005A8D'
          e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 119, 182, 0.3)'
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = '#0077B6'
          e.currentTarget.style.boxShadow = '0 2px 8px rgba(0, 119, 182, 0.2)'
        }}
        title="Back to Marketplace"
      >
        ←
      </button>

      {/* Main Profile Card */}
      <div style={{
        background: 'var(--bg-light)',
        borderRadius: '20px',
        padding: '32px',
        boxShadow: '0 10px 40px rgba(3, 4, 94, 0.08)',
        border: '1px solid rgba(202, 240, 248, 0.5)'
      }}>
        {/* Header Section */}
        <div style={{ marginBottom: '24px', paddingBottom: '24px', borderBottom: '1px solid var(--accent-100)' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '16px', marginBottom: '12px' }}>
            <h1 style={{ fontSize: '32px', fontWeight: 700, color: 'var(--primary-900)', margin: 0, lineHeight: 1.2 }}>
              {vendor.name}
            </h1>
          </div>
          <div style={{ display: 'flex', gap: '12px', marginBottom: '16px', flexWrap: 'wrap' }}>
            <span className="chip" style={{ background: '#e0e7ff', color: '#3730a3' }}>{vendor.industry_focus || 'Industry agnostic'}</span>
            <span className="chip" style={{ background: '#ecfccb', color: '#3f6212' }}>{vendor.country || 'Global'}</span>
          </div>
          {vendor.logo_url && (
            <div style={{ marginBottom: '16px' }}>
              <img src={vendor.logo_url} alt={`${vendor.name} logo`} style={{ maxHeight: 80, borderRadius: 8, border: '1px solid var(--accent-100)' }} />
            </div>
          )}
          <p style={{ fontSize: '16px', color: 'var(--primary-700)', margin: 0, lineHeight: 1.6 }}>
            {vendor.description || 'No description provided.'}
          </p>
        </div>

        {/* Contact Section */}
        <div style={{ marginBottom: '28px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--primary-900)', marginBottom: '16px' }}>Contact</h3>
          <div style={{
            background: 'var(--accent-50)',
            borderRadius: '12px',
            padding: '16px',
            border: '1px solid var(--accent-100)',
            display: 'flex',
            flexWrap: 'wrap',
            gap: '16px',
            fontSize: '14px'
          }}>
            {vendor.contact_email && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span>📧</span>
                <span style={{ color: 'var(--primary-700)' }}>{vendor.contact_email}</span>
              </div>
            )}
            {vendor.contact_phone && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span>📞</span>
                <span style={{ color: 'var(--primary-700)' }}>{vendor.contact_phone}</span>
              </div>
            )}
            {vendor.website_url && (
              <a
                href={vendor.website_url}
                target="_blank"
                rel="noreferrer"
                style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#0077B6', fontWeight: 500, textDecoration: 'none' }}
              >
                <span>🌐</span>
                <span>Visit Website</span>
              </a>
            )}
          </div>
        </div>

        {/* Datasets Section */}
        <div>
          <h3 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--primary-900)', marginBottom: '16px' }}>Datasets from this vendor</h3>
          {datasets.length === 0 ? (
            <div style={{
              background: 'var(--accent-50)',
              border: '1px dashed var(--accent-200)',
              borderRadius: '12px',
              padding: '32px 20px',
              textAlign: 'center',
              color: 'var(--primary-700)',
              fontSize: '15px'
            }}>
              No datasets published by this vendor.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {datasets.map((ds) => (
                <div
                  key={ds.id}
                  onClick={() => {
                    if (typeof onOpenDataset === 'function') onOpenDataset(ds.id)
                    else navigate(`/marketplace/dataset/${ds.id}`)
                  }}
                  style={{
                    background: 'var(--accent-50)',
                    borderRadius: '12px',
                    padding: '20px',
                    cursor: 'pointer',
                    border: '1px solid var(--accent-100)',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = 'var(--primary-600)'
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 119, 182, 0.15)'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = 'var(--accent-100)'
                    e.currentTarget.style.boxShadow = 'none'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px', marginBottom: '8px' }}>
                    <div style={{ fontWeight: 700, fontSize: '17px', color: 'var(--primary-900)' }}>{ds.title}</div>
                    <span className={`badge visibility-${ds.visibility || 'public'}`}>{ds.visibility}</span>
                  </div>
                  <div style={{ fontSize: '14px', color: 'var(--primary-700)', lineHeight: 1.6 }}>{ds.description}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
