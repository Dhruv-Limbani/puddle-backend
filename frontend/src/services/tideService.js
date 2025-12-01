const API_BASE_URL = '/api/v1'

export const tideService = {
  // Inquiries
  async listInquiries(token) {
    const response = await fetch(`${API_BASE_URL}/tide/inquiries`, {
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
    const response = await fetch(`${API_BASE_URL}/tide/inquiries/${inquiryId}`, {
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

  async respondToInquiry(token, inquiryId, responseData) {
    const response = await fetch(`${API_BASE_URL}/tide/inquiries/${inquiryId}/respond`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(responseData),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to submit response' }))
      throw new Error(error.detail || 'Failed to submit response')
    }

    return await response.json()
  },

  async getInquirySummary(token, inquiryId) {
    const response = await fetch(`${API_BASE_URL}/tide/inquiries/${inquiryId}/summary`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to generate summary' }))
      throw new Error(error.detail || 'Failed to generate summary')
    }

    return await response.json()
  },

  // Simple stateless chat for TIDE
  async sendChatMessage(token, inquiryId, content) {
    const response = await fetch(`${API_BASE_URL}/tide/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ inquiry_id: inquiryId, content }),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to send message' }))
      throw new Error(error.detail || 'Failed to send message')
    }

    return await response.json()
  },
}
