const API_BASE_URL = '/api/v1'

export const buyerService = {
  async getProfile(token) {
    const response = await fetch(`${API_BASE_URL}/buyers/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (response.status === 404) {
      return null
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to fetch buyer profile' }))
      throw new Error(error.detail || 'Failed to fetch buyer profile')
    }

    return await response.json()
  },

  async createProfile(token, payload) {
    const response = await fetch(`${API_BASE_URL}/buyers/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to create buyer profile' }))
      throw new Error(error.detail?.[0]?.msg || error.detail || 'Failed to create buyer profile')
    }

    return await response.json()
  },

  async updateProfile(token, payload) {
    const response = await fetch(`${API_BASE_URL}/buyers/me`, {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to update buyer profile' }))
      throw new Error(error.detail?.[0]?.msg || error.detail || 'Failed to update buyer profile')
    }

    return await response.json()
  },
}