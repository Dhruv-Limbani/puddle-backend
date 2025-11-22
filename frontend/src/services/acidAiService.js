const API_URL = '/api/v1/acid-ai'

export const acidAiService = {
  async query(token, userQuery, history = []) {
    const response = await fetch(`${API_URL}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ 
        query: userQuery,
        history: history.map(msg => ({
          role: msg.role === 'ai' ? 'ai' : 'user', 
          content: msg.content // Simplify to match backend expectation
        }))
      }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to get answer from ACID AI')
    }

    return response.json()
  },
}
