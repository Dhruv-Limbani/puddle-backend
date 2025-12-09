import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { tideService } from '../services/tideService';
import TideChatMessage from './TideChatMessage';
import { DatabaseIcon, UsersIcon, SendIcon, MessageIcon, CheckIcon, BotIcon } from './icons';
import './TideInquiries.css';

export default function TideInquiries({ onNavigateToDataset }) {
  const { token, user } = useAuth();
  const navigate = useNavigate();
  const [inquiries, setInquiries] = useState([]);
  const [selectedInquiry, setSelectedInquiry] = useState(null);
  const [selectedInquiryDetails, setSelectedInquiryDetails] = useState(null); // Full detail response
  const [statusFilter, setStatusFilter] = useState('submitted');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // TIDE Chat state (simple stateless messages for UI)
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

  useEffect(() => {
    loadInquiries();
  }, [token]);

  useEffect(() => {
    if (selectedInquiry) {
      // Clear messages when switching inquiries
      setMessages([]);
    }
  }, [selectedInquiry]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadInquiries = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await tideService.listInquiries(token);
      console.log('📋 Loaded inquiries:', data);
      if (data && data.length > 0) {
        console.log('📋 First inquiry keys:', Object.keys(data[0]));
        console.log('📋 First inquiry buyer_name:', data[0].buyer_name);
        console.log('📋 First inquiry dataset_title:', data[0].dataset_title);
      }
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
      // Backend returns { inquiry, dataset, buyer_info }
      setSelectedInquiry(data.inquiry || data);
      setSelectedInquiryDetails(data); // Store full response
      setResponseForm({
        pricing: data.inquiry?.vendor_response?.pricing || data.vendor_response?.pricing || '',
        delivery_method: data.inquiry?.vendor_response?.delivery_method || data.vendor_response?.delivery_method || '',
        delivery_timeline: data.inquiry?.vendor_response?.delivery_timeline || data.vendor_response?.delivery_timeline || '',
        terms_and_conditions: data.inquiry?.vendor_response?.terms_and_conditions || data.vendor_response?.terms_and_conditions || '',
        additional_notes: data.inquiry?.vendor_response?.additional_notes || data.vendor_response?.additional_notes || '',
      });
    } catch (err) {
      setError(err.message || 'Failed to load inquiry details');
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    console.log('handleSendMessage called', { chatInput, selectedInquiry: selectedInquiry?.id, sending });
    if (!chatInput.trim() || !selectedInquiry || sending) {
      console.log('Message send blocked:', { 
        hasInput: !!chatInput.trim(), 
        hasInquiry: !!selectedInquiry, 
        isSending: sending 
      });
      return;
    }

    const userMessage = chatInput.trim();
    setChatInput('');
    setSending(true);
    setError('');

    // Optimistically append user's message
    const tempUserMsg = {
      id: `temp-user-${Date.now()}`,
      role: 'user',
      content: userMessage,
      created_at: new Date().toISOString(),
    };
    setMessages(prev => [...prev, tempUserMsg]);

    try {
      console.log('Sending message to TIDE for inquiry:', selectedInquiry.id);
      const response = await tideService.sendChatMessage(token, selectedInquiry.id, userMessage);
      console.log('TIDE response received:', response);
      
      // Add AI response to messages
      const aiMsg = {
        id: `ai-${Date.now()}`,
        role: 'assistant',
        content: response.content,
        tool_call: response.tool_calls ? { calls: response.tool_calls } : null,
        created_at: new Date().toISOString(),
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch (err) {
      console.error('Failed to send message:', err);
      setError(err.message || 'Failed to send message');
      // Rollback on error
      setMessages(prev => prev.filter(m => m.id !== tempUserMsg.id));
      setChatInput(userMessage);
    } finally {
      setSending(false);
    }
  };

  const handleResponseSubmit = async (e) => {
    e.preventDefault();
    if (!selectedInquiry) return;

    setSubmitting(true);
    setError('');

    try {
      await tideService.respondToInquiry(token, selectedInquiry.id, responseForm);
      await loadInquiries();
      await loadInquiryDetails(selectedInquiry.id);
    } catch (err) {
      setError(err.message || 'Failed to submit response');
    } finally {
      setSubmitting(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleDatasetClick = () => {
    if (selectedInquiryDetails?.dataset?.id && onNavigateToDataset) {
      onNavigateToDataset(selectedInquiryDetails.dataset.id);
    }
  };

  const filteredInquiries = inquiries.filter(i =>
    statusFilter === 'all' || i.status === statusFilter
  );

  const statusCounts = {
    all: inquiries.length,
    submitted: inquiries.filter(i => i.status === 'submitted').length,
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
      <div className="tide-layout">
        {/* Left: Inquiry Sidebar */}
        <div className="inquiry-sidebar">
          <div className="inquiry-filters-vertical">
            <button
              className={`filter-btn-vertical ${statusFilter === 'submitted' ? 'active' : ''}`}
              onClick={() => setStatusFilter('submitted')}
            >
              🔔 New <span className="filter-count">{statusCounts.submitted}</span>
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

        {/* Right: Inquiry Details + TIDE Chat */}
        <div className="inquiry-main">
          {!selectedInquiry ? (
            <div className="inquiry-placeholder">
              <MessageIcon />
              <h3>Select an inquiry</h3>
              <p>Choose an inquiry from the list to view details and chat with TIDE</p>
            </div>
          ) : (
            <div className="inquiry-detail-container">
              {/* 1. Buyer Details */}
              <div className="detail-card">
                <h3 className="card-title">
                  <UsersIcon /> Buyer Information
                </h3>
                <div className="buyer-info-grid">
                  <div className="info-item">
                    <span className="info-label">Name</span>
                    <span className="info-value">{selectedInquiryDetails?.buyer_info?.name || 'N/A'}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Organization</span>
                    <span className="info-value">{selectedInquiryDetails?.buyer_info?.organization || 'N/A'}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Industry</span>
                    <span className="info-value">{selectedInquiryDetails?.buyer_info?.industry || 'N/A'}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Inquiry ID</span>
                    <span className="info-value">#{selectedInquiry.id}</span>
                  </div>
                </div>
              </div>

              {/* 2. Dataset Details (Clickable) */}
              <div className="detail-card clickable-card" onClick={handleDatasetClick}>
                <h3 className="card-title">
                  <DatabaseIcon /> Dataset Information
                </h3>
                <div className="dataset-info">
                  <h4 className="dataset-title">{selectedInquiryDetails?.dataset?.title || 'No dataset linked'}</h4>
                  {selectedInquiryDetails?.dataset?.description && (
                    <p className="dataset-description">{selectedInquiryDetails.dataset.description}</p>
                  )}
                  {selectedInquiryDetails?.dataset?.id && (
                    <span className="view-dataset-hint">Click to view dataset profile →</span>
                  )}
                </div>
              </div>

              {/* 3. Inquiry Summary */}
              {selectedInquiry.summary && (
                <div className="detail-card">
                  <h3 className="card-title">📄 Inquiry Summary</h3>
                  <div className="summary-content">
                    <p>{selectedInquiry.summary}</p>
                  </div>
                </div>
              )}

              {/* 4. TIDE Chat UI */}
              <div className="detail-card tide-chat-card">
                <h3 className="card-title">
                  💬 Chat with TIDE Assistant
                </h3>
                <p className="card-subtitle">
                  TIDE can help you analyze this inquiry and draft a response specific to this buyer's needs.
                </p>
                
                <div className="tide-chat-container">
                  <div className="tide-chat-messages">
                    {messages.length === 0 ? (
                      <div className="chat-welcome-tide">
                        <div className="chat-welcome-icon">
                          <BotIcon />
                        </div>
                        <h4>Hi! I'm TIDE, your vendor assistant</h4>
                        <p>I can help you with this inquiry:</p>
                        <ul>
                          <li>Analyze buyer requirements</li>
                          <li>Draft professional responses</li>
                          <li>Suggest pricing and delivery terms</li>
                        </ul>
                        <div className="chat-hint">Try: "Help me analyze this inquiry"</div>
                      </div>
                    ) : (
                      <>
                        <div className="date-separator"><span>Today</span></div>
                        {messages.map((msg) => (
                          <TideChatMessage key={msg.id} message={msg} isUser={msg.role === 'user'} />
                        ))}
                      </>
                    )}
                    
                    {sending && (
                      <div className="tide-typing-message tide-align-left">
                        <div className="tide-message-avatar">
                          <BotIcon />
                        </div>
                        <div className="tide-message-content">
                          <div className="tide-typing-indicator">
                            <div className="tide-typing-dot"></div>
                            <div className="tide-typing-dot"></div>
                            <div className="tide-typing-dot"></div>
                          </div>
                        </div>
                      </div>
                    )}
                    
                    <div ref={messagesEndRef} />
                  </div>

                  <div className="tide-chat-input-container">
                    <form className="tide-chat-input-form" onSubmit={handleSendMessage}>
                      <input
                        type="text"
                        className="tide-chat-input"
                        placeholder="Ask TIDE for help with this inquiry..."
                        value={chatInput}
                        onChange={(e) => setChatInput(e.target.value)}
                        disabled={sending}
                      />
                      <button 
                        type="submit" 
                        className="btn-send-tide" 
                        disabled={!chatInput.trim() || sending}
                        onClick={(e) => console.log('Send button clicked', e)}
                      >
                        <SendIcon />
                      </button>
                    </form>
                    <div className="chat-disclaimer-tide">
                      TIDE can make mistakes. Verify critical information independently.
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
