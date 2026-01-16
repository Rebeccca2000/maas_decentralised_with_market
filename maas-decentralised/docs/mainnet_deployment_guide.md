# Mainnet Deployment Guide: Event-Based Blockchain Architecture

## Overview

When deploying to mainnet, you **cannot wait** for transaction confirmations due to:
- **Network congestion**: Transactions may take minutes or hours to confirm
- **Gas price volatility**: Failed transactions waste gas fees
- **Unpredictable timing**: Block times vary, especially during high network usage
- **Cost considerations**: Each failed retry costs gas

The solution is an **event-based architecture** that relies on blockchain events for state tracking instead of blocking waits.

## Architecture Comparison

### ❌ Development/Testnet Approach (Blocking)
```python
# BAD for mainnet - blocks execution
tx_hash = contract.functions.registerCommuter(id, address).transact()
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)  # BLOCKS!
if receipt.status == 1:
    print("Registration confirmed")
```

### ✅ Mainnet Approach (Event-Based)
```python
# GOOD for mainnet - non-blocking
tx_hash = submit_transaction_async(
    contract.functions.registerCommuter(id, address),
    callback=on_registration_confirmed
)
print(f"Registration submitted: {tx_hash}")
# Continue execution immediately - callback handles confirmation
```

## Key Components

### 1. Event-Based Blockchain Interface (`EventBasedBlockchain`)

**Core Features:**
- **Fire-and-forget transactions**: Submit and continue immediately
- **Event monitoring**: Background thread listens for blockchain events
- **Automatic state tracking**: Events update application state
- **Retry mechanism**: Failed transactions can be retried automatically
- **Statistics tracking**: Real-time metrics on transaction status

**Key Methods:**
```python
# Submit transactions asynchronously
tx_hash = blockchain.register_commuter_async(commuter_id, address, callback)
tx_hash = blockchain.create_request_async(commuter_id, content_hash, callback)
tx_hash = blockchain.submit_offer_async(request_id, provider_id, content_hash, callback)

# Query confirmed state (from events)
is_registered = blockchain.is_commuter_registered(commuter_id)
is_confirmed = blockchain.is_request_confirmed(request_id)

# Get real-time statistics
stats = blockchain.get_statistics()
```

### 2. Smart Contract Events

All smart contracts emit events for state changes:

```solidity
// Registry events
event CommuterRegistered(uint256 indexed commuterId, address indexed account);
event ProviderRegistered(uint256 indexed providerId, address indexed account, uint8 mode);

// Request events  
event RequestCreated(uint256 indexed requestId, uint256 indexed commuterId, string contentHash);

// Auction events
event OfferSubmitted(uint256 indexed requestId, uint256 indexed offerId, uint256 indexed providerId, string contentHash);
event MatchRecorded(uint256 indexed requestId, uint256 indexed offerId, uint256 providerId, uint256 priceWei);
```

### 3. Event Monitoring System

Background threads continuously monitor for events:

```python
def _event_monitor_loop(self):
    """Background loop to monitor blockchain events"""
    while self.running:
        for subscription in self.event_subscriptions:
            new_events = subscription.filter_obj.get_new_entries()
            for event in new_events:
                subscription.callback(event)  # Process event
        time.sleep(1)  # Check every second
```

## Implementation Patterns

### 1. Transaction Submission Pattern

```python
def submit_with_callback(self, operation_data):
    """Submit transaction with callback for confirmation"""
    
    def on_confirmed(tx_hash, tx_data):
        # Handle successful confirmation
        self.update_local_state(tx_data.params)
        self.notify_user(f"Operation {tx_hash} confirmed")
    
    def on_failed(tx_hash, error):
        # Handle failure
        self.retry_transaction(tx_hash)
        self.notify_user(f"Operation {tx_hash} failed: {error}")
    
    # Submit asynchronously
    tx_hash = self.blockchain.submit_transaction_async(
        function_call=operation_data['function'],
        tx_type=operation_data['type'],
        params=operation_data['params'],
        callback=on_confirmed
    )
    
    return tx_hash  # Return immediately
```

### 2. State Reconciliation Pattern

```python
def reconcile_state(self):
    """Reconcile local state with blockchain events"""
    
    # Check what's confirmed on blockchain vs local state
    for local_request in self.local_requests:
        if not self.blockchain.is_request_confirmed(local_request.id):
            # Request not yet confirmed - keep waiting
            continue
        else:
            # Request confirmed - update local state
            local_request.status = 'confirmed'
            self.process_confirmed_request(local_request)
```

### 3. Graceful Degradation Pattern

```python
def handle_network_issues(self):
    """Handle network connectivity issues gracefully"""
    
    if not self.blockchain.w3.is_connected():
        # Network down - queue operations locally
        self.queue_for_later(operation_data)
        self.notify_user("Network issues - operation queued")
        return
    
    # Network up - process queued operations
    for queued_op in self.queued_operations:
        self.submit_with_callback(queued_op)
```

