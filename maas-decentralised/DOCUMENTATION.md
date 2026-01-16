# Decentralized Transportation System Documentation

## 🚀 Overview

This is a comprehensive decentralized Mobility-as-a-Service (MaaS) platform that combines agent-based modeling with blockchain technology to create a transparent, immutable transportation marketplace.

## 🏗️ Architecture

### Core Components

1. **Agent-Based Model (ABM)** - Simulates commuters and transportation providers
2. **Blockchain Integration** - Stores data permanently on Ethereum-compatible blockchain
3. **Smart Contracts** - Handle registrations, requests, offers, and settlements
4. **Marketplace API** - Manages off-chain matching and coordination
5. **Detailed Analytics** - Comprehensive booking tracking and reporting

### Technology Stack

- **Python**: Mesa framework for agent-based modeling
- **Solidity**: Smart contracts (v0.8.20)
- **Hardhat**: Ethereum development environment
- **Web3.py**: Blockchain interaction library
- **IPFS**: Decentralized content storage

## 📁 Project Structure

```
maas-decentralised/
├── abm/                          # Agent-Based Model
│   ├── agents/                   # Agent implementations
│   │   ├── decentralized_commuter.py    # Commuter agent logic
│   │   ├── decentralized_provider.py    # Provider agent logic
│   │   └── run_decentralized_model.py   # Main simulation runner
│   └── utils/                    # Utilities
│       └── blockchain_interface.py      # Blockchain integration
├── contracts/                    # Smart Contracts
│   ├── MaaSRegistry.sol         # User registration
│   ├── MaaSRequest.sol          # Travel requests
│   ├── MaaSAuction.sol          # Offers and matching
│   ├── MaaSFacade.sol           # Main interface
│   └── MockERC20.sol            # Test token
├── scripts/                      # Deployment and testing
├── artifacts/                    # Compiled contracts
└── deployment-info.json         # Contract addresses
```

## 🤖 Agent-Based Model

### Commuter Agents (`DecentralizedCommuter`)

**Purpose**: Simulate transportation users with realistic preferences and behaviors.

**Key Features**:
- **Demographics**: Age, income level, disability status, tech access
- **Preferences**: Transport mode preferences (car, bus, bike, train, walk)
- **Utility Functions**: Cost, time, comfort, reliability, environmental factors
- **Learning**: Adapts strategy based on past experiences
- **Blockchain Integration**: Registers on blockchain, creates requests

**Core Methods**:
```python
def _register_with_blockchain(self):
    """Register commuter and store detailed profile"""
    
def create_request(self, origin, destination, start_time):
    """Create travel request with route details"""
    
def calculate_option_utility(self, option, request_id):
    """Calculate utility score for transport options"""
```

### Provider Agents (`DecentralizedProvider`)

**Purpose**: Simulate transportation service providers (Uber, buses, bike-share, etc.).

**Key Features**:
- **Service Types**: Car, bus, bike sharing, train services
- **Dynamic Pricing**: Distance-based with randomization
- **Capacity Management**: Track available capacity
- **Quality Metrics**: Reliability and quality scores
- **Blockchain Integration**: Registers services, submits offers

**Core Methods**:
```python
def submit_offer_for_request(self, request_id):
    """Submit competitive offer for travel request"""
    
def get_service_offers(self, origin, destination, start_time):
    """Generate service offers with pricing"""
```

## 🔗 Blockchain Integration

### Smart Contracts

#### MaaSRegistry.sol
**Purpose**: Manage user registrations and access control.

```solidity
function registerAsCommuter(uint256 commuterId, string calldata metadataHash) external
function registerAsProvider(uint256 providerId, string calldata mode, string calldata metadataHash) external
```

#### MaaSRequest.sol
**Purpose**: Store travel requests with IPFS content hashes.

```solidity
function createRequestWithHash(uint256 requestId, uint256 commuterId, string calldata contentHash) external
function updateStatus(uint256 requestId, Status newStatus) external
```

#### MaaSAuction.sol
**Purpose**: Handle service offers and match recording.

```solidity
function submitOfferHash(uint256 requestId, uint256 providerId, string calldata contentHash) external
function recordMatchResult(uint256 requestId, uint256 offerId, uint256 providerId, uint256 priceWei) external
```

#### MaaSFacade.sol
**Purpose**: Main interface with access control and unified API.

```solidity
function recordMatch(uint256 requestId, uint256 offerId, uint256 providerId, uint256 priceWei) external onlyAPI
```

### Blockchain Interface (`BlockchainInterface`)

**Purpose**: Bridge between Python agents and smart contracts.

**Key Features**:
- **Asynchronous Processing**: Batch transaction processing
- **Nonce Management**: Sequential transaction ordering
- **Gas Optimization**: Efficient transaction batching
- **Error Handling**: Comprehensive retry logic
- **Performance Tracking**: Transaction statistics and monitoring

