# API Documentation - Decentralized Transportation System

## 🔗 Blockchain Interface API

### Core Registration Methods

#### `register_commuter(commuter)`
**Purpose**: Register a commuter on the blockchain and store detailed profile.

**Parameters**:
- `commuter` (DecentralizedCommuter): Commuter agent instance

**Returns**: 
- `tuple(bool, str)`: (success, blockchain_address)

**Blockchain Storage**:
- User registration in MaaSRegistry contract
- Profile data stored via `store_commuter_profile()`

**Example**:
```python
success, address = blockchain_interface.register_commuter(commuter_agent)
if success:
    print(f"Commuter registered at {address}")
```

#### `register_provider(provider)`
**Purpose**: Register a transportation provider on the blockchain.

**Parameters**:
- `provider` (DecentralizedProvider): Provider agent instance

**Returns**: 
- `tuple(bool, str)`: (success, blockchain_address)

**Blockchain Storage**:
- Provider registration in MaaSRegistry contract
- Service details and profile data stored

### Request Management

#### `create_travel_request_marketplace(commuter, request)`
**Purpose**: Create a travel request in marketplace and push to blockchain.

**Parameters**:
- `commuter` (DecentralizedCommuter): Requesting commuter
- `request` (dict): Request details including origin, destination, requirements

**Request Structure**:
```python
{
    'request_id': int,
    'commuter_id': int,
    'origin': [x, y],
    'destination': [x, y],
    'start_time': int,
    'travel_purpose': int,
    'requirement_keys': list,
    'requirement_values': list
}
```

**Returns**: 
- `tuple(bool, int)`: (success, request_id)

**Blockchain Storage**:
- Request hash in MaaSRequest contract
- Full request details in marketplace database

#### `get_marketplace_requests(status=None)`
**Purpose**: Retrieve requests from marketplace database.

**Parameters**:
- `status` (str, optional): Filter by status ('active', 'matched', 'completed')

**Returns**: 
- `list[dict]`: List of request objects

### Offer Management

#### `submit_offer_marketplace(provider, request_id, price, details=None)`
**Purpose**: Submit a service offer for a travel request.

**Parameters**:
- `provider` (DecentralizedProvider): Offering provider
- `request_id` (int): Target request ID
- `price` (float): Offer price
- `details` (dict, optional): Additional offer details

**Offer Details Structure**:
```python
{
    'route': [[x1, y1], [x2, y2]],
    'time': int,  # estimated duration in minutes
    'mode': str   # transport mode
}
```

**Returns**: 
- `bool`: Success status

**Blockchain Storage**:
- Offer hash in MaaSAuction contract
- Detailed offer data via `store_offer_details()`

#### `get_request_offers(request_id)`
**Purpose**: Get all offers for a specific request.

**Parameters**:
- `request_id` (int): Request identifier

**Returns**: 
- `list[dict]`: List of offer objects

### Matching and Settlement

#### `run_marketplace_matching(request_id)`
**Purpose**: Execute off-chain matching algorithm and record result.

**Parameters**:
- `request_id` (int): Request to match

**Returns**: 
- `tuple(bool, dict)`: (success, match_result)

**Matching Algorithm**:
1. Retrieve all offers for request
2. Score offers based on price, quality, reliability
3. Select winning offer
4. Store match result in marketplace
5. Queue blockchain transaction for settlement

**Match Result Structure**:
```python
{
    'request_id': int,
    'winning_offer_id': str,
    'provider_id': int,
    'final_price': float,
    'match_time': float,
    'match_score': float
}
```

### Profile and Analytics Storage

#### `store_commuter_profile(commuter_id, profile_data)`
**Purpose**: Store detailed commuter profile for analytics.

**Profile Data Structure**:
```python
{
    'commuter_id': int,
    'age': int,
    'income_level': str,
    'has_disability': bool,
    'tech_access': bool,
    'health_status': str,
    'payment_scheme': str,
    'home_location': [x, y],
    'preferences': dict,
    'utility_coefficients': dict
}
```

#### `store_provider_profile(provider_id, profile_data)`
**Purpose**: Store detailed provider profile for analytics.

**Profile Data Structure**:
```python
{
    'provider_id': int,
    'name': str,
    'mode': str,
    'capacity': int,
    'base_price': float,
    'quality_score': int,
    'reliability': int,
    'service_center': [x, y],
    'company_name': str
}
```

#### `store_match_details(match_id, match_data)`
**Purpose**: Store comprehensive booking information.

**Match Data Structure**:
```python
{
    'match_id': str,
    'commuter_id': int,
    'provider_id': int,
    'request_id': int,
    'offer_id': str,
    'price': float,
    'origin': [x, y],
    'destination': [x, y],
    'route_details': dict,
    'match_time': float
}
```

### Statistics and Reporting

