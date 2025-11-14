import { useEffect, useMemo, useState } from 'react'
import { datasetService } from '../services/datasetService'

const EMPTY_COLUMN = {
  name: '',
  description: '',
  data_type: '',
  sample_values: '',
}

const createEmptyForm = () => ({
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
  temporalCoverage: '',
  geographicCoverage: '',
  columns: [{ ...EMPTY_COLUMN }],
})

function normalizeArrayField(value) {
  if (!value || !value.trim()) return undefined
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
}

function parseSampleValues(value) {
  if (!value || !value.trim()) return undefined
  try {
    return JSON.parse(value)
  } catch (err) {
    return value
  }
}

function buildPayload(formState, vendorId, extras = {}) {
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

    if (key === 'temporalCoverage' || key === 'geographicCoverage' || key === 'columns') {
      return
    }

    payload[key] = value
  })

  if (Array.isArray(formState.columns)) {
    const columnsPayload = formState.columns
      .filter((col) => col.name && col.name.trim())
      .map((col) => ({
        name: col.name.trim(),
        description: col.description || undefined,
        data_type: col.data_type || undefined,
        sample_values: parseSampleValues(col.sample_values),
      }))
    if (columnsPayload.length) {
      payload.columns = columnsPayload
    }
  }

  Object.entries(extras).forEach(([key, value]) => {
    if (value !== undefined) {
      payload[key] = value
    }
  })

  return payload
}