**Core Methods**:
```python
def register_commuter(self, commuter):
    """Register commuter on blockchain with profile storage"""
    
def create_travel_request_marketplace(self, commuter, request):
    """Create request in marketplace and push to blockchain"""
    
def run_marketplace_matching(self, request_id):
    """Execute off-chain matching algorithm"""
    
def get_blockchain_summary(self):
    """Generate comprehensive statistics and booking details"""
```

## 📊 Detailed Booking Tracking

### Profile Storage

**Commuter Profiles**:
```python
{
    'commuter_id': int,
    'age': int,
    'income_level': str,  # 'low', 'middle', 'high'
    'has_disability': bool,
    'tech_access': bool,
    'health_status': str,
    'payment_scheme': str,  # 'PAYG', 'subscription'
    'preferences': dict,    # Transport mode preferences
    'utility_coefficients': dict  # Cost, time, comfort weights
}
```

**Provider Profiles**:
```python
{
    'provider_id': int,
    'name': str,
    'mode': str,           # 'car', 'bus', 'bike', 'train'
    'capacity': int,
    'base_price': float,
    'quality_score': int,
    'reliability': int,
    'service_center': list  # [x, y] coordinates
}
```

### Booking Records

**Comprehensive Booking Data**:
```python
{
    'booking_id': str,
    'commuter_id': int,
    'provider_id': int,
    'price': float,
    'origin': list,        # [x, y] coordinates
    'destination': list,   # [x, y] coordinates
    'route_details': {
        'distance': float,
        'duration': int    # minutes
    },
    'commuter_profile': dict,
    'provider_profile': dict,
    'timestamp': float
}
```

## 🚀 Running the System

### Prerequisites

```bash
npm install          # Install Hardhat and dependencies
pip install -r requirements.txt  # Install Python dependencies
```

### Start Blockchain Node

```bash
npx hardhat node     # Start local Ethereum node
```

### Deploy Contracts

```bash
npx hardhat run scripts/deploy.js --network localhost
```

### Run Simulation

```bash
# Debug mode (5 commuters, 3 providers, 20 steps)
python abm/agents/run_decentralized_model.py --debug

# Big test (15 commuters, 8 providers, 50 steps)
python abm/agents/run_decentralized_model.py --big-test

# Custom parameters
python abm/agents/run_decentralized_model.py --steps 100 --commuters 20 --providers 10
```

## 📈 Output and Analytics

### Simulation Summary

The system generates comprehensive reports including:

- **Transaction Statistics**: Success rates, gas costs, performance metrics
- **Blockchain Verification**: Connection status, contract accessibility
- **Detailed Booking Records**: Complete traceability of all transactions
- **Financial Analytics**: Revenue summaries, pricing analysis
- **Provider Performance**: Service type distribution, quality metrics
- **User Behavior**: Commuter preferences, demographic analysis

### Sample Output

```
📋 DETAILED BOOKING RECORDS:
🎫 BOOKING #1:
   • Booking ID: REQ_001
   • Commuter ID: 3 → Income: middle, Age: 35
   • Provider ID: 100 → Type: car, Name: UberLike-100
   • Total Price: $22.15
   • Route: [19,6] → [18,6], Distance: 1.0 units, Duration: 3 min

💰 FINANCIAL SUMMARY:
   • Total Revenue Generated: $211.50
   • Average Booking Price: $17.62

🚗 PROVIDER TYPE BREAKDOWN:
   • car: 9 bookings (75.0%)
   • bus: 3 bookings (25.0%)
```

## 🔧 Configuration

### Blockchain Configuration (`blockchain_config.json`)

```json
{
    "rpc_url": "http://127.0.0.1:8545",
    "chain_id": 31337,
    "gas_limit": 500000,
    "gas_price": 20000000000
}
```

### Contract Addresses (`deployment-info.json`)

```json
{
    "registry": "0x...",
    "request": "0x...",
    "auction": "0x...",
    "facade": "0x...",
    "token": "0x..."
}
```

## 🐛 Known Issues

1. **Match Recording**: Offer ID mapping between marketplace and blockchain needs refinement
2. **Gas Optimization**: Some transactions could be further optimized
3. **Scalability**: Large simulations may require performance tuning

## 🔮 Future Enhancements

1. **Real-time Matching**: WebSocket-based real-time updates
2. **Advanced Analytics**: Machine learning for demand prediction
3. **Multi-chain Support**: Deploy on multiple blockchain networks
4. **Mobile Interface**: React Native app for real users
5. **IoT Integration**: Real vehicle tracking and status updates

## 📚 References

- [Mesa Documentation](https://mesa.readthedocs.io/)
- [Hardhat Documentation](https://hardhat.org/docs)
- [Web3.py Documentation](https://web3py.readthedocs.io/)
- [Solidity Documentation](https://docs.soliditylang.org/)
