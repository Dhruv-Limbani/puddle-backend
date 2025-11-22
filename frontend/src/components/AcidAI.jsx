import React, { useState, useEffect, useRef } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { acidAiService } from '../services/acidAiService'
import './AcidAI.css'

// Helper to load state from localStorage
const loadState = () => {
  try {
    const saved = localStorage.getItem('acid_ai_chat_state')
    return saved ? JSON.parse(saved) : null
  } catch (e) {
    console.error('Failed to load chat state', e)
    return null
  }
}

export default function AcidAI({ token }) {
  const navigate = useNavigate()
  const location = useLocation()
  
  // Load initial state from localStorage if available, otherwise default
  const savedState = loadState()
  const [messages, setMessages] = useState(savedState?.messages || [
    {
      role: 'ai',
      content: 'Hello! I am ACID AI, your dataset assistant. Ask me anything about our datasets!',
    },
  ])
  
  const [input, setInput] = useState(savedState?.input || '')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  // Save state to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('acid_ai_chat_state', JSON.stringify({ messages, input }))
  }, [messages, input])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim()) return

    const userMessage = input
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }])
    setLoading(true)

    try {
      // Pass conversation history (excluding the latest user message which is passed as query)
      // Filter out error messages and keep format clean
      const history = messages.filter(m => !m.isError).map(m => ({
        role: m.role,
        content: m.content
      }));

      const response = await acidAiService.query(token, userMessage, history)
      
      setMessages((prev) => [
        ...prev,
        {
          role: 'ai',
          content: response.answer,
          data: response.tool_output?.results || [],
        },
      ])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'ai',
          content: 'Sorry, I encountered an error processing your request.',
          isError: true,
        },
      ])
    } finally {
      setLoading(false)
    }
  }
  
  // Clear chat history function (optional, maybe add a button for this later)
  const clearChat = () => {
      setMessages([{
          role: 'ai',
          content: 'Hello! I am ACID AI, your dataset assistant. Ask me anything about our datasets!',
      }])
      localStorage.removeItem('acid_ai_chat_state')
  }

  return (
    <div className="acid-ai-container">
      <div className="chat-sidebar">
        <div className="sidebar-header">
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
            <div>
                <h2>ACID AI</h2>
                <p>Your Dataset Assistant</p>
            </div>
            {/* Optional: Add clear chat button here if needed */}
          </div>
        </div>
        <div className="sidebar-info">
          <p>Ask me about:</p>
          <ul>
            <li>Dataset availability</li>
            <li>Specific domains (Finance, Health)</li>
            <li>Column details</li>
            <li>Pricing and licensing</li>
          </ul>
          
          <button 
            onClick={clearChat}
            style={{
                marginTop: '20px',
                padding: '8px 12px',
                background: '#ffebee',
                color: '#c62828',
                border: '1px solid #ffcdd2',
                borderRadius: '6px',
                fontSize: '12px',
                cursor: 'pointer',
                width: '100%'
            }}
          >
            Clear Conversation
          </button>
        </div>
      </div>
      
      <div className="chat-main">
        <div className="messages-container">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role} ${msg.isError ? 'error' : ''}`}>
              <div className="message-content">
                <p>{msg.content}</p>
              </div>
              
              {msg.data && msg.data.length > 0 && (
                <div className="dataset-results-grid">
                  {msg.data.map((dataset) => (
                    <div 
                      key={dataset.id} 
                      className="result-card"
                      onClick={() => {
                          // Save scroll position or state if needed before navigating
                          navigate(`/marketplace/dataset/${dataset.id}`)
                      }}
                      style={{ cursor: 'pointer' }}
                    >
                      <div className="result-header">
                        <h4>{dataset.title}</h4>
                        <span className="similarity-score">
                          {Math.round(dataset.similarity_score * 100)}% Match
                        </span>
                      </div>
                      <p className="result-desc">{dataset.description}</p>
                      <div className="result-meta">
                        <span className="badge">{dataset.domain}</span>
                        <span className="badge">{dataset.price}</span>
                      </div>
                      {dataset.columns && dataset.columns.length > 0 && (
                        <div className="columns-preview">
                          <strong>Columns:</strong> {dataset.columns.map(c => c.name).slice(0, 3).join(', ')}
                          {dataset.columns.length > 3 && '...'}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="message ai loading">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form className="chat-input-area" onSubmit={handleSubmit}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about datasets..."
            disabled={loading}
          />
          <button type="submit" disabled={loading || !input.trim()}>
            Send
          </button>
        </form>
      </div>
    </div>
  )
}
