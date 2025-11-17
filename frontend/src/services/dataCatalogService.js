// Based on your database schema and API conventions

const API_BASE_URL = '/api/v1';

/**
 * Handles the logic of parsing API responses, especially errors.
 */
async function handleResponse(response) {
  if (!response.ok) {
    const error = await response.json().catch(() => ({
      detail: `HTTP Error: ${response.status} ${response.statusText}`,
    }));
    // Handle nested validation errors
    if (Array.isArray(error.detail)) {
      throw new Error(error.detail[0].msg || 'Validation error');
    }
    throw new Error(error.detail || 'An unknown API error occurred');
  }
  // Handle 204 No Content for DELETE
  if (response.status === 204) {
    return null;
  }
  return response.json();
}

export const dataCatalogService = {
  /**
   * Lists all datasets for the authenticated vendor.
   * Assumes the backend filters datasets based on the token.
   * @param {string} token - The JWT auth token.
   * @returns {Promise<Array>} - A promise that resolves to an array of datasets.
   */
  async listDatasets(token) {
    const response = await fetch(`${API_BASE_URL}/datasets/me/`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    return handleResponse(response);
  },

  /**
   * Gets a single dataset and its columns.
   * Assumes the backend joins and returns dataset_columns.
   * @param {string} token - The JWT auth token.
   * @param {string} datasetId - The UUID of the dataset.
   * @returns {Promise<Object>} - A promise that resolves to the dataset object with a 'columns' array.
   */
  async getDatasetDetails(token, datasetId) {
    const response = await fetch(`${API_BASE_URL}/datasets/${datasetId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    return handleResponse(response);
  },

  /**
   * Creates a new dataset.
   * Assumes the backend can handle a nested 'columns' array in the payload
   * and create the associated dataset_columns records.
   * @param {string} token - The JWT auth token.
   * @param {Object} data - The dataset payload, including a 'columns' array.
   * @returns {Promise<Object>} - A promise that resolves to the new dataset object.
   */
  async createDataset(token, data) {
    const response = await fetch(`${API_BASE_URL}/datasets/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  /**
   * Updates an existing dataset and its columns.
   * Assumes the backend handles updating/creating/deleting columns
   * based on the provided 'columns' array.
   * @param {string} token - The JWT auth token.
   * @param {string} datasetId - The UUID of the dataset to update.
   * @param {Object} data - The dataset payload, including a 'columns' array.
   * @returns {Promise<Object>} - A promise that resolves to the updated dataset object.
   */
  async updateDataset(token, datasetId, data) {
    const response = await fetch(`${API_BASE_URL}/datasets/${datasetId}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  /**
   * Deletes a dataset.
   * Assumes the backend will cascade delete associated dataset_columns.
   * @param {string} token - The JWT auth token.
   * @param {string} datasetId - The UUID of the dataset to delete.
   * @returns {Promise<null>} - A promise that resolves when deletion is successful.
   */
  async deleteDataset(token, datasetId) {
    const response = await fetch(`${API_BASE_URL}/datasets/${datasetId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    return handleResponse(response);
  },
};