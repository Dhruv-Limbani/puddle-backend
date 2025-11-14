const API_BASE_URL = '/api/v1'

export const authService = {
  async signup(email, password, role, fullName = null) {
    const params = new URLSearchParams({
      email,
      password,
      role,
    })
    if (fullName) {
      params.append('full_name', fullName)
    }

    const response = await fetch(`${API_BASE_URL}/auth/register?${params}`, {
      method: 'POST',
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Registration failed' }))
      throw new Error(error.detail?.[0]?.msg || error.detail || 'Registration failed')
    }

    return await response.json()
  },

  async login(email, password) {
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Login failed' }))
      throw new Error(error.detail || 'Invalid email or password')
    }

    return await response.json()
  },

  async getCurrentUser(token) {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      throw new Error('Failed to get user data')
    }

    return await response.json()
  },
}