## Mainnet Configuration

### 1. Network Configuration

```json
{
    "rpc_url": "https://mainnet.infura.io/v3/YOUR_PROJECT_ID",
    "chain_id": 1,
    "gas_price_strategy": "fast",
    "max_gas_price": "100000000000",
    "confirmation_blocks": 3,
    "retry_count": 5,
    "retry_delay": 30,
    "use_poa": false
}
```

### 2. Gas Management

```python
# Dynamic gas pricing
def get_gas_price(self):
    """Get appropriate gas price for current network conditions"""
    
    # Get current network gas price
    current_price = self.w3.eth.gas_price
    
    # Apply strategy
    if self.config['gas_price_strategy'] == 'fast':
        return int(current_price * 1.2)  # 20% above current
    elif self.config['gas_price_strategy'] == 'standard':
        return current_price
    else:
        return int(current_price * 0.8)  # 20% below current
```

### 3. Error Handling

```python
def handle_transaction_error(self, tx_hash, error):
    """Handle various transaction errors"""
    
    if "nonce too low" in str(error):
        # Nonce issue - reset and retry
        self.reset_nonce(account_address)
        self.retry_transaction(tx_hash)
    
    elif "gas price too low" in str(error):
        # Gas price too low - increase and retry
        self.increase_gas_price()
        self.retry_transaction(tx_hash)
    
    elif "insufficient funds" in str(error):
        # Out of ETH - alert and queue for later
        self.alert_insufficient_funds()
        self.queue_for_later(tx_hash)
    
    else:
        # Unknown error - log and continue
        self.logger.error(f"Transaction {tx_hash} failed: {error}")
```

## Running the Mainnet Simulation

### 1. Basic Usage

```bash
# Run mainnet-ready simulation
python abm/agents/mainnet_simulation.py --commuters 10 --providers 5 --requests 20

# Monitor in real-time
python abm/agents/mainnet_simulation.py --commuters 50 --providers 20 --requests 100
```

### 2. Expected Output

```
🚀 MAINNET SIMULATION STATUS (Elapsed: 15.3s)
============================================================
📊 SIMULATION METRICS:
   • Agents created: 15
   • Registration attempts: 15
   • Requests created: 20
   • Offers submitted: 40
   • Matches recorded: 20

🔗 BLOCKCHAIN STATUS:
   • Transactions sent: 95
   • Transactions confirmed: 67
   • Transactions failed: 2
   • Pending transactions: 26
   • Events processed: 67

✅ CONFIRMED ON BLOCKCHAIN:
   • Registrations: 13
   • Requests: 18
   • Offers: 36
   • Matches: 18

⏳ 26 transactions still pending...
   Events will update status as confirmations arrive
============================================================
```

## Benefits of Event-Based Architecture

### 1. **Scalability**
- No blocking waits = higher throughput
- Can submit hundreds of transactions per second
- Graceful handling of network congestion

### 2. **Reliability**
- Automatic retry mechanisms
- Graceful degradation during network issues
- State reconciliation through events

### 3. **Cost Efficiency**
- No wasted gas on failed retries
- Dynamic gas pricing optimization
- Batch transaction processing

### 4. **User Experience**
- Immediate feedback on transaction submission
- Real-time status updates through events
- Continuous operation during network delays

### 5. **Production Ready**
- Handles mainnet conditions (slow confirmations, high gas prices)
- Robust error handling and recovery
- Comprehensive monitoring and alerting

## Migration from Blocking to Event-Based

### Step 1: Replace Blocking Calls
```python
# Before (blocking)
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

# After (event-based)
tx_hash = submit_transaction_async(function_call, callback=on_confirmed)
```

### Step 2: Add Event Handlers
```python
def on_registration_confirmed(event):
    commuter_id = event['args']['commuterId']
    self.mark_commuter_registered(commuter_id)
```

### Step 3: Update State Management
```python
# Query confirmed state from events instead of blockchain calls
def is_ready_for_next_step(self, commuter_id):
    return self.blockchain.is_commuter_registered(commuter_id)
```

### Step 4: Add Monitoring
```python
def print_status(self):
    stats = self.blockchain.get_statistics()
    print(f"Pending: {stats['pending_transactions']}")
    print(f"Confirmed: {stats['transactions_confirmed']}")
```

## Conclusion

The event-based architecture is **essential for mainnet deployment** because it:

1. **Eliminates blocking waits** that would freeze your application
2. **Handles network unpredictability** gracefully
3. **Provides real-time state tracking** through events
4. **Scales to high transaction volumes**
5. **Reduces gas costs** through intelligent retry mechanisms

This approach allows your MaaS simulation to run continuously on mainnet, providing real-time updates to users while handling the inherent challenges of public blockchain networks.
