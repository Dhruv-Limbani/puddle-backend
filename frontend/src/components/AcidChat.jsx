import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { acidService } from '../services/acidService';
import ChatMessage from './ChatMessage';
import ConfirmationModal from './ConfirmationModal';
import { PlusIcon, SendIcon, MessageIcon, BotIcon } from './icons';
import './AcidChat.css';
import './ChatMessage.css'; // Ensure animation styles are loaded

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
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [conversationToDelete, setConversationToDelete] = useState(null);
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
  }, [messages, sending]); 

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
    } finally {
      setLoading(false);
    }
  };

  const loadMessages = async (conversationId) => {
    try {
      const data = await acidService.getMessages(token, conversationId);
      setMessages(data);
    } catch (err) {
        setError(typeof err === 'string' ? err : (err.message || 'Failed to load messages'));
    }
  };

  const createNewConversation = async () => {
    setError('');
    try {
      const newConv = await acidService.createConversation(token, user.id, 'New Conversation');
      setConversations([newConv, ...conversations]);
      setActiveConversationId(newConv.id);
      setMessages([]);
      setInputValue('');
    } catch (err) {
      setError(typeof err === 'string' ? err : (err.message || 'Failed to create conversation'));
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
      await acidService.sendMessage(token, activeConversationId, userMessage);
      await loadMessages(activeConversationId);
    } catch (err) {
      setError(typeof err === 'string' ? err : (err.message || 'Failed to send message'));
      // Rollback on error
      setMessages(prev => prev.filter(m => m.id !== tempMsg.id));
      setInputValue(userMessage);
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
    const diffMins = Math.floor((now - date) / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const handleDeleteConversation = async () => {
    if (!conversationToDelete) return;
    
    try {
      await acidService.deleteConversation(token, conversationToDelete.id);
      setConversations(prev => prev.filter(c => c.id !== conversationToDelete.id));
      if (activeConversationId === conversationToDelete.id) {
        const remaining = conversations.filter(c => c.id !== conversationToDelete.id);
        setActiveConversationId(remaining.length > 0 ? remaining[0].id : null);
        setMessages([]);
      }
    } catch (err) {
      setError(typeof err === 'string' ? err : (err.message || 'Failed to delete conversation'));
    } finally {
      setDeleteModalOpen(false);
      setConversationToDelete(null);
    }
  };

  return (
    <div className="acid-chat-container">
      {/* Sidebar */}
      <div className="conversations-sidebar">
        <div className="conv-sidebar-header">
          <button className="btn-new-chat" onClick={createNewConversation} title="New Conversation">
            <PlusIcon />
            <span>New Chat</span>
          </button>
        </div>
        
        <div className="sidebar-section-label">History</div>
        
        <div className="conversations-list">
          {loading ? (
            <div style={{padding: '20px', textAlign: 'center', color: '#94a3b8', fontSize: '13px'}}>Loading...</div>
          ) : conversations.length === 0 ? (
            <div style={{padding: '20px', textAlign: 'center', color: '#94a3b8', fontSize: '13px'}}>No history yet</div>
          ) : (
            conversations.map((conv) => (
              <div
                key={conv.id}
                className={`conversation-item ${activeConversationId === conv.id ? 'active' : ''}`}
                onClick={() => setActiveConversationId(conv.id)}
              >
                <div className="conv-content">
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
                        onBlur={async () => {
                          if (editingTitle.trim() && editingTitle !== conv.title) {
                            try {
                              await acidService.updateConversation(token, conv.id, { title: editingTitle.trim() });
                              await loadConversations();
                            } catch (err) {
                              setError(typeof err === 'string' ? err : (err.message || 'Failed to update conversation'));
                            }
                          }
                          setEditingConversationId(null);
                        }}
                        autoFocus
                        onKeyDown={async (e) => {
                          if (e.key === 'Enter') {
                            if (editingTitle.trim() && editingTitle !== conv.title) {
                              try {
                                await acidService.updateConversation(token, conv.id, { title: editingTitle.trim() });
                                await loadConversations();
                              } catch (err) {
                                setError(typeof err === 'string' ? err : (err.message || 'Failed to update conversation'));
                              }
                            }
                            setEditingConversationId(null);
                          } else if (e.key === 'Escape') {
                            setEditingConversationId(null);
                          }
                        }}
                      />
                    ) : (
                      <span>{conv.title || 'Untitled'}</span>
                    )}
                  </div>
                  <div className="conv-date">{formatDate(conv.created_at)}</div>
                </div>
                <button
                  className="conv-delete-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    setConversationToDelete(conv);
                    setDeleteModalOpen(true);
                  }}
                  title="Delete conversation"
                >
                  ✕
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="chat-area">
        {!activeConversationId ? (
          <div className="chat-welcome">
            <h4>ACID Assistant</h4>
            <p>Select a conversation to start.</p>
            <button className="btn btn-primary" onClick={createNewConversation}>Start New</button>
          </div>
        ) : (
          <>
            <div className="chat-messages">
              {messages.length === 0 ? (
                <div className="chat-welcome">
                  <h4>👋 Hi! I'm ACID</h4>
                  <p>I can help you find the right datasets.</p>
                  <div className="chat-hint">Try "I need financial data for Q3 2024"</div>
                </div>
              ) : (
                <>
                  <div className="date-separator"><span>Today</span></div>
                  {messages.map((msg) => (
                    <ChatMessage key={msg.id} message={msg} isUser={msg.role === 'user'} />
                  ))}
                </>
              )}
              
              {/* Typing Animation Block */}
              {sending && (
                <div className="chat-message ai-message align-left">
                  <div className="message-avatar">
                    <BotIcon />
                  </div>
                  <div className="message-content typing-message">
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

            <div className="chat-input-container">
              <form className="chat-input-form" onSubmit={handleSendMessage}>
                <input
                  type="text"
                  className="chat-input"
                  placeholder="Ask ACID..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  disabled={sending}
                />
                <button type="submit" className="btn-send" disabled={!inputValue.trim() || sending}>
                  <SendIcon />
                </button>
              </form>
              <div className="chat-disclaimer">
                ACID can make mistakes. Verify critical dataset information independently.
              </div>
            </div>
          </>
        )}
      </div>

      <ConfirmationModal
        isOpen={deleteModalOpen}
        onClose={() => {
          setDeleteModalOpen(false);
          setConversationToDelete(null);
        }}
        onConfirm={handleDeleteConversation}
        title="Delete this conversation?"
        message="This action cannot be undone. All messages in this conversation will be permanently deleted."
        confirmText="Delete"
        cancelText="Cancel"
      />
    </div>
  );
}