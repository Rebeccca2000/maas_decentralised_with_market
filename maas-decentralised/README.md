# 🚀 Decentralized Transportation System (MaaS)

A comprehensive **Mobility-as-a-Service (MaaS)** platform that combines **agent-based modeling** with **blockchain technology** to create a transparent, immutable transportation marketplace with enterprise-grade analytics and visualization capabilities.

## 🌟 Key Features

- **🤖 Agent-Based Modeling**: Realistic simulation of commuters and transportation providers with complex behaviors
- **🔗 Blockchain Integration**: Immutable storage of all transportation data on Ethereum with smart contracts
- **📊 Advanced Transportation Metrics**: Industry-standard KPIs including match rates, generalized costs, and competition analysis
- **📈 Professional Visualizations**: Automated generation of publication-quality plots and dashboards (optimized for performance)
- **💰 Dynamic Pricing**: Market-driven pricing with supply/demand optimization and auction mechanisms
- **🎯 Smart Matching**: Advanced algorithms for optimal commuter-provider pairing with utility maximization
- **📈 Real-time Monitoring**: Live performance metrics and transaction tracking with comprehensive analytics
- **🏆 Competition Analysis**: Herfindahl-Hirschman Index (HHI) and market concentration metrics for business intelligence
- **💡 Enterprise Analytics**: Professional reporting with 11 comprehensive tables and advanced KPIs
- **⚡ Performance Optimized**: Fast execution modes with optional plot generation for development and testing

## 🏗️ System Architecture

### **High-Level Architecture Overview**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           🎯 USER INTERFACE LAYER                           │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐  │
│  │   Command Line      │  │   Analytics         │  │   Visualization     │  │
│  │   Interface (CLI)   │  │   Dashboard         │  │   Engine            │  │
│  │   - Run Parameters  │  │   - 11 Tables       │  │   - 2 Optimized     │  │
│  │   - Debug Modes     │  │   - KPI Metrics     │  │     Plots           │  │
│  │   - Configuration   │  │   - Benchmarking    │  │   - Performance     │  │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘  │
├─────────────────────────────────────────────────────────────────────────────┤
│                        🤖 AGENT-BASED MODEL LAYER                          │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐  │
│  │   Commuter Agents   │  │   Provider Agents   │  │   Market Dynamics   │  │
│  │   - Demographics    │  │   - Service Types   │  │   - Supply/Demand   │  │
│  │   - Preferences     │  │   - Pricing Models  │  │   - Competition     │  │
│  │   - Utility Calc    │  │   - Capacity Mgmt   │  │   - Price Discovery │  │
│  │   - Decision Logic  │  │   - Route Planning  │  │   - Market Share    │  │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘  │
├─────────────────────────────────────────────────────────────────────────────┤
│                       🎯 MARKETPLACE ENGINE LAYER                          │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐  │
│  │   Request Manager   │  │   Matching Engine   │  │   Auction System    │  │
│  │   - Request Queue   │  │   - Algorithm Sel   │  │   - Bid Management  │  │
│  │   - Validation      │  │   - Optimization    │  │   - Price Discovery │  │
│  │   - Routing         │  │   - Utility Max     │  │   - Winner Selection│  │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘  │
├─────────────────────────────────────────────────────────────────────────────┤
│                      🔗 BLOCKCHAIN INTERFACE LAYER                         │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐  │
│  │   Transaction Mgr   │  │   Smart Contracts   │  │   Data Storage      │  │
│  │   - Async Batching  │  │   - Registry        │  │   - Immutable Logs  │  │
│  │   - Nonce Mgmt      │  │   - Requests        │  │   - Transaction     │  │
│  │   - Gas Optimize    │  │   - Auctions        │  │     History         │  │
│  │   - Error Handling  │  │   - Facade Pattern  │  │   - User Profiles   │  │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘  │
├─────────────────────────────────────────────────────────────────────────────┤
│                        ⛓️ BLOCKCHAIN LAYER                                  │
│                    (Ethereum/Hardhat Local Network)                        │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐  │
│  │   Local Ethereum    │  │   Smart Contract    │  │   Gas & Mining      │  │
│  │   Node (Hardhat)    │  │   Deployment        │  │   - Gas Estimation  │  │
│  │   - JSON-RPC API    │  │   - Contract ABI    │  │   - Block Mining    │  │
│  │   - Account Mgmt    │  │   - Event Logs      │  │   - Transaction     │  │
│  │   - Network Config  │  │   - State Storage   │  │     Confirmation    │  │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### **Component Details**

