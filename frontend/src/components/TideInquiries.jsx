import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { tideService } from '../services/tideService';
import ChatMessage from './ChatMessage';
import { DatabaseIcon, UsersIcon, SendIcon, MessageIcon, CheckIcon } from './icons';
import './TideInquiries.css';

export default function TideInquiries() {
  const { token } = useAuth();
  const [inquiries, setInquiries] = useState([]);
  const [selectedInquiry, setSelectedInquiry] = useState(null);
  const [statusFilter, setStatusFilter] = useState('submitted');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  
  // Chat state
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef(null);
  
  // Response form state
  const [responseForm, setResponseForm] = useState({
    pricing: '',
    delivery_method: '',
    delivery_timeline: '',
    terms_and_conditions: '',
    additional_notes: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [showSummary, setShowSummary] = useState(false);
  const [aiSummary, setAiSummary] = useState(null);

  useEffect(() => {
    loadInquiries();
    loadConversations();
  }, [token]);

  useEffect(() => {
    if (activeConversationId) {
      loadMessages(activeConversationId);
    }
  }, [activeConversationId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadInquiries = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await tideService.listInquiries(token);
      setInquiries(data);
      // Auto-select first inquiry in current filter
      const filtered = data.filter(i => statusFilter === 'all' || i.status === statusFilter);
      if (filtered.length > 0 && !selectedInquiry) {
        await loadInquiryDetails(filtered[0].id);
      }
    } catch (err) {
      setError(err.message || 'Failed to load inquiries');
    } finally {
      setLoading(false);
    }
  };

  const loadInquiryDetails = async (inquiryId) => {
    try {
      const data = await tideService.getInquiry(token, inquiryId);
      setSelectedInquiry(data);
      setResponseForm({
        pricing: data.vendor_response?.pricing || '',
        delivery_method: data.vendor_response?.delivery_method || '',
        delivery_timeline: data.vendor_response?.delivery_timeline || '',
        terms_and_conditions: data.vendor_response?.terms_and_conditions || '',
        additional_notes: data.vendor_response?.additional_notes || '',
      });
    } catch (err) {
      setError(err.message || 'Failed to load inquiry details');
    }
  };

  const loadConversations = async () => {
    try {
      const data = await tideService.listConversations(token);
      setConversations(data);
      if (data.length > 0 && !activeConversationId) {
        setActiveConversationId(data[0].id);
      }
    } catch (err) {
      // Silently fail - chat is optional
    }
  };

  const loadMessages = async (conversationId) => {
    try {
      const data = await tideService.getMessages(token, conversationId);
      setMessages(data);
    } catch (err) {
      // Silently fail
    }
  };

  const createNewConversation = async () => {
    try {
      const newConv = await tideService.createConversation(token, 'TIDE Chat');
      setConversations([newConv, ...conversations]);
      setActiveConversationId(newConv.id);
      setMessages([]);
    } catch (err) {
      setError(err.message || 'Failed to create conversation');
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!chatInput.trim() || !activeConversationId || sending) return;

    const userMessage = chatInput.trim();
    setChatInput('');
    setSending(true);

    try {
      await tideService.sendMessage(token, activeConversationId, userMessage);
      await loadMessages(activeConversationId);
    } catch (err) {
      setError(err.message || 'Failed to send message');
      setChatInput(userMessage);
    } finally {
      setSending(false);
    }
  };

  const handleGenerateSummary = async () => {
    if (!selectedInquiry) return;
    setShowSummary(true);
    setAiSummary({ loading: true });
    try {
      const summary = await tideService.getInquirySummary(token, selectedInquiry.id);
      setAiSummary(summary);
    } catch (err) {
      setAiSummary({ error: err.message || 'Failed to generate summary' });
    }
  };

  const handleResponseSubmit = async (e) => {
    e.preventDefault();
    if (!selectedInquiry) return;

    setSubmitting(true);
    setError('');
    setSuccessMessage('');

    try {
      await tideService.respondToInquiry(token, selectedInquiry.id, responseForm);
      setSuccessMessage('Response submitted successfully!');
      await loadInquiries();
      await loadInquiryDetails(selectedInquiry.id);
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      setError(err.message || 'Failed to submit response');
    } finally {
      setSubmitting(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const filteredInquiries = inquiries.filter(i =>
    statusFilter === 'all' || i.status === statusFilter
  );

  const statusCounts = {
    all: inquiries.length,
    submitted: inquiries.filter(i => i.status === 'submitted').length,
    pending_review: inquiries.filter(i => i.status === 'pending_review').length,
    responded: inquiries.filter(i => i.status === 'responded').length,
    accepted: inquiries.filter(i => i.status === 'accepted').length,
    rejected: inquiries.filter(i => i.status === 'rejected').length,
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusIcon = (status) => {
    const icons = {
      submitted: '🔔',
      pending_review: '📋',
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
    <div className="tide-inquiries-container">
      {/* Success Toast */}
      {successMessage && (
        <div className="success-toast">
          <div className="success-toast-icon">✓</div>
          <div className="success-toast-message">{successMessage}</div>
        </div>
      )}

      <div className="tide-layout">
        {/* Left: Inquiry List */}
        <div className="inquiry-sidebar">
          <div className="inquiry-filters-vertical">
            <button
              className={`filter-btn-vertical ${statusFilter === 'submitted' ? 'active' : ''}`}
              onClick={() => setStatusFilter('submitted')}
            >
              🔔 New <span className="filter-count">{statusCounts.submitted}</span>
            </button>
            <button
              className={`filter-btn-vertical ${statusFilter === 'pending_review' ? 'active' : ''}`}
              onClick={() => setStatusFilter('pending_review')}
            >
              📋 In Review <span className="filter-count">{statusCounts.pending_review}</span>
            </button>
            <button
              className={`filter-btn-vertical ${statusFilter === 'responded' ? 'active' : ''}`}
              onClick={() => setStatusFilter('responded')}
            >
              ✅ Responded <span className="filter-count">{statusCounts.responded}</span>
            </button>
            <button
              className={`filter-btn-vertical ${statusFilter === 'accepted' ? 'active' : ''}`}
              onClick={() => setStatusFilter('accepted')}
            >
              🎉 Accepted <span className="filter-count">{statusCounts.accepted}</span>
            </button>
            <button
              className={`filter-btn-vertical ${statusFilter === 'all' ? 'active' : ''}`}
              onClick={() => setStatusFilter('all')}
            >
              All <span className="filter-count">{statusCounts.all}</span>
            </button>
          </div>

          <div className="inquiry-list-scrollable">
            {filteredInquiries.length === 0 ? (
              <div className="inquiry-empty-small">
                <CheckIcon />
                <p>No inquiries</p>
              </div>
            ) : (
              filteredInquiries.map((inquiry) => (
                <div
                  key={inquiry.id}
                  className={`inquiry-item ${selectedInquiry?.id === inquiry.id ? 'active' : ''}`}
                  onClick={() => loadInquiryDetails(inquiry.id)}
                >
                  <div className="inquiry-item-header">
                    <span className="inquiry-icon-small">{getStatusIcon(inquiry.status)}</span>
                    <span className="inquiry-num">#{inquiry.id}</span>
                  </div>
                  <div className="inquiry-item-buyer">{inquiry.buyer_name || 'Unknown Buyer'}</div>
                  <div className="inquiry-item-dataset">{inquiry.dataset_title || 'No dataset'}</div>
                  <div className="inquiry-item-date">{formatDate(inquiry.created_at)}</div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right: Inquiry Details + Chat */}
        <div className="inquiry-main">
          {!selectedInquiry ? (
            <div className="inquiry-placeholder">
              <CheckIcon />
              <h3>Select an inquiry</h3>
              <p>Choose an inquiry from the list to view details and respond</p>
            </div>
          ) : (
            <>
              {error && <div className="alert alert-error">{error}</div>}

              {/* Inquiry Details */}
              <div className="inquiry-details-section">
                <div className="inquiry-header-main">
                  <h2>Inquiry #{selectedInquiry.id}</h2>
                  <span className={`badge-status badge-status-${selectedInquiry.status}`}>
                    {selectedInquiry.status}
                  </span>
                </div>

                <div className="inquiry-info-grid">
                  <div className="info-card">
                    <div className="info-label">
                      <UsersIcon /> Buyer
                    </div>
                    <div className="info-value">{selectedInquiry.buyer_name || 'N/A'}</div>
                  </div>
                  <div className="info-card">
                    <div className="info-label">
                      <DatabaseIcon /> Dataset
                    </div>
                    <div className="info-value">{selectedInquiry.dataset_title || 'N/A'}</div>
                  </div>
                </div>

                <div className="requirements-section">
                  <div className="section-header-with-action">
                    <h4>Buyer Requirements</h4>
                    {!showSummary ? (
                      <button className="btn btn-secondary btn-sm" onClick={handleGenerateSummary}>
                        ✨ AI Summary
                      </button>
                    ) : (
                      <button className="btn btn-secondary btn-sm" onClick={() => setShowSummary(false)}>
                        Show Full
                      </button>
                    )}
                  </div>
                  
                  {showSummary && aiSummary ? (
                    <div className="ai-summary-box">
                      {aiSummary.loading ? (
                        <div className="summary-loading">Generating summary...</div>
                      ) : aiSummary.error ? (
                        <div className="summary-error">{aiSummary.error}</div>
                      ) : (
                        <>
                          <p><strong>Summary:</strong> {aiSummary.summary}</p>
                          {aiSummary.key_requirements && aiSummary.key_requirements.length > 0 && (
                            <>
                              <strong>Key Requirements:</strong>
                              <ul>
                                {aiSummary.key_requirements.map((req, idx) => (
                                  <li key={idx}>{req}</li>
                                ))}
                              </ul>
                            </>
                          )}
                          {aiSummary.recommendation && (
                            <p><strong>Recommendation:</strong> {aiSummary.recommendation}</p>
                          )}
                        </>
                      )}
                    </div>
                  ) : (
                    <pre className="json-display">
                      {JSON.stringify(selectedInquiry.buyer_requirements || {}, null, 2)}
                    </pre>
                  )}
                </div>

                {/* TIDE Chat */}
                <div className="tide-chat-section">
                  <h4>💬 Chat with TIDE Assistant</h4>
                  <div className="tide-chat-box">
                    <div className="chat-messages-small">
                      {messages.length === 0 ? (
                        <div className="chat-hint-small">
                          Ask TIDE to help analyze this inquiry, check work queue, or draft a response...
                        </div>
                      ) : (
                        messages.slice(-5).map((msg) => (
                          <ChatMessage key={msg.id} message={msg} isUser={msg.role === 'user'} />
                        ))
                      )}
                      {sending && (
                        <div className="typing-indicator">
                          <div className="typing-dot"></div>
                          <div className="typing-dot"></div>
                          <div className="typing-dot"></div>
                        </div>
                      )}
                      <div ref={messagesEndRef} />
                    </div>
                    <form className="chat-input-form-small" onSubmit={handleSendMessage}>
                      <input
                        type="text"
                        className="chat-input-small"
                        placeholder="Ask TIDE for help..."
                        value={chatInput}
                        onChange={(e) => setChatInput(e.target.value)}
                        disabled={sending}
                      />
                      <button type="submit" className="btn btn-primary btn-sm" disabled={!chatInput.trim() || sending}>
                        <SendIcon />
                      </button>
                    </form>
                  </div>
                </div>

                {/* Vendor Response Form */}
                <div className="response-form-section">
                  <h4>📤 Your Response</h4>
                  <form onSubmit={handleResponseSubmit}>
                    <div className="form-grid-tide">
                      <div className="form-group">
                        <label className="form-label">Pricing</label>
                        <input
                          type="text"
                          className="form-input"
                          value={responseForm.pricing}
                          onChange={(e) => setResponseForm({ ...responseForm, pricing: e.target.value })}
                          placeholder="e.g., $5,000/month"
                          disabled={submitting || selectedInquiry.status === 'accepted'}
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label">Delivery Method</label>
                        <input
                          type="text"
                          className="form-input"
                          value={responseForm.delivery_method}
                          onChange={(e) => setResponseForm({ ...responseForm, delivery_method: e.target.value })}
                          placeholder="e.g., REST API, S3, FTP"
                          disabled={submitting || selectedInquiry.status === 'accepted'}
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label">Delivery Timeline</label>
                        <input
                          type="text"
                          className="form-input"
                          value={responseForm.delivery_timeline}
                          onChange={(e) => setResponseForm({ ...responseForm, delivery_timeline: e.target.value })}
                          placeholder="e.g., 2-3 business days"
                          disabled={submitting || selectedInquiry.status === 'accepted'}
                        />
                      </div>
                      <div className="form-group full">
                        <label className="form-label">Terms and Conditions</label>
                        <textarea
                          className="form-input"
                          rows={3}
                          value={responseForm.terms_and_conditions}
                          onChange={(e) => setResponseForm({ ...responseForm, terms_and_conditions: e.target.value })}
                          placeholder="Enter terms and conditions..."
                          disabled={submitting || selectedInquiry.status === 'accepted'}
                        />
                      </div>
                      <div className="form-group full">
                        <label className="form-label">Additional Notes</label>
                        <textarea
                          className="form-input"
                          rows={2}
                          value={responseForm.additional_notes}
                          onChange={(e) => setResponseForm({ ...responseForm, additional_notes: e.target.value })}
                          placeholder="Any additional information..."
                          disabled={submitting || selectedInquiry.status === 'accepted'}
                        />
                      </div>
                    </div>
                    <div className="form-actions">
                      <button
                        type="submit"
                        className="btn btn-primary"
                        disabled={submitting || selectedInquiry.status === 'accepted'}
                      >
                        {submitting ? 'Submitting...' : selectedInquiry.status === 'responded' ? 'Update Response' : 'Submit Response'}
                      </button>
                      {selectedInquiry.status === 'accepted' && (
                        <span className="status-note">✅ This inquiry has been accepted by the buyer</span>
                      )}
                    </div>
                  </form>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
