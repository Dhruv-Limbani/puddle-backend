import { useMemo, useState } from 'react'
import { agentService } from '../services/agentService'

const EMPTY_FORM = {
  name: '',
  description: '',
  model_used: 'gemini-embedding-001',
  active: true,
  config: '',
}

function parseConfig(value) {
  if (!value || !value.trim()) return undefined
  try {
    return JSON.parse(value)
  } catch (error) {
    throw new Error('Config must be valid JSON')
  }
}

export default function AgentManager({ token, vendorProfile, agents, onRefresh }) {
  const [formState, setFormState] = useState(EMPTY_FORM)
  const [editingId, setEditingId] = useState(null)
  const [saving, setSaving] = useState(false)
  const [deletingId, setDeletingId] = useState(null)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  const hasVendorProfile = useMemo(() => Boolean(vendorProfile?.id), [vendorProfile?.id])

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target
    setFormState((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }))
  }

  const resetForm = () => {
    setFormState(EMPTY_FORM)
    setEditingId(null)
  }

  const handleEdit = (agent) => {
    setEditingId(agent.id)
    setFormState({
      name: agent.name || '',
      description: agent.description || '',
      model_used: agent.model_used || 'gemini-embedding-001',
      active: agent.active ?? true,
      config: agent.config ? JSON.stringify(agent.config, null, 2) : '',
    })
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!hasVendorProfile) {
      setError('Create your vendor profile before managing agents.')
      return
    }

    if (!formState.name.trim()) {
      setError('Agent name is required')
      return
    }

    let configObject
    try {
      configObject = parseConfig(formState.config)
    } catch (err) {
      setError(err.message)
      return
    }

    setSaving(true)
    setError('')
    setMessage('')

    try {
      const payload = {
        vendor_id: vendorProfile.id,
        name: formState.name,
        description: formState.description || undefined,
        model_used: formState.model_used || undefined,
        active: formState.active,
        config: configObject,
      }

      if (editingId) {
        await agentService.update(token, editingId, payload)
        setMessage('Agent updated successfully')
      } else {
        await agentService.create(token, payload)
        setMessage('Agent created successfully')
      }

      resetForm()
      await onRefresh?.()
    } catch (err) {
      setError(err.message || 'Failed to save agent')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (agentId) => {
    if (!window.confirm('Delete this agent? This cannot be undone.')) return

    setDeletingId(agentId)
    setError('')
    setMessage('')

    try {
      await agentService.remove(token, agentId)
      if (editingId === agentId) {
        resetForm()
      }
      setMessage('Agent deleted successfully')
      await onRefresh?.()
    } catch (err) {
      setError(err.message || 'Failed to delete agent')
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="agent-manager">
      <div className="panel-header">
        <h2>Your AI Agents</h2>
        <p>Configure the agents that help buyers interact with your datasets.</p>
      </div>

      {(message || error) && (
        <div className="agent-alerts">
          {message && <div className="success">{message}</div>}
          {error && <div className="error">{error}</div>}
        </div>
      )}

      <form className="agent-form" onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="agent-name">
              Agent Name <span>*</span>
            </label>
            <input
              id="agent-name"
              name="name"
              type="text"
              value={formState.name}
              onChange={handleChange}
              required
              disabled={saving || !hasVendorProfile}
              placeholder="Finance Data Assistant"
            />
          </div>

          <div className="form-group">
            <label htmlFor="model_used">Model Used</label>
            <input
              id="model_used"
              name="model_used"
              type="text"
              value={formState.model_used}
              onChange={handleChange}
              disabled={saving || !hasVendorProfile}
              placeholder="gemini-embedding-001"
            />
          </div>

          <div className="form-group checkbox-group">
            <label htmlFor="active">Active</label>
            <input
              id="active"
              name="active"
              type="checkbox"
              checked={formState.active}
              onChange={handleChange}
              disabled={saving || !hasVendorProfile}
            />
          </div>

          <div className="form-group full">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              name="description"
              rows={3}
              value={formState.description}
              onChange={handleChange}
              disabled={saving || !hasVendorProfile}
              placeholder="Explain the agent's purpose and scope"
            />
          </div>

          <div className="form-group full">
            <label htmlFor="config">Config (JSON)</label>
            <textarea
              id="config"
              name="config"
              rows={4}
              value={formState.config}
              onChange={handleChange}
              disabled={saving || !hasVendorProfile}
              placeholder='{"max_tokens": 1000, "temperature": 0.7}'
            />
          </div>
        </div>

        <div className="form-actions">
          <button type="submit" className="primary" disabled={saving || !hasVendorProfile}>
            {saving ? 'Saving...' : editingId ? 'Update Agent' : 'Create Agent'}
          </button>
          {editingId && (
            <button type="button" className="secondary" onClick={resetForm} disabled={saving}>
              Cancel
            </button>
          )}
        </div>
      </form>

      {agents.length === 0 ? (
        <div className="panel-empty agent-empty">
          {hasVendorProfile
            ? 'No agents yet. Use the form above to configure your first agent.'
            : 'Create your vendor profile to start configuring agents.'}
        </div>
      ) : (
        <ul className="agent-list">
          {agents.map((agent) => (
            <li key={agent.id} className="agent-card">
              <div className="agent-card__header">
                <h3>{agent.name || 'Untitled Agent'}</h3>
                <span className={`badge badge-pill ${agent.active ? 'active' : 'inactive'}`}>
                  {agent.active ? 'Active' : 'Inactive'}
                </span>
              </div>
              {agent.description && <p className="agent-card__description">{agent.description}</p>}
              <div className="agent-card__meta">
                <span>Model: {agent.model_used || '—'}</span>
                <span>
                  Updated: {agent.updated_at ? new Date(agent.updated_at).toLocaleDateString() : '—'}
                </span>
              </div>
              <div className="agent-row-actions">
                <button type="button" className="text-button" onClick={() => handleEdit(agent)} disabled={saving}>
                  Edit
                </button>
                <button
                  type="button"
                  className="text-button danger-text"
                  onClick={() => handleDelete(agent.id)}
                  disabled={deletingId === agent.id}
                >
                  {deletingId === agent.id ? 'Deleting...' : 'Delete'}
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
