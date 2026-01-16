import io from 'socket.io-client';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.listeners = new Map();
    this.isConnected = false;
  }

  connect(url = 'http://localhost:5000') {
    if (this.socket) {
      this.disconnect();
    }

    this.socket = io(url, {
      transports: ['websocket', 'polling'],
      timeout: 5000,
    });

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
      this.isConnected = true;
      this.emit('connection', { status: 'connected' });
    });

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected');
      this.isConnected = false;
      this.emit('connection', { status: 'disconnected' });
    });

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
      this.isConnected = false;
      this.emit('connection', { status: 'error', error });
    });

    // Listen for simulation updates
    this.socket.on('simulation_progress', (data) => {
      this.emit('simulation_progress', data);
    });

    this.socket.on('simulation_complete', (data) => {
      this.emit('simulation_complete', data);
    });

    this.socket.on('blockchain_transaction', (data) => {
      this.emit('blockchain_transaction', data);
    });

    this.socket.on('system_metrics', (data) => {
      this.emit('system_metrics', data);
    });

    return this.socket;
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
    }
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event).add(callback);

    // Return unsubscribe function
    return () => {
      const eventListeners = this.listeners.get(event);
      if (eventListeners) {
        eventListeners.delete(callback);
      }
    };
  }

  off(event, callback) {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      eventListeners.delete(callback);
    }
  }

  emit(event, data) {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      eventListeners.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in WebSocket event listener for ${event}:`, error);
        }
      });
    }
  }

  send(event, data) {
    if (this.socket && this.isConnected) {
      this.socket.emit(event, data);
    } else {
      console.warn('WebSocket not connected, cannot send:', event, data);
    }
  }

  getConnectionStatus() {
    return {
      connected: this.isConnected,
      socket: !!this.socket
    };
  }
}

// Create singleton instance
export const webSocketService = new WebSocketService();
export default webSocketService;