#### `get_blockchain_summary()`
**Purpose**: Generate comprehensive blockchain and booking statistics.

**Returns**: 
```python
{
    'total_transactions': int,
    'successful_transactions': int,
    'failed_transactions': int,
    'success_rate': float,
    'total_gas_used': int,
    'eth_spent': float,
    'commuter_registrations': int,
    'provider_registrations': int,
    'travel_requests': int,
    'service_offers': int,
    'completed_matches': int,
    'blockchain_connected': bool,
    'avg_tx_time': float,
    'peak_tps': float,
    'congestion_level': str,
    'recent_tx_hashes': list,
    'booking_details': list,
    'commuter_profiles': dict,
    'provider_profiles': dict
}
```

## 🤖 Agent API

### DecentralizedCommuter Methods

#### `create_request(origin, destination, start_time, travel_purpose='work', requirements=None)`
**Purpose**: Create a new travel request.

**Parameters**:
- `origin` (list): Starting coordinates [x, y]
- `destination` (list): Ending coordinates [x, y]
- `start_time` (int): Preferred departure time
- `travel_purpose` (str): Purpose of travel
- `requirements` (dict, optional): Custom requirements

**Returns**: 
- `int`: Request ID (or None if queued)

#### `calculate_option_utility(option, request_id)`
**Purpose**: Calculate utility score for a transport option.

**Parameters**:
- `option` (dict): Transport option details
- `request_id` (int): Associated request

**Returns**: 
- `float`: Utility score (higher is better)

**Utility Factors**:
- Cost sensitivity based on income level
- Time preferences based on travel purpose
- Comfort requirements based on age/disability
- Reliability importance based on trip criticality
- Environmental consciousness

### DecentralizedProvider Methods

#### `submit_offer_for_request(request_id)`
**Purpose**: Submit competitive offer for a travel request.

**Parameters**:
- `request_id` (int): Target request

**Returns**: 
- `bool`: Success status

**Pricing Algorithm**:
1. Calculate base distance cost
2. Apply service-specific multipliers
3. Add randomization for market dynamics
4. Consider capacity and demand

#### `get_service_offers(origin, destination, start_time)`
**Purpose**: Generate service offers for a route.

**Parameters**:
- `origin` (list): Starting coordinates
- `destination` (list): Ending coordinates  
- `start_time` (int): Departure time

**Returns**: 
- `list[dict]`: Available service options

## 🔧 Configuration API

### Blockchain Configuration

**File**: `blockchain_config.json`

```python
{
    "rpc_url": "http://127.0.0.1:8545",
    "chain_id": 31337,
    "gas_limit": 500000,
    "gas_price": 20000000000,
    "max_retries": 3,
    "retry_delay": 1.0
}
```

### Contract Deployment

**File**: `deployment-info.json`

```python
{
    "registry": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
    "request": "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512", 
    "auction": "0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0",
    "facade": "0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9",
    "token": "0xDc64a140Aa3E981100a9becA4E685f962f0cF6C9"
}
```

## 📊 Event Monitoring

### Blockchain Events

**MatchRecorded Event**:
```solidity
event MatchRecorded(
    uint256 indexed requestId,
    uint256 indexed offerId, 
    uint256 indexed providerId,
    uint256 priceWei
);
```

**RequestCreated Event**:
```solidity
event RequestCreated(
    uint256 indexed requestId,
    uint256 indexed commuterId,
    string contentHash
);
```

### Event Listening

```python
def listen_for_events():
    """Monitor blockchain events for real-time updates"""
    match_filter = auction_contract.events.MatchRecorded.createFilter(fromBlock='latest')
    
    for event in match_filter.get_new_entries():
        process_match_event(event)
```

## 🚨 Error Handling

### Common Error Codes

- **`ConnectionError`**: Blockchain node unreachable
- **`TransactionFailed`**: Transaction reverted or failed
- **`InsufficientFunds`**: Not enough ETH for gas
- **`NonceError`**: Transaction nonce conflicts
- **`ContractError`**: Smart contract execution failed

### Retry Logic

```python
@retry(max_attempts=3, delay=1.0)
def execute_transaction(tx_data):
    """Execute transaction with automatic retry"""
    try:
        return send_transaction(tx_data)
    except Exception as e:
        log_error(f"Transaction failed: {e}")
        raise
```

## 🔐 Security Considerations

### Access Control

- **onlyOwner**: Contract deployment and critical functions
- **onlyAPI**: Marketplace operations and data updates
- **Rate Limiting**: Prevent spam transactions
- **Input Validation**: Sanitize all user inputs

### Data Privacy

- **IPFS Storage**: Sensitive data stored off-chain
- **Hash References**: Only content hashes on blockchain
- **Encryption**: Optional encryption for private data
- **Anonymization**: User IDs don't reveal personal information
