const API_BASE_URL = '/api/v1'

export const datasetService = {
  async list(token, { limit = 100, offset = 0, search = '', filters = '' } = {}) {
    const params = new URLSearchParams({
      limit: String(limit),
      offset: String(offset),
    })

    if (search) {
      params.append('search', search)
    }

    if (filters) {
      params.append('filters', filters)
    }

    const response = await fetch(`${API_BASE_URL}/datasets/?${params.toString()}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to fetch datasets' }))
      throw new Error(error.detail || 'Failed to fetch datasets')
    }

    return await response.json()
  },

  async get(token, datasetId, opts = {}) {
    // opts: { public: true } to use the public endpoint
    const url = opts.public
      ? `${API_BASE_URL}/datasets/public/${datasetId}`
      : `${API_BASE_URL}/datasets/${datasetId}`;
    const response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to fetch dataset' }))
      throw new Error(error.detail || 'Failed to fetch dataset')
    }

    return await response.json()
  },

  async create(token, payload) {
    const response = await fetch(`${API_BASE_URL}/datasets/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to create dataset' }))
      throw new Error(error.detail?.[0]?.msg || error.detail || 'Failed to create dataset')
    }

    return await response.json()
  },

  async update(token, datasetId, payload) {
    const response = await fetch(`${API_BASE_URL}/datasets/${datasetId}`, {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to update dataset' }))
      throw new Error(error.detail?.[0]?.msg || error.detail || 'Failed to update dataset')
    }

    return await response.json()
  },

  async remove(token, datasetId) {
    const response = await fetch(`${API_BASE_URL}/datasets/${datasetId}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to delete dataset' }))
      throw new Error(error.detail || 'Failed to delete dataset')
    }

    return response.status === 204 ? null : await response.json()
  },
}
