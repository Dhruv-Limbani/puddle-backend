import { useEffect, useMemo, useState } from 'react'
import { datasetService } from '../services/datasetService'

const EMPTY_FORM = {
  title: '',
  description: '',
  domain: '',
  dataset_type: '',
  granularity: '',
  pricing_model: '',
  license: '',
  visibility: 'public',
  status: 'active',
  topics: '',
  entities: '',
}

function normalizeArrayField(value) {
  if (!value || !value.trim()) return undefined
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
}

function buildPayload(formState, vendorId) {
  const payload = { vendor_id: vendorId }

  Object.entries(formState).forEach(([key, value]) => {
    if (value === '' || value === null || value === undefined) {
      return
    }

    if (key === 'topics' || key === 'entities') {
      const arr = normalizeArrayField(value)
      if (arr && arr.length) {
        payload[key] = arr
      }
      return
    }

    payload[key] = value
  })

  return payload
}

export default function DatasetManager({ token, vendorProfile, datasets, onRefresh }) {
  const [formState, setFormState] = useState(EMPTY_FORM)
  const [editingId, setEditingId] = useState(null)
  const [saving, setSaving] = useState(false)
  const [deletingId, setDeletingId] = useState(null)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  const hasVendorProfile = useMemo(() => Boolean(vendorProfile?.id), [vendorProfile?.id])

  useEffect(() => {
    if (!editingId) {
      resetForm()
    }
  }, [editingId])

  useEffect(() => {
    if (!hasVendorProfile) {
      setFormState(EMPTY_FORM)
      setEditingId(null)
    }
  }, [hasVendorProfile])

  const resetForm = () => {
    setFormState(EMPTY_FORM)
    setEditingId(null)
  }

  const handleChange = (event) => {
    const { name, value } = event.target
    setFormState((prev) => ({ ...prev, [name]: value }))
  }

  const handleEdit = (dataset) => {
    setEditingId(dataset.id)
    setFormState({
      title: dataset.title || '',
      description: dataset.description || '',
      domain: dataset.domain || '',
      dataset_type: dataset.dataset_type || '',
      granularity: dataset.granularity || '',
      pricing_model: dataset.pricing_model || '',
      license: dataset.license || '',
      visibility: dataset.visibility || 'public',
      status: dataset.status || 'active',
      topics: Array.isArray(dataset.topics) ? dataset.topics.join(', ') : '',
      entities: Array.isArray(dataset.entities) ? dataset.entities.join(', ') : '',
    })
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!hasVendorProfile) {
      setError('Create your vendor profile before managing datasets.')
      return
    }

    if (!formState.title.trim()) {
      setError('Dataset title is required')
      return
    }

    setSaving(true)
    setError('')
    setMessage('')

    try {
      const payload = buildPayload(formState, vendorProfile.id)
      if (editingId) {
        await datasetService.update(token, editingId, payload)
        setMessage('Dataset updated successfully')
      } else {
        await datasetService.create(token, payload)
        setMessage('Dataset created successfully')
      }

      resetForm()
      await onRefresh?.()
    } catch (err) {
      setError(err.message || 'Failed to save dataset')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (datasetId) => {
    if (!window.confirm('Delete this dataset? This cannot be undone.')) return

    setDeletingId(datasetId)
    setError('')
    setMessage('')

    try {
      await datasetService.remove(token, datasetId)
      if (editingId === datasetId) {
        resetForm()
      }
      setMessage('Dataset deleted successfully')
      await onRefresh?.()
    } catch (err) {
      setError(err.message || 'Failed to delete dataset')
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="dataset-manager">
      <div className="panel-header">
        <h2>Your Datasets</h2>
        <p>Manage the datasets visible in the marketplace.</p>
      </div>

      {(message || error) && (
        <div className="dataset-alerts">
          {message && <div className="success">{message}</div>}
          {error && <div className="error">{error}</div>}
        </div>
      )}

      <form className="dataset-form" onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="form-group full">
            <label htmlFor="dataset-title">
              Dataset Title <span>*</span>
            </label>
            <input
              id="dataset-title"
              name="title"
              type="text"
              value={formState.title}
              onChange={handleChange}
              required
              disabled={saving || !hasVendorProfile}
              placeholder="Global E-commerce Transactions 2024"
            />
          </div>

          <div className="form-group full">
            <label htmlFor="dataset-description">Description</label>
            <textarea
              id="dataset-description"
              name="description"
              rows={3}
              value={formState.description}
              onChange={handleChange}
              disabled={saving || !hasVendorProfile}
              placeholder="High-level summary of the dataset's contents and value"
            />
          </div>

          <div className="form-group">
            <label htmlFor="domain">Domain</label>
            <input
              id="domain"
              name="domain"
              type="text"
              value={formState.domain}
              onChange={handleChange}
              disabled={saving || !hasVendorProfile}
              placeholder="Finance, Healthcare, Retail..."
            />
          </div>

          <div className="form-group">
            <label htmlFor="dataset_type">Dataset Type</label>
            <input
              id="dataset_type"
              name="dataset_type"
              type="text"
              value={formState.dataset_type}
              onChange={handleChange}
              disabled={saving || !hasVendorProfile}
              placeholder="Transactional, Time-series..."
            />
          </div>

          <div className="form-group">
            <label htmlFor="granularity">Granularity</label>
            <input
              id="granularity"
              name="granularity"
              type="text"
              value={formState.granularity}
              onChange={handleChange}
              disabled={saving || !hasVendorProfile}
              placeholder="Transaction-level, Daily, Monthly..."
            />
          </div>

          <div className="form-group">
            <label htmlFor="pricing_model">Pricing Model</label>
            <input
              id="pricing_model"
              name="pricing_model"
              type="text"
              value={formState.pricing_model}
              onChange={handleChange}
              disabled={saving || !hasVendorProfile}
              placeholder="Subscription, One-time, Usage-based"
            />
          </div>

          <div className="form-group">
            <label htmlFor="license">License</label>
            <input
              id="license"
              name="license"
              type="text"
              value={formState.license}
              onChange={handleChange}
              disabled={saving || !hasVendorProfile}
              placeholder="Commercial Use Allowed"
            />
          </div>

          <div className="form-group">
            <label htmlFor="visibility">Visibility</label>
            <select
              id="visibility"
              name="visibility"
              value={formState.visibility}
              onChange={handleChange}
              disabled={saving || !hasVendorProfile}
            >
              <option value="public">Public</option>
              <option value="private">Private</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="status">Status</label>
            <select
              id="status"
              name="status"
              value={formState.status}
              onChange={handleChange}
              disabled={saving || !hasVendorProfile}
            >
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="draft">Draft</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="topics">Topics (comma separated)</label>
            <input
              id="topics"
              name="topics"
              type="text"
              value={formState.topics}
              onChange={handleChange}
              disabled={saving || !hasVendorProfile}
              placeholder="e-commerce, retail, consumer behavior"
            />
          </div>

          <div className="form-group">
            <label htmlFor="entities">Entities (comma separated)</label>
            <input
              id="entities"
              name="entities"
              type="text"
              value={formState.entities}
              onChange={handleChange}
              disabled={saving || !hasVendorProfile}
              placeholder="transactions, products, customers"
            />
          </div>
        </div>

        <div className="form-actions">
          <button type="submit" className="primary" disabled={saving || !hasVendorProfile}>
            {saving ? 'Saving...' : editingId ? 'Update Dataset' : 'Create Dataset'}
          </button>
          {editingId && (
            <button type="button" className="secondary" onClick={resetForm} disabled={saving}>
              Cancel
            </button>
          )}
        </div>
      </form>

      {datasets.length === 0 ? (
        <div className="panel-empty dataset-empty">
          {hasVendorProfile
            ? 'No datasets yet. Use the form above to publish your first dataset.'
            : 'Create your vendor profile to start adding datasets.'}
        </div>
      ) : (
        <table className="data-table dataset-table">
          <thead>
            <tr>
              <th>Title</th>
              <th>Status</th>
              <th>Visibility</th>
              <th>Updated</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {datasets.map((dataset) => (
              <tr key={dataset.id}>
                <td>{dataset.title}</td>
                <td>
                  <span className={`badge status-${dataset.status || 'unknown'}`}>
                    {dataset.status || 'unknown'}
                  </span>
                </td>
                <td>
                  <span className={`badge visibility-${dataset.visibility || 'public'}`}>
                    {dataset.visibility || 'public'}
                  </span>
                </td>
                <td>{dataset.updated_at ? new Date(dataset.updated_at).toLocaleDateString() : '—'}</td>
                <td>
                  <div className="dataset-actions">
                    <button
                      type="button"
                      className="text-button"
                      onClick={() => handleEdit(dataset)}
                      disabled={saving}
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      className="text-button danger-text"
                      onClick={() => handleDelete(dataset.id)}
                      disabled={deletingId === dataset.id}
                    >
                      {deletingId === dataset.id ? 'Deleting...' : 'Delete'}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
