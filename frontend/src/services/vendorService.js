const API_BASE_URL = '/api/v1'

export const vendorService = {
  async getMe(token) {
    const response = await fetch(`${API_BASE_URL}/vendors/me/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to fetch vendor profile' }))
      throw new Error(error.detail || 'Failed to fetch vendor profile')
    }

    return await response.json()
  },

  async list(token) {
    const response = await fetch(`${API_BASE_URL}/vendors/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to fetch vendors' }))
      throw new Error(error.detail || 'Failed to fetch vendors')
    }

    return await response.json()
  },

  async get(token, vendorId) {
    const response = await fetch(`${API_BASE_URL}/vendors/${vendorId}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to fetch vendor' }))
      throw new Error(error.detail || 'Failed to fetch vendor')
    }

    return await response.json()
  },

  async create(token, payload) {
    const response = await fetch(`${API_BASE_URL}/vendors/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to create vendor profile' }))
      throw new Error(error.detail?.[0]?.msg || error.detail || 'Failed to create vendor profile')
    }

    return await response.json()
  },

  async update(token, vendorId, payload) {
    const response = await fetch(`${API_BASE_URL}/vendors/${vendorId}`, {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to update vendor profile' }))
      throw new Error(error.detail?.[0]?.msg || error.detail || 'Failed to update vendor profile')
    }

    return await response.json()
  },

  async remove(token, vendorId) {
    const response = await fetch(`${API_BASE_URL}/vendors/${vendorId}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to delete vendor profile' }))
      throw new Error(error.detail || 'Failed to delete vendor profile')
    }

    return response.status === 204 ? null : await response.json()
  },
}
