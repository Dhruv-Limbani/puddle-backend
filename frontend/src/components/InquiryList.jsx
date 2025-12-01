import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { acidService } from '../services/acidService';
import { CheckIcon, DatabaseIcon, UsersIcon } from './icons';
import './InquiryList.css';

export default function InquiryList() {
  const { token } = useAuth();
  const [inquiries, setInquiries] = useState([]);
  const [selectedInquiry, setSelectedInquiry] = useState(null);
  const [statusFilter, setStatusFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    loadInquiries();
  }, [token]);

  const loadInquiries = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await acidService.listInquiries(token);
      setInquiries(data);
    } catch (err) {
      setError(err.message || 'Failed to load inquiries');
    } finally {
      setLoading(false);
    }
  };

  const loadInquiryDetails = async (inquiryId) => {
    try {
      const data = await acidService.getInquiry(token, inquiryId);
      setSelectedInquiry(data);
    } catch (err) {
      setError(err.message || 'Failed to load inquiry details');
    }
  };

  const handleStatusUpdate = async (inquiryId, newStatus) => {
    setUpdating(true);
    setError('');
    setSuccessMessage('');
    try {
      await acidService.updateInquiry(token, inquiryId, { status: newStatus });
      setSuccessMessage(`Inquiry ${newStatus === 'accepted' ? 'accepted' : 'rejected'} successfully!`);
      await loadInquiries();
      if (selectedInquiry?.id === inquiryId) {
        await loadInquiryDetails(inquiryId);
      }
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      setError(err.message || 'Failed to update inquiry status');
    } finally {
      setUpdating(false);
    }
  };

  const filteredInquiries = inquiries.filter(inq => 
    statusFilter === 'all' || inq.status === statusFilter
  );

  const statusCounts = {
    all: inquiries.length,
    draft: inquiries.filter(i => i.status === 'draft').length,
    submitted: inquiries.filter(i => i.status === 'submitted').length,
    pending_review: inquiries.filter(i => i.status === 'pending_review').length,
    responded: inquiries.filter(i => i.status === 'responded').length,
    accepted: inquiries.filter(i => i.status === 'accepted').length,
    rejected: inquiries.filter(i => i.status === 'rejected').length,
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusIcon = (status) => {
    const icons = {
      draft: '📝',
      submitted: '✉️',
      pending_review: '⏳',
      responded: '✅',
      accepted: '🎉',
      rejected: '❌',
    };
    return icons[status] || '📄';
  };

  if (loading) {
    return (
      <div className="loading-state">
        <div className="loading-spinner"></div>
        <p>Loading inquiries...</p>
      </div>
    );
  }

  return (
    <div className="inquiry-list-container">
      {/* Success Toast */}
      {successMessage && (
        <div className="success-toast">
          <div className="success-toast-icon">✓</div>
          <div className="success-toast-message">{successMessage}</div>
        </div>
      )}

      <div className="inquiry-filters">
        <button
          className={`filter-btn ${statusFilter === 'all' ? 'active' : ''}`}
          onClick={() => setStatusFilter('all')}
        >
          All <span className="filter-count">{statusCounts.all}</span>
        </button>
        <button
          className={`filter-btn ${statusFilter === 'draft' ? 'active' : ''}`}
          onClick={() => setStatusFilter('draft')}
        >
          Draft <span className="filter-count">{statusCounts.draft}</span>
        </button>
        <button
          className={`filter-btn ${statusFilter === 'submitted' ? 'active' : ''}`}
          onClick={() => setStatusFilter('submitted')}
        >
          Submitted <span className="filter-count">{statusCounts.submitted}</span>
        </button>
        <button
          className={`filter-btn ${statusFilter === 'pending_review' ? 'active' : ''}`}
          onClick={() => setStatusFilter('pending_review')}
        >
          In Review <span className="filter-count">{statusCounts.pending_review}</span>
        </button>
        <button
          className={`filter-btn ${statusFilter === 'responded' ? 'active' : ''}`}
          onClick={() => setStatusFilter('responded')}
        >
          Responded <span className="filter-count">{statusCounts.responded}</span>
        </button>
        <button
          className={`filter-btn ${statusFilter === 'accepted' ? 'active' : ''}`}
          onClick={() => setStatusFilter('accepted')}
        >
          Accepted <span className="filter-count">{statusCounts.accepted}</span>
        </button>
        <button
          className={`filter-btn ${statusFilter === 'rejected' ? 'active' : ''}`}
          onClick={() => setStatusFilter('rejected')}
        >
          Rejected <span className="filter-count">{statusCounts.rejected}</span>
        </button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <div className="inquiry-content">
        {/* Inquiry List */}
        <div className="inquiry-cards">
          {filteredInquiries.length === 0 ? (
            <div className="inquiry-empty">
              <CheckIcon />
              <h3>No inquiries found</h3>
              <p>
                {statusFilter === 'all'
                  ? 'Start a conversation with ACID assistant to create your first inquiry!'
                  : `No inquiries with status: ${statusFilter}`}
              </p>
            </div>
          ) : (
            filteredInquiries.map((inquiry) => (
              <div
                key={inquiry.id}
                className={`inquiry-card ${selectedInquiry?.id === inquiry.id ? 'selected' : ''}`}
                onClick={() => loadInquiryDetails(inquiry.id)}
              >
                <div className="inquiry-card-header">
                  <span className="inquiry-icon">{getStatusIcon(inquiry.status)}</span>
                  <span className="inquiry-id">Inquiry #{inquiry.id}</span>
                  <span className={`badge-status badge-status-${inquiry.status}`}>
                    {inquiry.status}
                  </span>
                </div>
                <div className="inquiry-card-body">
                  {inquiry.dataset_title && (
                    <div className="inquiry-dataset">
                      <DatabaseIcon />
                      <span>{inquiry.dataset_title}</span>
                    </div>
                  )}
                  {inquiry.vendor_name && (
                    <div className="inquiry-vendor">
                      <UsersIcon />
                      <span>{inquiry.vendor_name}</span>
                    </div>
                  )}
                  <div className="inquiry-date">Created: {formatDate(inquiry.created_at)}</div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Inquiry Details Panel */}
        {selectedInquiry && (
          <div className="inquiry-details-panel">
            <div className="details-header">
              <h3>Inquiry #{selectedInquiry.id}</h3>
              <span className={`badge-status badge-status-${selectedInquiry.status}`}>
                {selectedInquiry.status}
              </span>
            </div>

            <div className="details-section">
              <h4>Dataset Information</h4>
              {selectedInquiry.dataset_title ? (
                <div className="info-item">
                  <DatabaseIcon />
                  <span>{selectedInquiry.dataset_title}</span>
                </div>
              ) : (
                <p className="info-empty">No dataset linked</p>
              )}
            </div>

            <div className="details-section">
              <h4>Vendor Information</h4>
              {selectedInquiry.vendor_name ? (
                <div className="info-item">
                  <UsersIcon />
                  <span>{selectedInquiry.vendor_name}</span>
                </div>
              ) : (
                <p className="info-empty">No vendor assigned</p>
              )}
            </div>

            {/* Removed: Your Requirements and Vendor Response sections as requested */}

            <div className="details-section">
              <h4>Timeline</h4>
              <div className="timeline">
                <div className="timeline-item">
                  <span className="timeline-label">Created</span>
                  <span className="timeline-date">{formatDate(selectedInquiry.created_at)}</span>
                </div>
                <div className="timeline-item">
                  <span className="timeline-label">Last Updated</span>
                  <span className="timeline-date">{formatDate(selectedInquiry.updated_at)}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
