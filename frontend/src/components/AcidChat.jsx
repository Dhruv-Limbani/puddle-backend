import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { acidService } from '../services/acidService';
import ChatMessage from './ChatMessage';
import { PlusIcon, SendIcon, MessageIcon } from './icons';
import './AcidChat.css';

export default function AcidChat() {
  const { token, user } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [editingConversationId, setEditingConversationId] = useState(null);
  const [editingTitle, setEditingTitle] = useState('');
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
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

  const loadConversations = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await acidService.listConversations(token);
      setConversations(data);
      if (data.length > 0 && !activeConversationId) {
        setActiveConversationId(data[0].id);
      }
    } catch (err) {
        const errorMsg = typeof err === 'string' ? err : (err.message || 'Failed to load conversations');
        setError(errorMsg);
        console.error('Error loading conversations:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadMessages = async (conversationId) => {
    try {
      const data = await acidService.getMessages(token, conversationId);
      setMessages(data);
    } catch (err) {
        const errorMsg = typeof err === 'string' ? err : (err.message || 'Failed to load messages');
        setError(errorMsg);
        console.error('Error loading messages:', err);
    }
  };

  const createNewConversation = async () => {
      setError(''); // Clear any previous errors
    try {
      const newConv = await acidService.createConversation(token, user.id, 'New Conversation');
      setConversations([newConv, ...conversations]);
      setActiveConversationId(newConv.id);
      setMessages([]);
      setInputValue('');
    } catch (err) {
      const errorMsg = typeof err === 'string' ? err : (err.message || 'Failed to create conversation');
      setError(errorMsg);
      console.error('Error creating conversation:', err);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || !activeConversationId || sending) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    setSending(true);
    setError('');

    // Optimistically append user's message
    const tempMsg = {
      id: `temp-${Date.now()}`,
      conversation_id: activeConversationId,
      role: 'user',
      content: userMessage,
      created_at: new Date().toISOString(),
    };
    setMessages(prev => [...prev, tempMsg]);

    try {
      const response = await acidService.sendMessage(token, activeConversationId, userMessage);
      // Reload messages to replace temp and include AI reply
      await loadMessages(activeConversationId);
    } catch (err) {
      const errorMsg = typeof err === 'string' ? err : (err.message || 'Failed to send message');
      setError(errorMsg);
      console.error('Error sending message:', err);
      // Rollback optimistic message
      setMessages(prev => prev.filter(m => m.id !== tempMsg.id));
      setInputValue(userMessage); // Restore message on error
    } finally {
      setSending(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const formatDate = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  if (loading) {
    return (
      <div className="loading-state">
        <div className="loading-spinner"></div>
        <p>Loading conversations...</p>
      </div>
    );
  }

  return (
    <div className="acid-chat-container">
      {/* Conversations Sidebar */}
      <div className="conversations-sidebar">
        <div className="sidebar-header">
          <h3>Conversations</h3>
          <button className="btn btn-primary btn-sm" onClick={createNewConversation} title="New Conversation">
            <PlusIcon />
          </button>
        </div>
        <div className="conversations-list">
          {conversations.length === 0 ? (
            <div className="empty-conversations">
              <MessageIcon />
              <p>No conversations yet</p>
              <button className="btn btn-secondary btn-sm" onClick={createNewConversation}>
                Start Chat
              </button>
            </div>
          ) : (
            conversations.map((conv) => (
              <div
                key={conv.id}
                className={`conversation-item ${activeConversationId === conv.id ? 'active' : ''}`}
                onClick={() => setActiveConversationId(conv.id)}
              >
                <div className="conv-title" onDoubleClick={(e) => {
                  e.stopPropagation();
                  setEditingConversationId(conv.id);
                  setEditingTitle(conv.title || '');
                }}>
                  {editingConversationId === conv.id ? (
                    <input
                      className="conv-title-input"
                      value={editingTitle}
                      onChange={(e) => setEditingTitle(e.target.value)}
                      onClick={(e) => e.stopPropagation()}
                      onKeyDown={async (e) => {
                        if (e.key === 'Enter') {
                          try {
                            const updated = await acidService.updateConversation(token, conv.id, { title: editingTitle || 'Untitled Conversation' });
                            setConversations(prev => prev.map(c => c.id === conv.id ? updated : c));
                          } catch (err) {
                            setError(typeof err === 'string' ? err : (err.message || 'Failed to rename conversation'));
                          } finally {
                            setEditingConversationId(null);
                          }
                        } else if (e.key === 'Escape') {
                          setEditingConversationId(null);
                        }
                      }}
                      onBlur={async () => {
                        try {
                          const updated = await acidService.updateConversation(token, conv.id, { title: editingTitle || 'Untitled Conversation' });
                          setConversations(prev => prev.map(c => c.id === conv.id ? updated : c));
                        } catch (err) {
                          setError(typeof err === 'string' ? err : (err.message || 'Failed to rename conversation'));
                        } finally {
                          setEditingConversationId(null);
                        }
                      }}
                      autoFocus
                    />
                  ) : (
                    <span>{conv.title || 'Untitled Conversation'}</span>
                  )}
                </div>
                <div className="conv-date">{formatDate(conv.created_at)}</div>
                <button
                  className="conv-delete-btn"
                  title="Delete conversation"
                  onClick={async (e) => {
                    e.stopPropagation();
                    try {
                      await acidService.deleteConversation(token, conv.id);
                      setConversations(prev => prev.filter(c => c.id !== conv.id));
                      if (activeConversationId === conv.id) {
                        setActiveConversationId(prev => {
                          const remaining = conversations.filter(c => c.id !== conv.id);
                          return remaining.length ? remaining[0].id : null;
                        });
                        setMessages([]);
                      }
                    } catch (err) {
                      setError(typeof err === 'string' ? err : (err.message || 'Failed to delete conversation'));
                    }
                  }}
                >
                  ✕
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Chat Area */}
      <div className="chat-area">
        {!activeConversationId ? (
          <div className="chat-empty-state">
            <MessageIcon />
            <h3>Welcome to ACID Assistant</h3>
            <p>Your AI-powered dataset discovery companion</p>
            <button className="btn btn-primary" onClick={createNewConversation}>
              Start New Conversation
            </button>
          </div>
        ) : (
          <>
            <div className="chat-messages">
              {messages.length === 0 ? (
                <div className="chat-welcome">
                  <h4>👋 Hi! I'm ACID, your dataset discovery assistant</h4>
                  <p>I can help you:</p>
                  <ul>
                    <li>Search for datasets based on your needs</li>
                    <li>Find vendor information and contact details</li>
                    <li>Build and submit data inquiries</li>
                    <li>Track your inquiry status</li>
                  </ul>
                  <p className="chat-hint">Try: "I need financial data for credit risk modeling"</p>
                </div>
              ) : (
                messages.map((msg) => (
                  <ChatMessage key={msg.id} message={msg} isUser={msg.role === 'user'} />
                ))
              )}
              {sending && (
                <div className="chat-message ai-message">
                  <div className="message-avatar">🤖</div>
                  <div className="message-content">
                    <div className="typing-indicator">
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {error && <div className="chat-error">{error}</div>}

            <form className="chat-input-form" onSubmit={handleSendMessage}>
              <input
                type="text"
                className="chat-input"
                placeholder="Type your message..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                disabled={sending}
              />
              <button
                type="submit"
                className="btn btn-primary btn-send"
                disabled={!inputValue.trim() || sending}
              >
                <SendIcon />
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
}