#### **🤖 Agent-Based Model Layer**
- **Commuter Agents**: Simulate real users with demographics, preferences, and utility-based decision making
- **Provider Agents**: Model transportation services (car, bus, bike) with dynamic pricing and capacity management
- **Market Dynamics**: Supply/demand balancing, competition modeling, and price discovery mechanisms

#### **🎯 Marketplace Engine Layer**
- **Request Management**: Queue processing, validation, and routing optimization
- **Matching Engine**: Advanced algorithms for optimal commuter-provider pairing with utility maximization
- **Auction System**: Real-time bidding, price discovery, and winner selection mechanisms

#### **🔗 Blockchain Interface Layer**
- **Transaction Manager**: Asynchronous processing, nonce management, and gas optimization
- **Smart Contracts**: Solidity contracts for registry, requests, auctions, and facade patterns
- **Data Storage**: Immutable logging of all transactions, user profiles, and system state

#### **⛓️ Blockchain Layer**
- **Local Ethereum Node**: Hardhat development network with JSON-RPC API
- **Smart Contract Deployment**: Automated deployment and ABI management
- **Gas & Mining**: Optimized gas estimation, block mining, and transaction confirmation

## 🚀 Getting Started

### **🌐 NEW: React Web Interface**

**Quick Start with Web Interface:**
```bash
# Windows
start-maas-web.bat

# Linux/macOS
./start-maas-web.sh

# Or manually
npm run dev-full
```

This starts the complete web interface at **http://localhost:3000** with:
- � **Real-time Dashboard** - Monitor simulation progress and metrics
- 🎮 **Simulation Control** - Start/stop simulations with custom parameters
- 📈 **Interactive Analytics** - View charts and insights
- ⛓️ **Blockchain Status** - Monitor contracts and transactions

### **�📋 Prerequisites**

| Requirement | Version | Purpose |
|-------------|---------|---------|
| **Node.js** | v16+ | React frontend and blockchain development |
| **npm** | Latest | Package management for JavaScript dependencies |
| **Python** | 3.8+ | Agent-based modeling and simulation engine |
| **pip** | Latest | Python package management |
| **Git** | Latest | Version control and repository management |

### **⚙️ Installation & Setup**

#### **Step 1: Clone Repository**
```bash
git clone <repository-url>
cd maas-decentralised
```

#### **Step 2: Install Dependencies**
```bash
# Install Node.js dependencies (blockchain & smart contracts)
npm install

# Install Python dependencies (simulation engine)
pip install -r requirements.txt
```

#### **Step 3: Start Blockchain Infrastructure**
```bash
# Terminal 1: Start local Ethereum node
npx hardhat node
```

#### **Step 4: Deploy Smart Contracts**
```bash
# Terminal 2: Deploy contracts to local network
npx hardhat run scripts/deploy.js --network localhost
```

#### **Step 5: Choose Your Interface**

## 🎯 **Dual-Mode Operation**

### **🌐 Web Interface Mode (NEW)**
```bash
# Start complete web interface
npm run dev-full

# Or start individual services
npm run start-hardhat    # Blockchain node
npm run start-backend    # Python API server
npm start               # React frontend
```

**Features:**
- 📊 Real-time dashboard with live metrics
- 🎮 Interactive simulation control panel
- 📈 Dynamic charts and visualizations
- ⛓️ Blockchain transaction monitoring
- 🎯 Preset configuration templates
- 📱 Responsive web design

### **💻 Command Line Mode (Original)**

#### **🔧 Development & Testing Modes**
```bash
# Quick debug mode (5 commuters, 3 providers, 20 steps)
python abm/agents/run_decentralized_model.py --debug

# Fast execution without plots (development/testing)
python abm/agents/run_decentralized_model.py --debug --no-plots

# Big test scenario (15 commuters, 8 providers, 50 steps)
python abm/agents/run_decentralized_model.py --big-test
```

