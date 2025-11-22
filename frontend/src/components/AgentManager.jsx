import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { agentService } from '../services/agentService';
import { vendorService } from '../services/vendorService';
import {
  AlignLeftIcon,
  PlusIcon,
  AgentIcon,
} from './icons';


const EMPTY_AGENT_FORM = {
  name: '',
  description: '',
  config: { context_entries: [] },
};

/**
 * Config Editor Component
 * Allows vendor to add multiple context entries (type + content)
 */
function ConfigEditor({ config, onChange, disabled }) {
  const [entries, setEntries] = useState([]);

  // Initialize from config prop
  useEffect(() => {
    if (config && Array.isArray(config.context_entries)) {
      setEntries(config.context_entries);
    } else {
      setEntries([]);
    }
  }, [config]);

  // Notify parent when entries change (only when entries actually change)
  const updateParent = (newEntries) => {
    onChange({ context_entries: newEntries });
  };

  const addEntry = () => {
    const newEntries = [...entries, { type: '', content: '' }];
    setEntries(newEntries);
    updateParent(newEntries);
  };

  const updateEntry = (index, field, value) => {
    const updated = [...entries];
    updated[index][field] = value;
    setEntries(updated);
    updateParent(updated);
  };

  const removeEntry = (index) => {
    const newEntries = entries.filter((_, i) => i !== index);
    setEntries(newEntries);
    updateParent(newEntries);
  };

  return (
    <div className="config-editor">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <label className="form-label" style={{ marginBottom: 0 }}>
          Configure your AI Agent
        </label>
        <button
          type="button"
          className="btn btn-secondary btn-sm"
          onClick={addEntry}
          disabled={disabled}
          style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', padding: '8px 16px', height: 'auto' }}
        >
          <PlusIcon /> Add Context Entry
        </button>
      </div>

      {entries.length === 0 && (
        <div style={{ 
          padding: '24px', 
          textAlign: 'center', 
          color: 'var(--primary-600)', 
          background: 'var(--bg-light)', 
          borderRadius: '10px',
          fontSize: '14px',
          border: '1px solid var(--accent-100)'
        }}>
          No context entries yet. Click "Add Context Entry" to start configuring your AI agent.
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {entries.map((entry, index) => (
          <div
            key={index}
            style={{
              padding: '20px',
              background: 'var(--bg-light)',
              borderRadius: '10px',
              border: '1px solid var(--accent-100)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--primary-900)' }}>
                Entry {index + 1}
              </span>
              <button
                type="button"
                onClick={() => removeEntry(index)}
                disabled={disabled}
                style={{
                  background: 'none',
                  border: 'none',
                  color: disabled ? '#d1d5db' : '#dc2626',
                  cursor: disabled ? 'not-allowed' : 'pointer',
                  fontSize: '20px',
                  lineHeight: 1,
                  padding: '4px 8px',
                }}
                title="Remove entry"
              >
                ×
              </button>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <label style={{ 
                display: 'block',
                fontSize: '13px', 
                fontWeight: 600,
                color: 'var(--primary-900)',
                marginBottom: '8px'
              }}>
                Context Type
              </label>
              <input
                type="text"
                className="form-input"
                value={entry.type}
                onChange={(e) => updateEntry(index, 'type', e.target.value)}
                disabled={disabled}
                placeholder="e.g., company policy, security guideline, internal procedure"
                style={{ paddingLeft: '14px' }}
              />
            </div>

            <div style={{ marginBottom: 0 }}>
              <label style={{ 
                display: 'block',
                fontSize: '13px', 
                fontWeight: 600,
                color: 'var(--primary-900)',
                marginBottom: '8px'
              }}>
                Context Content
              </label>
              <textarea
                className="form-input"
                rows={4}
                value={entry.content}
                onChange={(e) => updateEntry(index, 'content', e.target.value)}
                disabled={disabled}
                placeholder="Enter the actual content/text for this context..."
                style={{ paddingLeft: '14px' }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function AgentManager() {
  const { user, token } = useAuth();
  const [vendorProfile, setVendorProfile] = useState(null);
  const [agentProfile, setAgentProfile] = useState(null);
  const [formData, setFormData] = useState(EMPTY_AGENT_FORM);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [showSuccessToast, setShowSuccessToast] = useState(false);
  const [wasCreate, setWasCreate] = useState(false);

  useEffect(() => {
    loadAgentData();
  }, [token, user?.id]);

  const loadAgentData = async () => {
    setLoading(true);
    setError('');
    setMessage('');
    try {
      // Get vendor profile
      const vendors = await vendorService.list(token);
      const ownVendor = vendors.find((item) => item.user_id === user?.id) || null;
      setVendorProfile(ownVendor);

      if (ownVendor) {
        // Get agent for this vendor
        const agents = await agentService.list(token, { vendorId: ownVendor.id });
        const ownAgent = agents && agents.length > 0 ? agents[0] : null;
        setAgentProfile(ownAgent);

        if (ownAgent) {
          // Transform flat config object back to context_entries array for editing
          let contextEntries = [];
          if (ownAgent.config && typeof ownAgent.config === 'object') {
            // Check if it's already in the old format (has context_entries)
            if (Array.isArray(ownAgent.config.context_entries)) {
              contextEntries = ownAgent.config.context_entries;
            } else {
              // It's in the new flat format, convert back to array for editing
              contextEntries = Object.entries(ownAgent.config).map(([type, content]) => ({
                type,
                content,
              }));
            }
          }

          setFormData({
            name: ownAgent.name || '',
            description: ownAgent.description || '',
            config: { context_entries: contextEntries },
          });
        } else {
          setFormData(EMPTY_AGENT_FORM);
        }
      } else {
        setFormData(EMPTY_AGENT_FORM);
      }
    } catch (err) {
      setError(err.message || 'Failed to load AI agent information');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleConfigChange = (newConfig) => {
    setFormData((prev) => ({
      ...prev,
      config: newConfig,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    if (!vendorProfile) {
      setError('Please create a vendor profile first');
      return;
    }

    // Show confirmation modal only for updates
    if (agentProfile) {
      setShowConfirmModal(true);
      return;
    }
    
    // For new agents, save directly
    await saveAgent();
  };

  const saveAgent = async () => {
    setSaving(true);
    setMessage('');
    setError('');
    setShowConfirmModal(false);
    
    if (!formData.name) {
      setError('Agent name is required');
      setSaving(false);
      return;
    }

    if (!formData.description) {
      setError('Agent description is required');
      setSaving(false);
      return;
    }
    
    try {
      // Transform context_entries array to flat key-value object
      const transformedConfig = {};
      if (formData.config && Array.isArray(formData.config.context_entries)) {
        formData.config.context_entries.forEach((entry) => {
          if (entry.type && entry.type.trim()) {
            transformedConfig[entry.type] = entry.content || '';
          }
        });
      }

      const payload = {
        name: formData.name,
        description: formData.description,
        config: transformedConfig,
        vendor_id: vendorProfile.id,
      };

      if (agentProfile) {
        await agentService.update(token, agentProfile.id, payload);
        setWasCreate(false);
      } else {
        await agentService.create(token, payload);
        setWasCreate(true);
      }
      
      // Show success toast for both create and update
      setShowSuccessToast(true);
      setTimeout(() => setShowSuccessToast(false), 3000);
      
      await loadAgentData();
    } catch (err) {
      setError(err.message || 'Failed to save AI agent');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-state">
        <div className="loading-spinner"></div>
        <p>Loading AI agent...</p>
      </div>
    );
  }

  if (!vendorProfile) {
    return (
      <div className="alert alert-error">
        Please create a vendor profile first before configuring your AI agent.
      </div>
    );
  }

  return (
    <div className="vendor-profile">
      {/* Success Toast */}
      {showSuccessToast && (
        <div className="success-toast">
          <div className="success-toast-icon">✓</div>
          <div className="success-toast-message">
            {wasCreate ? 'Agent created successfully!' : 'Agent updated successfully!'}
          </div>
        </div>
      )}

      {/* Confirmation Modal */}
      {showConfirmModal && (
        <div className="modal-overlay" onClick={() => setShowConfirmModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Confirm Update</h3>
              <p>Are you sure you want to update your AI agent configuration?</p>
            </div>
            <div className="modal-actions">
              <button 
                className="btn btn-secondary" 
                onClick={() => setShowConfirmModal(false)}
                disabled={saving}
              >
                Cancel
              </button>
              <button 
                className="btn btn-primary" 
                onClick={saveAgent}
                disabled={saving}
              >
                {saving ? 'Updating...' : 'Update'}
              </button>
            </div>
          </div>
        </div>
      )}

      {(message || error) && (
        <div className="alerts-container">
          {message && <div className="alert alert-success">{message}</div>}
          {error && <div className="alert alert-error">{error}</div>}
        </div>
      )}

      <form className="vendor-form" onSubmit={handleSubmit}>
        <div className="form-section">
          <h3>Basic Information</h3>
          <div className="form-grid">
            {/* Agent Name */}
            <div className="form-group full">
              <label htmlFor="name" className="form-label">
                Agent Name <span className="required">*</span>
              </label>
              <div className="input-wrapper">
                <div className="input-group">
                  <span className="input-icon"><AgentIcon /></span>
                  <input
                    id="name"
                    name="name"
                    type="text"
                    required
                    value={formData.name}
                    onChange={handleInputChange}
                    disabled={saving}
                    placeholder="e.g., Customer Support Bot, Data Query Assistant"
                    className="form-input"
                  />
                </div>
              </div>
            </div>

            {/* Description */}
            <div className="form-group full">
              <label htmlFor="description" className="form-label">
                Description <span className="required">*</span>
              </label>
              <div className="input-wrapper">
                <div className="input-group">
                  <span className="input-icon textarea-icon"><AlignLeftIcon /></span>
                  <textarea
                    id="description"
                    name="description"
                    rows={4}
                    required
                    value={formData.description}
                    onChange={handleInputChange}
                    disabled={saving}
                    placeholder="Describe what this AI agent does and how it helps buyers interact with your data..."
                    className="form-input"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="form-section">
          <h3>Agent Configuration</h3>
          <ConfigEditor
            config={formData.config}
            onChange={handleConfigChange}
            disabled={saving}
          />
        </div>

        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={saving || loading}>
            {saving ? 'Saving...' : agentProfile ? 'Update Agent' : 'Create Agent'}
          </button>
        </div>
      </form>
    </div>
  );
}
