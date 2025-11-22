import { useEffect, useMemo, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { datasetService } from '../services/datasetService'
import { vendorService } from '../services/vendorService'
import DatasetProfile from './DatasetProfile'
import PublicVendorProfile from './PublicVendorProfile'
import './Marketplace.css'

export default function Marketplace() {
  const { token } = useAuth()
  const [datasets, setDatasets] = useState([])
  const [vendors, setVendors] = useState([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  // Local navigation state
  const [view, setView] = useState({ type: 'list', id: null })

  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      setError('')
      try {
        const [ds, vs] = await Promise.all([
          datasetService.list(token, { limit: 200 }),
          vendorService.list(token),
        ])
        setDatasets(ds)
        setVendors(vs)
      } catch (err) {
        setError(err.message || 'Failed to load marketplace data')
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [token])

  const filteredDatasets = useMemo(() => {
    if (!search.trim()) return datasets
    const term = search.toLowerCase()
    return datasets.filter(
      (ds) =>
        ds.title?.toLowerCase().includes(term) ||
        ds.description?.toLowerCase().includes(term) ||
        (Array.isArray(ds.topics) && ds.topics.join(' ').toLowerCase().includes(term)),
    )
  }, [datasets, search])

  const filteredVendors = useMemo(() => {
    if (!search.trim()) return vendors
    const term = search.toLowerCase()
    return vendors.filter(
      (vendor) =>
        vendor.name?.toLowerCase().includes(term) ||
        vendor.description?.toLowerCase().includes(term) ||
        vendor.industry_focus?.toLowerCase().includes(term),
    )
  }, [vendors, search])

  // Local navigation logic
  if (view.type === 'dataset') {
    return (
      <div className="marketplace-tab">
        <DatasetProfile
          datasetId={view.id}
          onBack={() => setView({ type: 'list', id: null })}
          onOpenVendor={(vendorId) => setView({ type: 'vendor', id: vendorId })}
        />
      </div>
    )
  }
  if (view.type === 'vendor') {
    return (
      <div className="marketplace-tab">
        <PublicVendorProfile
          vendorId={view.id}
          onBack={() => setView({ type: 'list', id: null })}
          onOpenDataset={(datasetId) => setView({ type: 'dataset', id: datasetId })}
        />
      </div>
    )
  }

  // Default: show marketplace list
  return (
    <div className="marketplace-tab">
      <input
        className="search-input"
        type="text"
        placeholder="Search datasets or vendors..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      {loading ? (
        <div className="marketplace-loading">Loading marketplace data...</div>
      ) : error ? (
        <div className="marketplace-error">{error}</div>
      ) : (
        <>
          <section className="marketplace-section">
            <div className="section-header">
              <h2>Datasets</h2>
              <span className="results-count">
                {filteredDatasets.length} {filteredDatasets.length === 1 ? 'dataset' : 'datasets'}
              </span>
            </div>
            {filteredDatasets.length === 0 ? (
              <div className="marketplace-empty">
                {search ? 'No datasets match your search.' : 'No datasets available.'}
              </div>
            ) : (
              <div className="dataset-grid">
                {filteredDatasets.map((dataset) => (
                  <article
                    key={dataset.id}
                    className="dataset-card"
                    role="button"
                    tabIndex={0}
                    onClick={() => setView({ type: 'dataset', id: dataset.id })}
                    onKeyDown={(e) => { if (e.key === 'Enter') setView({ type: 'dataset', id: dataset.id }) }}
                    style={{ cursor: 'pointer' }}
                  >
                    <div className="dataset-card-header">
                      <h3>{dataset.title}</h3>
                      <span className={`badge visibility-${dataset.visibility || 'public'}`}>
                        {dataset.visibility}
                      </span>
                    </div>
                    <p className="dataset-description">{dataset.description || 'No description provided.'}</p>
                    <div className="dataset-meta">
                      <span>{dataset.domain || 'General'}</span>
                      <span>{dataset.dataset_type || 'N/A'}</span>
                      <span>{dataset.pricing_model || 'Pricing TBD'}</span>
                    </div>
                    {Array.isArray(dataset.topics) && dataset.topics.length > 0 && (
                      <div className="chip-row">
                        {dataset.topics.slice(0, 4).map((topic) => (
                          <span key={topic} className="chip">
                            {topic}
                          </span>
                        ))}
                        {dataset.topics.length > 4 && (
                          <span className="chip">+{dataset.topics.length - 4} more</span>
                        )}
                      </div>
                    )}
                  </article>
                ))}
              </div>
            )}
          </section>

          <section className="marketplace-section">
            <div className="section-header">
              <h2>Vendors</h2>
              <span className="results-count">
                {filteredVendors.length} {filteredVendors.length === 1 ? 'vendor' : 'vendors'}
              </span>
            </div>
            {filteredVendors.length === 0 ? (
              <div className="marketplace-empty">
                {search ? 'No vendors match your search.' : 'No vendors available.'}
              </div>
            ) : (
              <div className="vendor-grid">
                {filteredVendors.map((vendor) => (
                  <article
                    key={vendor.id}
                    className="vendor-card"
                    role="button"
                    tabIndex={0}
                    onClick={() => setView({ type: 'vendor', id: vendor.id })}
                    onKeyDown={(e) => { if (e.key === 'Enter') setView({ type: 'vendor', id: vendor.id }) }}
                    style={{ cursor: 'pointer' }}
                  >
                    <h3>{vendor.name}</h3>
                    <p className="vendor-description">{vendor.description || 'No description provided.'}</p>
                    <div className="vendor-meta">
                      <span>{vendor.industry_focus || 'Industry agnostic'}</span>
                      <span>{vendor.country || 'Global'}</span>
                    </div>
                    <div className="vendor-contact">
                      {vendor.contact_email && (
                        <span>📧 {vendor.contact_email}</span>
                      )}
                      {vendor.website_url && (
                        <a href={vendor.website_url} target="_blank" rel="noreferrer">
                          🌐 Visit Website
                        </a>
                      )}
                    </div>
                  </article>
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </div>
  )
}