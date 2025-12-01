const API_BASE_URL = '/api/v1'

export const acidService = {
  // Conversations
  async createConversation(token, userId, title = null) {
    const payload = { user_id: userId }
    if (title) payload.title = title
    
    const response = await fetch(`${API_BASE_URL}/acid/conversations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to create conversation' }))
      throw new Error(error.detail || 'Failed to create conversation')
    }

    return await response.json()
  },

  async listConversations(token) {
    const response = await fetch(`${API_BASE_URL}/acid/conversations`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to load conversations' }))
      throw new Error(error.detail || 'Failed to load conversations')
    }

    return await response.json()
  },

  async getConversation(token, conversationId) {
    const response = await fetch(`${API_BASE_URL}/acid/conversations/${conversationId}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to load conversation' }))
      throw new Error(error.detail || 'Failed to load conversation')
    }

    return await response.json()
  },

  async updateConversation(token, conversationId, data) {
    const response = await fetch(`${API_BASE_URL}/acid/conversations/${conversationId}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to update conversation' }))
      throw new Error(error.detail || 'Failed to update conversation')
    }

    return await response.json()
  },

  async deleteConversation(token, conversationId) {
    const response = await fetch(`${API_BASE_URL}/acid/conversations/${conversationId}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok && response.status !== 204) {
      const error = await response.json().catch(() => ({ detail: 'Failed to delete conversation' }))
      throw new Error(error.detail || 'Failed to delete conversation')
    }

    return true
  },

  // Messages
  async sendMessage(token, conversationId, content) {
    const response = await fetch(`${API_BASE_URL}/acid/conversations/${conversationId}/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ content }),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to send message' }))
      throw new Error(error.detail || 'Failed to send message')
    }

    return await response.json()
  },

  async getMessages(token, conversationId) {
    const response = await fetch(`${API_BASE_URL}/acid/conversations/${conversationId}/messages`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to load messages' }))
      throw new Error(error.detail || 'Failed to load messages')
    }

    return await response.json()
  },

  // Inquiries
  async listInquiries(token) {
    const response = await fetch(`${API_BASE_URL}/acid/inquiries`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to load inquiries' }))
      throw new Error(error.detail || 'Failed to load inquiries')
    }

    return await response.json()
  },

  async getInquiry(token, inquiryId) {
    const response = await fetch(`${API_BASE_URL}/acid/inquiries/${inquiryId}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to load inquiry' }))
      throw new Error(error.detail || 'Failed to load inquiry')
    }

    return await response.json()
  },

  async updateInquiry(token, inquiryId, data) {
    const response = await fetch(`${API_BASE_URL}/acid/inquiries/${inquiryId}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to update inquiry' }))
      throw new Error(error.detail || 'Failed to update inquiry')
    }

    return await response.json()
  },
}