export default function DatasetManager({ token, vendorProfile, datasets, onRefresh }) {
  const [formState, setFormState] = useState(createEmptyForm())
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
      setFormState(createEmptyForm())
      setEditingId(null)
    }
  }, [hasVendorProfile])

  const resetForm = () => {
    setFormState(createEmptyForm())
    setEditingId(null)
  }

  const handleChange = (event) => {
    const { name, value } = event.target
    setFormState((prev) => ({ ...prev, [name]: value }))
  }

  const handleColumnChange = (index, field, value) => {
    setFormState((prev) => ({
      ...prev,
      columns: prev.columns.map((column, i) =>
        i === index ? { ...column, [field]: value } : column
      ),
    }))
  }

  const addColumn = () => {
    setFormState((prev) => ({
      ...prev,
      columns: [...prev.columns, { ...EMPTY_COLUMN }],
    }))
  }

  const removeColumn = (index) => {
    if (formState.columns.length === 1) {
      return
    }
    setFormState((prev) => ({
      ...prev,
      columns: prev.columns.filter((_, i) => i !== index),
    }))
  }

  const handleEdit = async (dataset) => {
    setEditingId(dataset.id)
    setSaving(true)
    setError('')
    try {
      const fullDataset = await datasetService.get(token, dataset.id)

      // Prefer fully loaded columns from detail endpoint, but fall back to list data
      const sourceColumns =
        (fullDataset.columns && fullDataset.columns.length && fullDataset.columns) ||
        (dataset.columns && dataset.columns.length && dataset.columns) ||
        []

      const mappedColumns =
        sourceColumns.length > 0
          ? sourceColumns.map((col) => ({
              name: col.name || '',
              description: col.description || '',
              data_type: col.data_type || '',
              sample_values:
                col.sample_values !== undefined && col.sample_values !== null
                  ? typeof col.sample_values === 'string'
                    ? col.sample_values
                    : JSON.stringify(col.sample_values, null, 2)
                  : '',
            }))
          : [{ ...EMPTY_COLUMN }]

      setFormState({
        title: fullDataset.title || '',
        description: fullDataset.description || '',
        domain: fullDataset.domain || '',
        dataset_type: fullDataset.dataset_type || '',
        granularity: fullDataset.granularity || '',
        pricing_model: fullDataset.pricing_model || '',
        license: fullDataset.license || '',
        visibility: fullDataset.visibility || 'public',
        status: fullDataset.status || 'active',
        topics: Array.isArray(fullDataset.topics) ? fullDataset.topics.join(', ') : '',
        entities: Array.isArray(fullDataset.entities) ? fullDataset.entities.join(', ') : '',
        temporalCoverage: fullDataset.temporal_coverage ? JSON.stringify(fullDataset.temporal_coverage, null, 2) : '',
        geographicCoverage: fullDataset.geographic_coverage ? JSON.stringify(fullDataset.geographic_coverage, null, 2) : '',
        columns: mappedColumns,
      })
    } catch (err) {
      setError(err.message || 'Failed to load dataset details')
    } finally {
      setSaving(false)
    }
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!hasVendorProfile) {
      setError('Create your vendor profile before managing datasets.')
      return
    }

    const requiredFields = [
      { key: 'title', label: 'Dataset title' },
      { key: 'description', label: 'Description' },
      { key: 'domain', label: 'Domain' },
      { key: 'dataset_type', label: 'Dataset type' },
      { key: 'granularity', label: 'Granularity' },
      { key: 'pricing_model', label: 'Pricing model' },
      { key: 'license', label: 'License' },
      { key: 'topics', label: 'Topics' },
      { key: 'entities', label: 'Entities' },
      { key: 'temporalCoverage', label: 'Temporal coverage' },
      { key: 'geographicCoverage', label: 'Geographic coverage' },
    ]

    const missingField = requiredFields.find(({ key }) => !formState[key] || !formState[key].trim())
    if (missingField) {
      setError(`${missingField.label} is required`)
      return
    }

    let temporalCoverageObj
    let geographicCoverageObj
    try {
      temporalCoverageObj = JSON.parse(formState.temporalCoverage)
    } catch (err) {
      setError('Temporal coverage must be valid JSON')
      return
    }

    try {
      geographicCoverageObj = JSON.parse(formState.geographicCoverage)
    } catch (err) {
      setError('Geographic coverage must be valid JSON')
      return
    }

    const validColumns = (formState.columns || []).filter((col) => col.name && col.name.trim())
    if (!validColumns.length) {
      setError('Add at least one dataset column (name is required)')
      return
    }

    setSaving(true)
    setError('')
    setMessage('')

    try {
      const payload = buildPayload(formState, vendorProfile.id, {
        temporal_coverage: temporalCoverageObj,
        geographic_coverage: geographicCoverageObj,
      })
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
            <label htmlFor="dataset-description">
              Description <span>*</span>
            </label>
            <textarea
              id="dataset-description"
              name="description"
              rows={3}
              value={formState.description}
              onChange={handleChange}
              disabled={saving || !hasVendorProfile}
              required
              placeholder="High-level summary of the dataset's contents and value"
            />
          </div>

          <div className="form-group">
            <label htmlFor="domain">
              Domain <span>*</span>
            </label>
            <input
              id="domain"
              name="domain"
              type="text"
              value={formState.domain}
              onChange={handleChange}
              disabled={saving || !hasVendorProfile}
              required
              placeholder="Finance, Healthcare, Retail..."
            />
          </div>

          <div className="form-group">
            <label htmlFor="dataset_type">
              Dataset Type <span>*</span>
            </label>
            <input
              id="dataset_type"
              name="dataset_type"
              type="text"
              value={formState.dataset_type}
              onChange={handleChange}
              disabled={saving || !hasVendorProfile}
              required
              placeholder="Transactional, Time-series..."
            />
          </div>

          <div className="form-group">
            <label htmlFor="granularity">
              Granularity <span>*</span>
            </label>
            <input
              id="granularity"
              name="granularity"
              type="text"
              value={formState.granularity}
              onChange={handleChange}
              disabled={saving || !hasVendorProfile}
              required
              placeholder="Transaction-level, Daily, Monthly..."
            />
          </div>

          <div className="form-group">
            <label htmlFor="pricing_model">
              Pricing Model <span>*</span>
            </label>
            <input
              id="pricing_model"
              name="pricing_model"
              type="text"
              value={formState.pricing_model}
              onChange={handleChange}
              disabled={saving || !hasVendorProfile}
              required
              placeholder="Subscription, One-time, Usage-based"
            />
          </div>

          <div className="form-group">
            <label htmlFor="license">
              License <span>*</span>
            </label>
            <input
              id="license"
              name="license"
              type="text"
              value={formState.license}
              onChange={handleChange}
              disabled={saving || !hasVendorProfile}
              required
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
            <label htmlFor="topics">
              Topics (comma separated) <span>*</span>
            </label>
            <input
              id="topics"
              name="topics"
              type="text"
              value={formState.topics}
              onChange={handleChange}
              disabled={saving || !hasVendorProfile}
              required
              placeholder="e-commerce, retail, consumer behavior"
            />
          </div>

          <div className="form-group">
            <label htmlFor="entities">
              Entities (comma separated) <span>*</span>
            </label>
            <input
              id="entities"
              name="entities"
              type="text"
              value={formState.entities}
              onChange={handleChange}
              disabled={saving || !hasVendorProfile}
              required
              placeholder="transactions, products, customers"
            />
          </div>

          <div className="form-group full">
            <label htmlFor="temporalCoverage">
              Temporal Coverage (JSON) <span>*</span>
            </label>
            <textarea
              id="temporalCoverage"
              name="temporalCoverage"
              rows={3}
              value={formState.temporalCoverage}
              onChange={handleChange}
              disabled={saving || !hasVendorProfile}
              required
              placeholder='{"start_date":"2024-01-01","end_date":"2024-12-31","frequency":"Monthly"}'
            />
          </div>

          <div className="form-group full">
            <label htmlFor="geographicCoverage">
              Geographic Coverage (JSON) <span>*</span>
            </label>
            <textarea
              id="geographicCoverage"
              name="geographicCoverage"
              rows={3}
              value={formState.geographicCoverage}
              onChange={handleChange}
              disabled={saving || !hasVendorProfile}
              required
              placeholder='{"countries":["US","UK"],"regions":["North America","Europe"]}'
            />
          </div>

          <div className="form-group full columns-section">
            <div className="columns-header">
              <div>
                <h3>Dataset Columns</h3>
                <p>Provide the schema buyers can expect.</p>
              </div>
              <button type="button" className="secondary small" onClick={addColumn} disabled={saving || !hasVendorProfile}>
                Add Column
              </button>
            </div>

            {formState.columns.map((column, index) => (
              <div className="column-card" key={`dataset-column-${index}`}>
                <div className="column-grid">
                  <div className="form-group">
                    <label>
                      Column Name <span>*</span>
                    </label>
                    <input
                      type="text"
                      value={column.name}
                      onChange={(e) => handleColumnChange(index, 'name', e.target.value)}
                      placeholder="transaction_id"
                      required
                      disabled={saving || !hasVendorProfile}
                    />
                  </div>

                  <div className="form-group">
                    <label>Data Type</label>
                    <input
                      type="text"
                      value={column.data_type}
                      onChange={(e) => handleColumnChange(index, 'data_type', e.target.value)}
                      placeholder="UUID, DECIMAL, TEXT..."
                      disabled={saving || !hasVendorProfile}
                    />
                  </div>

                  <div className="form-group full">
                    <label>Description</label>
                    <textarea
                      rows={2}
                      value={column.description}
                      onChange={(e) => handleColumnChange(index, 'description', e.target.value)}
                      placeholder="Unique transaction identifier"
                      disabled={saving || !hasVendorProfile}
                    />
                  </div>

                  <div className="form-group full">
                    <label>Sample Values (JSON)</label>
                    <textarea
                      rows={2}
                      value={column.sample_values}
                      onChange={(e) => handleColumnChange(index, 'sample_values', e.target.value)}
                      placeholder='["a1b2c3", "d4e5f6"]'
                      disabled={saving || !hasVendorProfile}
                    />
                  </div>
                </div>

                <div className="column-actions">
                  <button
                    type="button"
                    className="text-button danger-text"
                    onClick={() => removeColumn(index)}
                    disabled={saving || formState.columns.length === 1}
                  >
                    Remove Column
                  </button>
                </div>
              </div>
            ))}
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
