import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

class ApiService {
  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.baseUrl = API_BASE_URL;

    // Add response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error);
        throw error;
      }
    );
  }

  // System Status
  async getSystemStatus() {
    const response = await this.api.get('/api/status');
    return response.data;
  }

  // Simulation Control
  async startSimulation(config) {
    const response = await this.api.post('/api/simulation/start', config);
    return response.data;
  }

  async stopSimulation() {
    const response = await this.api.post('/api/simulation/stop');
    return response.data;
  }

  async getSimulationStatus() {
    const response = await this.api.get('/api/simulation/status');
    return response.data;
  }

  async getSimulationProgress() {
    const response = await this.api.get('/api/simulation/progress');
    return response.data;
  }

  // Analytics and Metrics
  async getSimulationMetrics() {
    const response = await this.api.get('/api/analytics/metrics');
    return response.data;
  }

  async getTransactionHistory() {
    const response = await this.api.get('/api/analytics/transactions');
    return response.data;
  }

  async getAgentData() {
    const response = await this.api.get('/api/analytics/agents');
    return response.data;
  }

  async getMarketData() {
    const response = await this.api.get('/api/analytics/market');
    return response.data;
  }

  // Blockchain Status
  async getBlockchainStatus() {
    const response = await this.api.get('/api/blockchain/status');
    return response.data;
  }

  async getContractAddresses() {
    const response = await this.api.get('/api/blockchain/contracts');
    return response.data;
  }

  async getRecentTransactions() {
    const response = await this.api.get('/api/blockchain/transactions/recent');
    return response.data;
  }

  // Real-time data (for WebSocket fallback)
  async getRealTimeData() {
    const response = await this.api.get('/api/realtime/data');
    return response.data;
  }

  // Configuration
  async getDefaultConfig() {
    const response = await this.api.get('/api/config/default');
    return response.data;
  }

  async saveConfig(config) {
    const response = await this.api.post('/api/config/save', config);
    return response.data;
  }

  async loadConfig(configName) {
    const response = await this.api.get(`/api/config/load/${configName}`);
    return response.data;
  }

  // File operations
  async getSimulationResults() {
    const response = await this.api.get('/api/files/results');
    return response.data;
  }

  async downloadResults(filename) {
    const response = await this.api.get(`/api/files/download/${filename}`, {
      responseType: 'blob'
    });
    return response.data;
  }

  fileDownloadUrl(filename) {
    return `${this.baseUrl}/api/files/download/${filename}`;
  }

  // Research results
  async getResultsLog() {
    const response = await this.api.get('/api/results/log');
    return response.data;
  }

  // Bundle API methods
  async getBundlesList(limit = 50, offset = 0) {
    const response = await this.api.get(`/api/bundles/list?limit=${limit}&offset=${offset}`);
    return response.data;
  }

  async getBundleStats() {
    const response = await this.api.get('/api/bundles/stats');
    return response.data;
  }

  async getBundleDetails(bundleId) {
    const response = await this.api.get(`/api/bundles/details/${bundleId}`);
    return response.data;
  }

  async getRecentBundles(limit = 10) {
    const response = await this.api.get(`/api/bundles/recent?limit=${limit}`);
    return response.data;
  }

  // Health check
  async healthCheck() {
    try {
      const response = await this.api.get('/api/health');
      return response.data;
    } catch (error) {
      return { status: 'error', message: error.message };
    }
  }

  // Database Explorer API methods
  async getDatabaseData(table) {
    const response = await this.api.get(`/api/database/${table}`);
    return response.data;
  }

  async getDatabaseStats() {
    const response = await this.api.get('/api/database/stats');
    return response.data;
  }

  async exportDatabaseTable(table, format = 'excel', runId = null) {
    const params = new URLSearchParams();
    if (runId) params.append('run_id', runId);

    const response = await this.api.get(
      `/api/database/export/${table}/${format}?${params.toString()}`,
      { responseType: 'blob' }
    );
    return response.data;
  }

  async exportBlockchainData(format = 'excel') {
    const response = await this.api.get(
      `/api/blockchain/export/${format}`,
      { responseType: 'blob' }
    );
    return response.data;
  }

  async getAllSimulationRuns() {
    const response = await this.api.get('/api/database/runs');
    return response.data;
  }
}

const apiServiceInstance = new ApiService();
export { apiServiceInstance as ApiService };
export default apiServiceInstance;
