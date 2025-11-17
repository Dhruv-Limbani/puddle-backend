import React, { useState, useEffect, } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { dataCatalogService } from '../services/dataCatalogService';
import './DataCatalog.css';

// Import all the icons this component needs
import {
  PlusIcon,
  EditIcon,
  TrashIcon,
  ArrowLeftIcon,
  TagIcon,
  ColumnsIcon,
  TypeIcon,
  DatabaseIcon,
  GlobeIcon,
  CheckIcon,
  EyeIcon,
  AlignLeftIcon,
  ChartIcon,
  UsersIcon,
  CalendarIcon,
} from './icons'; // Assuming Icons.jsx is in the same folder

// --- UTILITY COMPONENTS ---

/**
 * Reusable Modal Component
 * (Styled to match your screenshot)
 */
function Modal({ title, children, confirmText, cancelText, onConfirm, onCancel, confirmVariant = 'primary', isSaving = false }) {
  return (
    <div className="modal-overlay" onMouseDown={onCancel}>
      <div className="modal-content" onMouseDown={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{title}</h3>
          <p>{children}</p>
        </div>
        <div className="modal-actions">
          <button className="btn btn-secondary" onClick={onCancel} disabled={isSaving}>
            {cancelText || 'Cancel'}
          </button>
          <button
            className={`btn ${confirmVariant === 'danger' ? 'btn-danger' : 'btn-primary'}`}
            onClick={onConfirm}
            disabled={isSaving}
          >
            {isSaving ? 'Saving...' : (confirmText || 'Confirm')}
          </button>
        </div>
      </div>
    </div>
  );
}

// Reusable Toast Component
function SuccessToast({ message }) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setVisible(false), 3000);
    return () => clearTimeout(timer);
  }, []);

  if (!visible) return null;

  return (
    <div className="success-toast">
      <div className="success-toast-icon">✓</div>
      <div className="success-toast-message">{message}</div>
    </div>
  );
}

// Reusable Tag Input for Topics
function TagInput({ tags, setTags }) {
  const [inputValue, setInputValue] = useState('');

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      const newTag = inputValue.trim().toLowerCase();
      if (newTag && !tags.includes(newTag)) {
        setTags([...tags, newTag]);
      }
      setInputValue('');
    }
  };

  const removeTag = (tagToRemove) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  return (
    <div className="tag-input-container">
      {tags.map((tag, index) => (
        <span key={index} className="tag-item">
          {tag}
          <button type="button" onClick={() => removeTag(tag)}>&times;</button>
        </span>
      ))}
      <input
        type="text"
        className="tag-input"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Add topics (press Enter)"
      />
    </div>
  );
}


// --- DATA CATALOG COMPONENTS ---

/**
 * 1. DatasetList (Main View)
 * Shows a table of datasets with actions
 */