#### **📊 Analysis & Research Modes**
```bash
# Standard analysis with optimized visualizations
python abm/agents/run_decentralized_model.py --steps 15 --commuters 6 --providers 4

# Large-scale market analysis
python abm/agents/run_decentralized_model.py --steps 100 --commuters 20 --providers 10

# Performance testing without plots
python abm/agents/run_decentralized_model.py --steps 50 --commuters 15 --providers 8 --no-plots
```

#### **🎛️ Custom Configuration**
```bash
# Full parameter control
python abm/agents/run_decentralized_model.py \
  --steps 30 \
  --commuters 10 \
  --providers 5 \
  --no-plots

# With specific random seed for reproducibility
python abm/agents/run_decentralized_model.py \
  --steps 25 \
  --commuters 8 \
  --providers 4 \
  --seed 12345
```

### **📊 Output & Analytics**

#### **📈 Comprehensive Analytics Generated**
Each simulation automatically produces:

| Output Type | Description | Performance |
|-------------|-------------|-------------|
| **📋 Summary Tables** | 11 comprehensive tables (8 original + 3 advanced metrics) | Always generated |
| **📊 Visualization Plots** | 2 optimized essential charts (50% faster than legacy) | Optional with `--no-plots` |
| **🎯 Transportation KPIs** | Match rate, generalized cost, competition intensity | Real-time calculation |
| **📈 Market Analysis** | HHI, market share, provider performance analysis | Advanced algorithms |
| **🔗 Blockchain Summary** | Transaction statistics, gas usage, success rates | Immutable storage |

#### **⚡ Performance Options**
- **Standard Mode**: Essential visualizations with optimized performance
- **Fast Mode**: Skip plots with `--no-plots` flag for maximum speed (70% faster)
- **Debug Mode**: Detailed logging and intermediate results for development

## 📊 Enhanced Sample Output

### **Advanced Transportation Metrics**
```
📈 TABLE 9: SERVICE PERFORMANCE METRICS
--------------------------------------------------------------------------------
Metric                              Value                Benchmark       Status
--------------------------------------------------------------------------------
Match Rate / Service Fill Rate      175.0%               >80%            🟢 Excellent
Average Generalized Cost            $35.06               <$30            🟡 Moderate
Total Requests                      4                    -               📊 Data
Successful Matches                  7                    -               📊 Data
--------------------------------------------------------------------------------

🏆 TABLE 10: COMPETITION INTENSITY METRICS
--------------------------------------------------------------------------------
Metric                              Value                Interpretation
--------------------------------------------------------------------------------
Average Bids per Request            1.2                  Moderate Competition
Herfindahl-Hirschman Index          7551                 Concentrated
Number of Active Providers          2                    Market Participants
Number of Transport Modes           2                    Service Diversity
--------------------------------------------------------------------------------

📊 TABLE 11: MARKET SHARE ANALYSIS
--------------------------------------------------------------------------------
Provider/Mode             Bookings        Market Share    Performance
--------------------------------------------------------------------------------
Provider 100               6               85.7%           🌟 Leader
Provider 102               1               14.3%           📊 Active
--------------------------------------------------------------------------------
```

### **Professional Visualizations Generated**
```
📊 VISUALIZATION PLOTS CREATED:
   📁 Directory: simulation_plots_20250918_155405/
   📈 Service Performance Dashboard: service_performance_dashboard.png
   📊 Market Share Analysis: market_share_analysis.png
   🔗 Blockchain Analysis: blockchain_analysis.png
   💰 Cost Analysis: cost_analysis.png
```

### **Blockchain Storage Summary**
```
================================================================================
🔗 BLOCKCHAIN STORAGE SUMMARY
================================================================================
📊 TRANSACTION STATISTICS:
   • Total transactions sent: 15
   • Successful transactions: 15
   • Failed transactions: 0
   • Success rate: 100.0%

💰 GAS & COSTS:
   • Total gas used: 750,000
   • Estimated ETH spent: 0.015000 ETH

📋 DETAILED BOOKING RECORDS:
   Total bookings completed: 7
   Total Revenue Generated: $196.75
   Average Booking Price: $28.11

   🚗 PROVIDER TYPE BREAKDOWN:
      • car: 6 bookings (85.7%)
      • bus: 1 bookings (14.3%)
================================================================================
```

