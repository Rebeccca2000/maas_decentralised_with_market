# 🌐 React Web Interface Setup Guide

This guide explains how to run the MaaS Decentralized Platform with the new React web interface while maintaining the existing Python CLI functionality.

## 🚀 Quick Start

### Option 1: Full Web Interface (Recommended)
```bash
# Install all dependencies
npm install
pip install -r backend/requirements.txt

# Start all services (Hardhat + Backend + React)
npm run dev-full
```

### Option 2: Web Interface Only (Blockchain already running)
```bash
# Start backend and React frontend
npm run dev
```

### Option 3: Traditional CLI Mode (Original functionality)
```bash
# Run simulation directly with Python (as before)
python abm/agents/run_decentralized_model.py --debug
```

## 📋 Prerequisites

- **Node.js** v16+ and npm
- **Python** 3.8+ with pip
- **Git** for version control

## 🔧 Installation Steps

### 1. Install Dependencies

```bash
# Install Node.js dependencies (React + Hardhat)
npm install

# Install Python dependencies (Backend + Simulation)
pip install -r backend/requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings (optional for local development)
```

### 3. Start Services

#### Option A: All-in-One Development
```bash
# Starts Hardhat node, backend API, and React frontend
npm run dev-full
```

This will open:
- **Hardhat Node**: http://127.0.0.1:8545
- **Backend API**: http://localhost:5000
- **React Frontend**: http://localhost:3000

#### Option B: Individual Services
```bash
# Terminal 1: Start Hardhat blockchain node
npm run start-hardhat

# Terminal 2: Start Python backend API
npm run start-backend

# Terminal 3: Start React frontend
npm start
```

## 🌟 Features

### Web Interface
- **📊 Real-time Dashboard**: Monitor simulation progress and system status
- **🎮 Simulation Control**: Start/stop simulations with custom parameters
- **📈 Interactive Analytics**: View charts and metrics in real-time
- **⛓️ Blockchain Status**: Monitor contracts and transactions
- **🎯 Preset Configurations**: Quick-start with predefined simulation settings

### CLI Interface (Preserved)
- **All existing functionality maintained**
- **Command-line arguments work as before**
- **Direct Python execution supported**

## 📱 Usage

### Web Interface

1. **Open Browser**: Navigate to http://localhost:3000
2. **Check Status**: Verify backend and blockchain connections in header
3. **Start Simulation**: Go to Simulation tab, configure parameters, and start
4. **Monitor Progress**: Watch real-time updates on Dashboard
5. **View Results**: Check Analytics tab for detailed insights

### CLI Interface (Original)

```bash
# Debug mode (5 commuters, 3 providers, 20 steps)
python abm/agents/run_decentralized_model.py --debug

# Custom parameters
python abm/agents/run_decentralized_model.py --steps 100 --commuters 20 --providers 10

# Fast execution without plots
python abm/agents/run_decentralized_model.py --debug --no-plots
```

## 🔄 Available Scripts

| Script | Description |
|--------|-------------|
| `npm start` | Start React frontend only |
| `npm run start-backend` | Start Python backend API |
| `npm run start-hardhat` | Start Hardhat blockchain node |
| `npm run dev` | Start backend + frontend |
| `npm run dev-full` | Start all services (blockchain + backend + frontend) |
| `npm run build` | Build React app for production |
| `npm run deploy-contracts` | Deploy smart contracts |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (Port 3000)              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Dashboard     │  │   Simulation    │  │  Analytics  │ │
│  │   - Status      │  │   - Control     │  │  - Charts   │ │
│  │   - Metrics     │  │   - Config      │  │  - Insights │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │ HTTP/WebSocket
┌─────────────────────────────────────────────────────────────┐
│                  Python Backend API (Port 5000)            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Flask API     │  │   Simulation    │  │  Blockchain │ │
│  │   - REST        │  │   - Control     │  │  - Interface│ │
│  │   - WebSocket   │  │   - Monitor     │  │  - Status   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │ Web3/JSON-RPC
┌─────────────────────────────────────────────────────────────┐
│              Hardhat Blockchain Node (Port 8545)           │
│                     (Existing functionality)               │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Configuration

### Simulation Parameters
- **Steps**: Number of simulation steps (1-1000)
- **Commuters**: Number of commuter agents (1-100)
- **Providers**: Number of provider agents (1-50)
- **Debug Mode**: Enable detailed logging
- **Skip Plots**: Disable plot generation for faster execution
- **Random Seed**: Set seed for reproducible results

### Preset Configurations
- **Debug Mode**: 20 steps, 5 commuters, 3 providers
- **Small Test**: 30 steps, 8 commuters, 4 providers
- **Medium Test**: 50 steps, 15 commuters, 8 providers
- **Large Scale**: 100 steps, 25 commuters, 12 providers
- **Research Mode**: 200 steps, 50 commuters, 20 providers

## 🐛 Troubleshooting

### Common Issues

1. **Backend Connection Failed**
   ```bash
   # Check if backend is running
   curl http://localhost:5000/api/health
   
   # Restart backend
   npm run start-backend
   ```

2. **Blockchain Not Connected**
   ```bash
   # Start Hardhat node
   npx hardhat node
   
   # Deploy contracts
   npx hardhat run scripts/deploy.js --network localhost
   ```

3. **React Build Errors**
   ```bash
   # Clear cache and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **Python Dependencies**
   ```bash
   # Reinstall Python dependencies
   pip install -r backend/requirements.txt
   ```

## 🔄 Migration from CLI

The React interface is **fully compatible** with existing CLI usage:

- **All CLI commands work unchanged**
- **Existing scripts and automation continue to work**
- **No changes to simulation engine or blockchain integration**
- **Web interface is an additional layer, not a replacement**

## 📚 Next Steps

1. **Explore the Dashboard**: Monitor real-time simulation metrics
2. **Try Different Configurations**: Use preset configurations or create custom ones
3. **Analyze Results**: Use the Analytics tab for detailed insights
4. **Monitor Blockchain**: Check transaction status and contract interactions
5. **Extend Functionality**: Add custom charts or metrics as needed

## 🤝 Support

- **CLI Mode**: Use existing documentation and README.md
- **Web Interface**: Check browser console for errors and API responses
- **Blockchain Issues**: Verify Hardhat node is running and contracts are deployed