function DatasetList({ vendorId, onEdit, onCreate, onRefresh }) {
  const { token } = useAuth();
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showDeleteModal, setShowDeleteModal] = useState(null); // stores datasetId
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    loadData();
  }, [vendorId, onRefresh, token]); // Refresh when vendorId or refresh trigger changes

  const loadData = async () => {
    setLoading(true);
    setError('');
    try {
      // Assuming vendorId is now implicitly handled by the token on the backend
      const data = await dataCatalogService.listDatasets(token);
      setDatasets(data);
    } catch (err) {
      setError('Failed to load datasets.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClick = (datasetId) => {
    setShowDeleteModal(datasetId);
  };

  const confirmDelete = async () => {
    if (!showDeleteModal) return;
    setDeleting(true);
    setError('');
    try {
      await dataCatalogService.deleteDataset(token, showDeleteModal);
      setShowDeleteModal(null);
      loadData(); // Refresh the list
    } catch (err) {
      setError('Failed to delete dataset.');
    } finally {
      setDeleting(false);
    }
  };

  const formatDate = (isoString) => {
    return new Date(isoString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="loading-state">
        <div className="loading-spinner"></div>
        <p>Loading your data catalog...</p>
      </div>
    );
  }

  return (
    <div className="data-catalog-tab">
      {showDeleteModal && (
        <Modal
          title="Delete Dataset"
          confirmText={deleting ? 'Deleting...' : 'Delete'}
          confirmVariant="danger"
          onConfirm={confirmDelete}
          onCancel={() => setShowDeleteModal(null)}
          isSaving={deleting}
        >
          Are you sure you want to delete this dataset? This action cannot be undone.
        </Modal>
      )}

      <div className="catalog-header">
        <h2>Your Datasets</h2>
        <button className="btn btn-primary" onClick={onCreate}>
          <PlusIcon />
          Create Dataset
        </button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      
      <div className="dataset-table-wrapper">
        <table className="dataset-table">
          <thead>
            <tr>
              <th>Title</th>
              <th>Status</th>
              <th>Visibility</th>
              <th>Domain</th>
              <th>Last Updated</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {datasets.length === 0 ? (
              <tr>
                <td colSpan="6" style={{ textAlign: 'center', padding: '32px' }}>
                  You haven't created any datasets yet.
                </td>
              </tr>
            ) : (
              datasets.map(ds => (
                <tr key={ds.id}>
                  <td><span className="dataset-title">{ds.title}</span></td>
                  <td><span className={`badge-status badge-status-${ds.status}`}>{ds.status}</span></td>
                  <td><span className={`badge-status badge-visibility-${ds.visibility}`}>{ds.visibility}</span></td>
                  <td>{ds.domain || 'N/A'}</td>
                  <td>{formatDate(ds.updated_at)}</td>
                  <td>
                    <div className="action-buttons">
                      <button className="icon-btn" title="Edit" onClick={() => onEdit(ds.id)}>
                        <EditIcon />
                      </button>
                      <button className="icon-btn delete" title="Delete" onClick={() => handleDeleteClick(ds.id)}>
                        <TrashIcon />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/**
 * 2. DatasetForm (Create/Edit View)
 * A full form for dataset and its columns
 */
const EMPTY_DATASET_FORM = {
  title: '', description: '', status: 'draft', visibility: 'private',
  domain: '', dataset_type: '', granularity: '', pricing_model: '',
  license: '', topics: [],
};
const EMPTY_COLUMN = { id: `temp_${Date.now()}`, name: '', data_type: 'string', description: '' };

function DatasetForm({ datasetId, onBack, onSaveSuccess }) {
  const { token } = useAuth();
  const [formData, setFormData] = useState(EMPTY_DATASET_FORM);
  const [columns, setColumns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [showSuccess, setShowSuccess] = useState(false);
  const [pageTitle, setPageTitle] = useState('Create Dataset');
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  useEffect(() => {
    if (datasetId) {
      setPageTitle('Edit Dataset');
      loadDataset();
    } else {
      setFormData(EMPTY_DATASET_FORM);
      setColumns([
        { ...EMPTY_COLUMN, id: `temp_${Date.now()}` },
      ]);
      setLoading(false);
    }
  }, [datasetId]);

  const loadDataset = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await dataCatalogService.getDatasetDetails(token, datasetId);
      const { columns, ...datasetData } = data;
      setFormData({
        title: data.title || '',
        description: data.description || '',
        status: data.status || 'draft',
        visibility: data.visibility || 'private',
        domain: data.domain || '',
        dataset_type: data.dataset_type || '',
        granularity: data.granularity || '',
        pricing_model: data.pricing_model || '',
        license: data.license || '',
        topics: Array.isArray(data.topics) ? data.topics : [],
      });
      setColumns(columns || []);
    } catch (err) {
      setError('Failed to load dataset details.');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleColumnChange = (index, field, value) => {
    const newColumns = [...columns];
    newColumns[index] = { ...newColumns[index], [field]: value };
    setColumns(newColumns);
  };

  const addColumn = () => {
    setColumns([...columns, { ...EMPTY_COLUMN, id: `temp_${Date.now()}` }]);
  };

  const removeColumn = (index) => {
    setColumns(columns.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (datasetId) { // This is an UPDATE
      setShowConfirmModal(true); // Show modal instead of saving directly
    } else { // This is a CREATE
      await saveDataset(); // Save directly
    }
  };

  const saveDataset = async () => {
    setShowConfirmModal(false);
    setSaving(true);
    setError('');
    
    // Clean columns: remove temp IDs
    const cleanColumns = columns.map(col => {
      const { id, ...rest } = col;
      // Send real ID if it's not a temp one
      return col.id.toString().startsWith('temp_') ? rest : col;
    });

    const payload = { ...formData, columns: cleanColumns };
    
    try {
      if (datasetId) {
        await dataCatalogService.updateDataset(token, datasetId, payload);
      } else {
        await dataCatalogService.createDataset(token, payload);
      }
      setShowSuccess(true);
      setTimeout(() => {
        setShowSuccess(false);
        onSaveSuccess(); // Go back to list
      }, 2000);
    } catch (err) {
      setError(err.message || 'Failed to save dataset.');
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-state">
        <div className="loading-spinner"></div>
        <p>Loading dataset form...</p>
      </div>
    );
  }

  return (
    <div className="data-catalog-form">
      {showSuccess && <SuccessToast message={datasetId ? 'Dataset updated!' : 'Dataset created!'} />}
      
      {showConfirmModal && (
        <Modal
          title="Confirm Update"
          confirmText="Confirm Update"
          onConfirm={saveDataset}
          onCancel={() => setShowConfirmModal(false)}
          isSaving={saving}
        >
          Are you sure you want to update this dataset?
        </Modal>
      )}
      
      <form className="vendor-form" onSubmit={handleSubmit}>
        <div className="form-header">
          <button type="button" className="back-btn" onClick={onBack} title="Back to list" disabled={saving}>
            <ArrowLeftIcon />
          </button>
          <h2>{pageTitle}</h2>
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        <div className="form-section">
          <h3>Dataset Details</h3>
          <div className="form-grid">
            <div className="form-group full">
              <label htmlFor="title" className="form-label">Title <span className="required">*</span></label>
              <div className="input-wrapper">
                <span className="input-icon" style={{ left: '16px' }}><TagIcon /></span>
                <input id="title" name="title" type="text" required value={formData.title} onChange={handleInputChange} className="form-input" placeholder="e.g., US Consumer Credit Trends" disabled={saving} style={{ paddingLeft: '48px' }} />
              </div>
            </div>

            <div className="form-group full">
              <label htmlFor="description" className="form-label">Description</label>
              <div className="input-wrapper">
                <span className="input-icon textarea-icon" style={{ left: '16px' }}><AlignLeftIcon /></span>
                <textarea id="description" name="description" value={formData.description} onChange={handleInputChange} className="form-input" placeholder="A brief summary of what this dataset contains..." disabled={saving} style={{ paddingLeft: '48px' }}></textarea>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="status" className="form-label">Status</label>
              <div className="input-wrapper">
                <span className="input-icon" style={{ left: '16px' }}><CheckIcon /></span>
                <select id="status" name="status" value={formData.status} onChange={handleInputChange} className="form-input" disabled={saving} style={{ paddingLeft: '48px' }}>
                  <option value="draft">Draft</option>
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                </select>
              </div>
            </div>
            
            <div className="form-group">
              <label htmlFor="visibility" className="form-label">Visibility</label>
              <div className="input-wrapper">
                <span className="input-icon" style={{ left: '16px' }}><EyeIcon /></span>
                <select id="visibility" name="visibility" value={formData.visibility} onChange={handleInputChange} className="form-input" disabled={saving} style={{ paddingLeft: '48px' }}>
                  <option value="private">Private</option>
                  <option value="public">Public</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="domain" className="form-label">Domain</label>
              <div className="input-wrapper">
                <span className="input-icon" style={{ left: '16px' }}><GlobeIcon /></span>
                <input id="domain" name="domain" type="text" value={formData.domain} onChange={handleInputChange} className="form-input" placeholder="e.g., Finance, Healthcare" disabled={saving} style={{ paddingLeft: '48px' }} />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="dataset_type" className="form-label">Dataset Type</label>
              <div className="input-wrapper">
                <span className="input-icon" style={{ left: '16px' }}><DatabaseIcon /></span>
                <input id="dataset_type" name="dataset_type" type="text" value={formData.dataset_type} onChange={handleInputChange} className="form-input" placeholder="e.g., Time Series, Geospatial" disabled={saving} style={{ paddingLeft: '48px' }} />
              </div>
            </div>
            
            <div className="form-group">
              <label htmlFor="pricing_model" className="form-label">Pricing Model</label>
              <div className="input-wrapper">
                <span className="input-icon" style={{ left: '16px' }}><ChartIcon /></span>
                <input id="pricing_model" name="pricing_model" type="text" value={formData.pricing_model} onChange={handleInputChange} className="form-input" placeholder="e.g., Subscription, Per-query" disabled={saving} style={{ paddingLeft: '48px' }} />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="license" className="form-label">License</label>
              <div className="input-wrapper">
                <span className="input-icon" style={{ left: '16px' }}><UsersIcon /></span>
                <input id="license" name="license" type="text" value={formData.license} onChange={handleInputChange} className="form-input" placeholder="e.g., Commercial Use" disabled={saving} style={{ paddingLeft: '48px' }} />
              </div>
            </div>

            <div className="form-group full">
              <label htmlFor="topics" className="form-label">Topics</label>
              <div className="input-wrapper">
                <span className="input-icon textarea-icon" style={{ left: '16px' }}><TagIcon /></span>
                <TagInput tags={formData.topics} setTags={(newTags) => setFormData(p => ({...p, topics: newTags}))} />
              </div>
            </div>
          </div>
        </div>

        <div className="form-section columns-section">
          <h3>Dataset Columns</h3>
          <div className="columns-list">
            {columns.map((col, index) => (
              <div className="column-row" key={col.id}>
                {/* FIX 1: Add input-wrapper for correct label order */}
                <div className="form-group">
                  <label htmlFor={`col_name_${index}`} className="form-label">Column Name <span className="required">*</span></label>
                  <div className="input-wrapper">
                    <input id={`col_name_${index}`} type="text" value={col.name} onChange={(e) => handleColumnChange(index, 'name', e.target.value)} className="form-input" placeholder="e.g., user_id" required disabled={saving} />
                  </div>
                </div>
                {/* FIX 1: Add input-wrapper for correct label order */}
                <div className="form-group">
                  <label htmlFor={`col_type_${index}`} className="form-label">Data Type</label>
                  <div className="input-wrapper">
                    <select id={`col_type_${index}`} value={col.data_type} onChange={(e) => handleColumnChange(index, 'data_type', e.target.value)} className="form-input" disabled={saving}>
                      <option value="string">String</option>
                      <option value="number">Number</option>
                      <option value="boolean">Boolean</option>
                      <option value="date">Date</option>
                      <option value="timestamp">Timestamp</option>
                      <option value="object">Object</option>
                    </select>
                  </div>
                </div>
                {/* FIX 1: Add input-wrapper for correct label order */}
                <div className="form-group">
                  <label htmlFor={`col_desc_${index}`} className="form-label">Description</label>
                  <div className="input-wrapper">
                    <input id={`col_desc_${index}`} type="text" value={col.description} onChange={(e) => handleColumnChange(index, 'description', e.target.value)} className="form-input" placeholder="e.g., Unique user identifier" disabled={saving} />
                  </div>
                </div>
                <button type="button" className="remove-column-btn" title="Remove Column" onClick={() => removeColumn(index)} disabled={saving}>
                  <TrashIcon />
                </button>
              </div>
            ))}
          </div>
          {/* FIX 3: Changed button style to 'btn-secondary' 
            (or any other style) for better contrast.
            'btn-secondary' is light blue, let's use that.
          */}
          <button type="button" className="btn btn-secondary add-column-btn" onClick={addColumn} disabled={saving}>
            <PlusIcon />
            Add Column
          </button>
        </div>

        <div className="form-actions">
          <button type="button" className="btn btn-secondary" onClick={onBack} disabled={saving}>
            Cancel
          </button>
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? (datasetId ? 'Saving...' : 'Creating...') : (datasetId ? 'Save Changes' : 'Create Dataset')}
          </button>
        </div>
      </form>
    </div>
  );
}


/**
 * 3. DataCatalogTab (Main Controller)
 * Manages the view state between List and Form
 */
export default function DataCatalogTab() {
  const { vendorId } = useAuth(); // You need to make sure your AuthContext provides this!
  const [view, setView] = useState('list'); // 'list' or 'form'
  const [selectedDatasetId, setSelectedDatasetId] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0); // Used to trigger list refresh

  // Mock vendorId if not provided by AuthContext, for dev purposes
  // In production, your AuthContext should find the vendorId from the user
  const effectiveVendorId = vendorId || 'vendor_abc_123'; // REMOVE THIS FALLBACK IN PROD

  const handleCreate = () => {
    setSelectedDatasetId(null);
    setView('form');
  };

  const handleEdit = (datasetId) => {
    setSelectedDatasetId(datasetId);
    setView('form');
  };

  const handleBack = () => {
    setView('list');
    setSelectedDatasetId(null);
  };
  
  const handleSaveSuccess = () => {
    setView('list');
    setSelectedDatasetId(null);
    setRefreshKey(key => key + 1); // Increment key to force DatasetList refresh
  };

  if (!effectiveVendorId) {
    return (
      <div className="loading-state">
        <div className="loading-spinner"></div>
        <p>Verifying vendor status...</p>
      </div>
    );
  }

  return (
    view === 'list' ? (
      <DatasetList
        vendorId={effectiveVendorId}
        onEdit={handleEdit}
        onCreate={handleCreate}
        onRefresh={refreshKey}
      />
    ) : (
      <DatasetForm
        vendorId={effectiveVendorId}
        datasetId={selectedDatasetId}
        onBack={handleBack}
        onSaveSuccess={handleSaveSuccess}
      />
    )
  );
}