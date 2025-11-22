import React, { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { datasetService } from '../services/datasetService'
import { vendorService } from '../services/vendorService'
import { useNavigate } from 'react-router-dom'

// Props:
// - datasetId: id to load
// - onBack: optional callback to return to list (keeps navigation internal)
// - onOpenVendor: optional callback to open vendor profile internally
export default function DatasetProfile({ datasetId, onBack, onOpenVendor }) {
  const { token } = useAuth()
  const navigate = useNavigate()
  const [dataset, setDataset] = useState(null)
  const [vendor, setVendor] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      setError('')
      try {
        // Try public endpoint first, fallback to private if needed
        let ds = null
        try {
          ds = await datasetService.get(token, datasetId, { public: true })
        } catch (err) {
          // If forbidden, try private endpoint (for owner/admin)
          if (err.message && err.message.includes('Dataset is not public')) {
            ds = await datasetService.get(token, datasetId)
          } else {
            throw err
          }
        }
        setDataset(ds)
        // Try to fetch vendor if vendor_id present
        if (ds.vendor_id) {
          try {
            const v = await vendorService.get(token, ds.vendor_id)
            setVendor(v)
          } catch (_) {
            setVendor(null)
          }
        }
      } catch (err) {
        setError(err.message || 'Failed to load dataset')
      } finally {
        setLoading(false)
      }
    }

    load()
  }, [token, datasetId])

  if (loading) {
    return (
      <div className="loading-state">
        <div className="loading-spinner"></div>
        <p>Loading dataset details...</p>
      </div>
    )
  }

  if (error) return <div className="alert alert-error">{error}</div>
  if (!dataset) return <div className="marketplace-empty">Dataset not found.</div>

  return (
    <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Back Button */}
      <button
        onClick={() => {
            if (onBack) {
                onBack()
            } else {
                navigate(-1)
            }
        }}
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
              {dataset.title}
            </h1>
            <span className={`badge visibility-${dataset.visibility || 'public'}`}>
              {dataset.visibility}
            </span>
          </div>
          <p style={{ fontSize: '16px', color: 'var(--primary-700)', margin: '8px 0 0 0', lineHeight: 1.6 }}>
            {dataset.description || 'No description provided.'}
          </p>
        </div>

        {/* Metadata Section */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '24px', marginBottom: '20px' }}>
          <div>
            <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--primary-600)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '4px' }}>Domain</div>
            <div style={{ fontSize: '15px', fontWeight: 600, color: 'var(--primary-900)' }}>{dataset.domain || 'General'}</div>
          </div>
          <div>
            <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--primary-600)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '4px' }}>Type</div>
            <div style={{ fontSize: '15px', fontWeight: 600, color: 'var(--primary-900)' }}>{dataset.dataset_type || 'N/A'}</div>
          </div>
          <div>
            <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--primary-600)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '4px' }}>Pricing</div>
            <div style={{ fontSize: '15px', fontWeight: 600, color: 'var(--primary-900)' }}>{dataset.pricing_model || 'Pricing TBD'}</div>
          </div>
        </div>

        {/* Topics */}
        {Array.isArray(dataset.topics) && dataset.topics.length > 0 && (
          <div style={{ marginBottom: '28px' }}>
            <div className="chip-row">
              {dataset.topics.map((t) => (
                <span key={t} className="chip">{t}</span>
              ))}
            </div>
          </div>
        )}

        {/* Columns Section */}
        {dataset.columns && dataset.columns.length > 0 && (
          <div style={{ marginBottom: '28px' }}>
            <h3 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--primary-900)', marginBottom: '16px' }}>Columns</h3>
            <div style={{ background: 'white', borderRadius: '12px', border: '1px solid var(--accent-100)', overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ background: 'var(--accent-50)' }}>
                    <th style={{ padding: '14px 20px', textAlign: 'left', fontSize: '13px', fontWeight: 700, color: 'var(--primary-900)', textTransform: 'uppercase', letterSpacing: '0.05em', borderBottom: '1px solid var(--accent-100)' }}>Column Name</th>
                    <th style={{ padding: '14px 20px', textAlign: 'left', fontSize: '13px', fontWeight: 700, color: 'var(--primary-900)', textTransform: 'uppercase', letterSpacing: '0.05em', borderBottom: '1px solid var(--accent-100)' }}>Data Type</th>
                    <th style={{ padding: '14px 20px', textAlign: 'left', fontSize: '13px', fontWeight: 700, color: 'var(--primary-900)', textTransform: 'uppercase', letterSpacing: '0.05em', borderBottom: '1px solid var(--accent-100)' }}>Description</th>
                  </tr>
                </thead>
                <tbody>
                  {dataset.columns.map((c, idx) => (
                    <tr key={c.name || c.id} style={{ background: idx % 2 === 0 ? 'white' : 'var(--accent-50)' }}>
                      <td style={{ padding: '14px 20px', fontSize: '14px', fontWeight: 600, color: 'var(--primary-900)', borderBottom: idx < dataset.columns.length - 1 ? '1px solid var(--accent-100)' : 'none' }}>{c.name}</td>
                      <td style={{ padding: '14px 20px', fontSize: '14px', fontWeight: 500, color: '#0077B6', borderBottom: idx < dataset.columns.length - 1 ? '1px solid var(--accent-100)' : 'none' }}>{c.data_type || 'string'}</td>
                      <td style={{ padding: '14px 20px', fontSize: '14px', color: 'var(--primary-700)', borderBottom: idx < dataset.columns.length - 1 ? '1px solid var(--accent-100)' : 'none' }}>{c.description || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Temporal Coverage */}
        {dataset.temporal_coverage && (
          <div style={{ marginBottom: '28px' }}>
            <h3 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--primary-900)', marginBottom: '16px' }}>Temporal Coverage</h3>
            <div style={{ background: 'var(--accent-50)', borderRadius: '12px', padding: '16px', border: '1px solid var(--accent-100)', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ fontSize: '14px' }}>
                <span style={{ fontWeight: 600, color: 'var(--primary-900)' }}>Start:</span>
                <span style={{ color: 'var(--primary-700)', marginLeft: '8px' }}>{dataset.temporal_coverage.start_date || '—'}</span>
              </div>
              <div style={{ fontSize: '14px' }}>
                <span style={{ fontWeight: 600, color: 'var(--primary-900)' }}>End:</span>
                <span style={{ color: 'var(--primary-700)', marginLeft: '8px' }}>{dataset.temporal_coverage.end_date || '—'}</span>
              </div>
              <div style={{ fontSize: '14px' }}>
                <span style={{ fontWeight: 600, color: 'var(--primary-900)' }}>Frequency:</span>
                <span style={{ color: 'var(--primary-700)', marginLeft: '8px' }}>{dataset.temporal_coverage.frequency || '—'}</span>
              </div>
            </div>
          </div>
        )}

        {/* Geographic Coverage */}
        {dataset.geographic_coverage && (
          <div style={{ marginBottom: '28px' }}>
            <h3 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--primary-900)', marginBottom: '16px' }}>Geographic Coverage</h3>
            <div style={{ background: 'var(--accent-50)', borderRadius: '12px', padding: '16px', border: '1px solid var(--accent-100)', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {Array.isArray(dataset.geographic_coverage.countries) && dataset.geographic_coverage.countries.length > 0 && (
                <div style={{ fontSize: '14px' }}>
                  <span style={{ fontWeight: 600, color: 'var(--primary-900)' }}>Countries:</span>
                  <span style={{ color: 'var(--primary-700)', marginLeft: '8px' }}>{dataset.geographic_coverage.countries.join(', ')}</span>
                </div>
              )}
              {Array.isArray(dataset.geographic_coverage.regions) && dataset.geographic_coverage.regions.length > 0 && (
                <div style={{ fontSize: '14px' }}>
                  <span style={{ fontWeight: 600, color: 'var(--primary-900)' }}>Regions:</span>
                  <span style={{ color: 'var(--primary-700)', marginLeft: '8px' }}>{dataset.geographic_coverage.regions.join(', ')}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Provider Section */}
        <div>
          <h3 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--primary-900)', marginBottom: '16px' }}>Provider</h3>
          {vendor ? (
            <div
              onClick={() => {
                if (typeof onOpenVendor === 'function') onOpenVendor(vendor.id)
                else navigate(`/marketplace/vendor/${vendor.id}`)
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
              <div style={{ fontWeight: 700, fontSize: '17px', color: 'var(--primary-900)', marginBottom: '8px' }}>{vendor.name}</div>
              <div style={{ fontSize: '14px', color: 'var(--primary-700)', lineHeight: 1.6 }}>{vendor.description}</div>
            </div>
          ) : (
            <div style={{ fontSize: '14px', color: 'var(--primary-700)' }}>
              {dataset.vendor_id ? `Provider ID: ${dataset.vendor_id}` : 'Independent Dataset'}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
