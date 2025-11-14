const API_BASE_URL = '/api/v1'

export const agentService = {
  async list(token, { vendorId = '', active = '' } = {}) {
    const params = new URLSearchParams()

    if (vendorId) {
      params.append('vendor_id', vendorId)
    }

    if (active !== '') {
      params.append('active', String(active))
    }

    const query = params.toString()
    const url = query ? `${API_BASE_URL}/agents/?${query}` : `${API_BASE_URL}/agents/`

    const response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to fetch agents' }))
      throw new Error(error.detail || 'Failed to fetch agents')
    }

    return await response.json()
  },

  async create(token, payload) {
    const response = await fetch(`${API_BASE_URL}/agents/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to create agent' }))
      throw new Error(error.detail?.[0]?.msg || error.detail || 'Failed to create agent')
    }

    return await response.json()
  },

  async update(token, agentId, payload) {
    const response = await fetch(`${API_BASE_URL}/agents/${agentId}`, {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to update agent' }))
      throw new Error(error.detail?.[0]?.msg || error.detail || 'Failed to update agent')
    }

    return await response.json()
  },

  async remove(token, agentId) {
    const response = await fetch(`${API_BASE_URL}/agents/${agentId}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to delete agent' }))
      throw new Error(error.detail || 'Failed to delete agent')
    }

    return response.status === 204 ? null : await response.json()
  },
}