## 📚 Documentation

### **Core Documentation**
- **[DOCUMENTATION.md](./DOCUMENTATION.md)** - Complete system overview and architecture
- **[API_DOCUMENTATION.md](./API_DOCUMENTATION.md)** - Detailed API reference and usage
- **[TECHNICAL_GUIDE.md](./TECHNICAL_GUIDE.md)** - Deep dive into implementation details

### **Enhanced Features Documentation**
- **[Advanced Metrics Guide](./docs/advanced_metrics_and_visualization_guide.md)** - Comprehensive guide to transportation KPIs and visualizations
- **[Simulation Comparison Analysis](./docs/simulation_comparison_analysis.md)** - Multi-scenario market analysis and benchmarking
- **[Enhanced Simulation Summary](./docs/enhanced_simulation_summary.md)** - Complete implementation overview
- **[Blockchain Improvements](./docs/blockchain_improvements_summary.md)** - Production-ready blockchain interface enhancements
- **[Documentation Index](./docs/README.md)** - Organized navigation for all documentation resources
- **[CHANGELOG.md](./CHANGELOG.md)** - Complete version history and feature updates
- **[Plotting Optimization Guide](./docs/plotting_optimization_guide.md)** - Performance improvements and usage options

## 🔧 Configuration

The system can be configured through various parameters:

- **Simulation Scale**: Number of commuters, providers, and simulation steps
- **Blockchain Settings**: Gas limits, pricing, and network configuration
- **Agent Behavior**: Utility functions, preferences, and decision-making algorithms
- **Market Dynamics**: Pricing strategies, matching algorithms, and capacity management

## 🧪 Testing

Run the test suite to verify system functionality:

```bash
# Run unit tests
python -m pytest tests/

# Run integration tests
python -m pytest tests/integration/

# Run blockchain tests
npx hardhat test
```

## 🔍 Key Components

### Agent-Based Model
- **Commuter Agents**: Simulate real user behavior with demographics, preferences, and utility calculations
- **Provider Agents**: Model transportation services with dynamic pricing and capacity management

### Blockchain Integration
- **Smart Contracts**: Solidity contracts for registry, requests, auctions, and facade patterns
- **Transaction Management**: Asynchronous processing with nonce management and gas optimization
- **Data Storage**: Immutable storage of all transportation transactions and user profiles

### Analytics & Monitoring
- **Advanced Transportation Metrics**: Match rate, generalized cost analysis, competition intensity (HHI)
- **Professional Visualizations**: Automated generation of 4 publication-quality plots per simulation
- **Real-time Metrics**: Transaction success rates, gas usage, and performance monitoring
- **Detailed Reporting**: 11 comprehensive summary tables with full traceability
- **Business Intelligence**: Revenue tracking, market share analysis, and strategic insights
- **Comparative Analysis**: Multi-scenario benchmarking and market evolution tracking

## ✅ Recent Improvements

### **Blockchain Interface Enhancements**
- ✅ **Fixed Race Conditions**: Thread-safe operations with comprehensive locking
- ✅ **Atomic Transactions**: ACID-like properties with rollback mechanisms
- ✅ **Enhanced Error Handling**: Intelligent retry logic and error classification
- ✅ **Improved Statistics**: Accurate transaction counting and success tracking

### **Advanced Analytics Implementation**
- ✅ **Transportation KPIs**: Match rate, generalized cost, competition intensity
- ✅ **Professional Visualizations**: 4 automated plots per simulation
- ✅ **Market Analysis**: HHI calculation and market share distribution
- ✅ **Comparative Studies**: Multi-scenario benchmarking capabilities

## 🚨 Known Limitations

- **Network Dependency**: Requires local Hardhat node for blockchain operations
- **Scalability**: Optimized for research and development environments
- **Gas Costs**: Transaction costs may vary with network congestion

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with Mesa framework for agent-based modeling
- Ethereum blockchain integration via Web3.py
- Smart contracts developed with Hardhat and Solidity
- Comprehensive testing and documentation

---

**Ready to revolutionize transportation with blockchain technology!** 🚀
