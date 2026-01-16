#!/usr/bin/env python3
"""
Event-based blockchain interface for mainnet deployment
Handles asynchronous transaction processing using blockchain events
"""

import time
import json
import logging
import threading
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable, Any
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account

@dataclass
class PendingTransaction:
    """Represents a transaction waiting for confirmation"""
    tx_hash: str
    tx_type: str
    params: Dict[str, Any]
    timestamp: float
    retry_count: int = 0
    callback: Optional[Callable] = None

@dataclass
class EventSubscription:
    """Represents an event subscription"""
    contract_name: str
    event_name: str
    filter_obj: Any
    callback: Callable
    from_block: str = 'latest'

class EventBasedBlockchain:
    """
    Event-based blockchain interface suitable for mainnet deployment
    
    Key features:
    - Fire-and-forget transaction submission
    - Event-based confirmation tracking
    - Automatic retry mechanism
    - State reconciliation through events
    - No blocking waits
    """
    
    def __init__(self, config_file="blockchain_config.json"):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Load configuration
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.config['rpc_url']))
        if not self.w3.is_connected():
            raise ConnectionError("Cannot connect to blockchain")
        
        # Add PoA middleware for some networks
        if self.config.get('use_poa', False):
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Load contracts
        self.contracts = self._load_contracts()
        
        # Transaction management
        self.pending_transactions: Dict[str, PendingTransaction] = {}
        self.nonce_manager = defaultdict(int)
        self.nonce_lock = threading.Lock()
        
        # Event management
        self.event_subscriptions: List[EventSubscription] = []
        self.event_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        
        # State tracking
        self.confirmed_registrations = set()
        self.confirmed_requests = set()
        self.confirmed_offers = set()
        self.confirmed_matches = set()
        
        # Background processing
        self.running = True
        self.event_thread = None
        self.cleanup_thread = None
        
        # Statistics
        self.stats = {
            'transactions_sent': 0,
            'transactions_confirmed': 0,
            'transactions_failed': 0,
            'events_processed': 0
        }
        
        self._start_event_monitoring()
    
    def _load_contracts(self) -> Dict[str, Any]:
        """Load smart contract interfaces"""
        contracts = {}
        
        # Load deployment info
        with open(self.config.get('deployment_info', 'deployed/simplified.json'), 'r') as f:
            deployed = json.load(f)
        
        # Load contract ABIs and create contract instances
        contract_names = ['registry', 'request', 'auction', 'facade']
        
        for name in contract_names:
            if name in deployed:
                try:
                    abi_path = f"artifacts/contracts/MaaS{name.capitalize()}.sol/MaaS{name.capitalize()}.json"
                    with open(abi_path, 'r') as f:
                        contract_data = json.load(f)
                    
                    contracts[name] = self.w3.eth.contract(
                        address=deployed[name],
                        abi=contract_data['abi']
                    )
                    self.logger.info(f"Loaded {name} contract at {deployed[name]}")
                except Exception as e:
                    self.logger.warning(f"Could not load {name} contract: {e}")
        
        return contracts
    
    def _start_event_monitoring(self):
        """Start background event monitoring"""
        self.event_thread = threading.Thread(target=self._event_monitor_loop, daemon=True)
        self.event_thread.start()
        
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
        
        # Subscribe to key events
        self._subscribe_to_events()
    
    def _subscribe_to_events(self):
        """Subscribe to important blockchain events"""
        
        # Registry events
        if 'registry' in self.contracts:
            self.subscribe_to_event(
                'registry', 'CommuterRegistered',
                self._handle_commuter_registered
            )
            self.subscribe_to_event(
                'registry', 'ProviderRegistered', 
                self._handle_provider_registered
            )
        
        # Request events
        if 'request' in self.contracts:
            self.subscribe_to_event(
                'request', 'RequestCreated',
                self._handle_request_created
            )
        
        # Auction events
        if 'auction' in self.contracts:
            self.subscribe_to_event(
                'auction', 'OfferSubmitted',
                self._handle_offer_submitted
            )
            self.subscribe_to_event(
                'auction', 'MatchRecorded',
                self._handle_match_recorded
            )
    
    def subscribe_to_event(self, contract_name: str, event_name: str, callback: Callable):
        """Subscribe to a specific contract event"""
        if contract_name not in self.contracts:
            self.logger.warning(f"Contract {contract_name} not available for event subscription")
            return
        
        try:
            contract = self.contracts[contract_name]
            event = getattr(contract.events, event_name)
            event_filter = event.createFilter(fromBlock='latest')
            
            subscription = EventSubscription(
                contract_name=contract_name,
                event_name=event_name,
                filter_obj=event_filter,
                callback=callback
            )
            
            self.event_subscriptions.append(subscription)
            self.logger.info(f"Subscribed to {contract_name}.{event_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to subscribe to {contract_name}.{event_name}: {e}")
    
    def _event_monitor_loop(self):
        """Background loop to monitor blockchain events"""
        self.logger.info("Event monitoring started")
        
        while self.running:
            try:
                for subscription in self.event_subscriptions:
                    try:
                        # Get new events
                        new_events = subscription.filter_obj.get_new_entries()
                        
                        for event in new_events:
                            self.stats['events_processed'] += 1
                            
                            # Call the callback
                            try:
                                subscription.callback(event)
                            except Exception as e:
                                self.logger.error(f"Error in event callback: {e}")
                    
                    except Exception as e:
                        self.logger.warning(f"Error checking events for {subscription.event_name}: {e}")
                
                time.sleep(1)  # Check events every second
                
            except Exception as e:
                self.logger.error(f"Error in event monitoring loop: {e}")
                time.sleep(5)  # Wait longer on error
    
    def _cleanup_loop(self):
        """Background loop to clean up old pending transactions"""
        while self.running:
            try:
                current_time = time.time()
                timeout = 300  # 5 minutes timeout
                
                expired_txs = []
                for tx_hash, tx_data in self.pending_transactions.items():
                    if current_time - tx_data.timestamp > timeout:
                        expired_txs.append(tx_hash)
                
                for tx_hash in expired_txs:
                    tx_data = self.pending_transactions.pop(tx_hash)
                    self.stats['transactions_failed'] += 1
                    self.logger.warning(f"Transaction {tx_hash} timed out after {timeout}s")
                
                time.sleep(60)  # Clean up every minute
                
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
                time.sleep(60)
    
    # Event handlers
    def _handle_commuter_registered(self, event):
        """Handle CommuterRegistered event"""
        commuter_id = event['args']['commuterId']
        address = event['args']['account']
        
        self.confirmed_registrations.add(f"commuter_{commuter_id}")
        self.logger.info(f"✅ Commuter {commuter_id} registration confirmed at {address}")
        
        # Remove from pending if exists
        self._mark_transaction_confirmed(event['transactionHash'].hex())
    
    def _handle_provider_registered(self, event):
        """Handle ProviderRegistered event"""
        provider_id = event['args']['providerId']
        address = event['args']['account']
        mode = event['args']['mode']
        
        self.confirmed_registrations.add(f"provider_{provider_id}")
        self.logger.info(f"✅ Provider {provider_id} registration confirmed at {address} (mode: {mode})")
        
        self._mark_transaction_confirmed(event['transactionHash'].hex())
    
    def _handle_request_created(self, event):
        """Handle RequestCreated event"""
        request_id = event['args']['requestId']
        commuter_id = event['args']['commuterId']
        
        self.confirmed_requests.add(request_id)
        self.logger.info(f"✅ Request {request_id} created by commuter {commuter_id}")
        
        self._mark_transaction_confirmed(event['transactionHash'].hex())
    
    def _handle_offer_submitted(self, event):
        """Handle OfferSubmitted event"""
        request_id = event['args']['requestId']
        offer_id = event['args']['offerId']
        provider_id = event['args']['providerId']
        
        self.confirmed_offers.add(offer_id)
        self.logger.info(f"✅ Offer {offer_id} submitted by provider {provider_id} for request {request_id}")
        
        self._mark_transaction_confirmed(event['transactionHash'].hex())
    
    def _handle_match_recorded(self, event):
        """Handle MatchRecorded event"""
        request_id = event['args']['requestId']
        offer_id = event['args']['offerId']
        provider_id = event['args']['providerId']
        
        self.confirmed_matches.add(request_id)
        self.logger.info(f"✅ Match recorded: request {request_id}, offer {offer_id}, provider {provider_id}")
        
        self._mark_transaction_confirmed(event['transactionHash'].hex())
    
    def _mark_transaction_confirmed(self, tx_hash: str):
        """Mark a transaction as confirmed and remove from pending"""
        if tx_hash in self.pending_transactions:
            tx_data = self.pending_transactions.pop(tx_hash)
            self.stats['transactions_confirmed'] += 1
            
            # Call callback if provided
            if tx_data.callback:
                try:
                    tx_data.callback(tx_hash, tx_data)
                except Exception as e:
                    self.logger.error(f"Error in transaction callback: {e}")
    
    # Public interface methods
    def submit_transaction_async(self, function_call, tx_type: str, params: Dict[str, Any], 
                               callback: Optional[Callable] = None) -> str:
        """
        Submit transaction asynchronously without waiting for confirmation
        Returns transaction hash immediately
        """
        try:
            # Get API account
            api_account = self._get_api_account()
            
            # Get nonce
            with self.nonce_lock:
                nonce = self.w3.eth.get_transaction_count(api_account.address)
                self.nonce_manager[api_account.address] = max(
                    self.nonce_manager[api_account.address], nonce
                )
                current_nonce = self.nonce_manager[api_account.address]
                self.nonce_manager[api_account.address] += 1
            
            # Build transaction
            transaction = function_call.build_transaction({
                'from': api_account.address,
                'nonce': current_nonce,
                'gas': 500000,
                'gasPrice': self.w3.eth.gas_price,
                'chainId': self.w3.eth.chain_id
            })
            
            # Sign and send
            signed_txn = api_account.sign_transaction(transaction)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_hash_hex = tx_hash.hex()
            
            # Track as pending
            self.pending_transactions[tx_hash_hex] = PendingTransaction(
                tx_hash=tx_hash_hex,
                tx_type=tx_type,
                params=params,
                timestamp=time.time(),
                callback=callback
            )
            
            self.stats['transactions_sent'] += 1
            self.logger.info(f"📤 Submitted {tx_type} transaction: {tx_hash_hex}")
            
            return tx_hash_hex
            
        except Exception as e:
            self.stats['transactions_failed'] += 1
            self.logger.error(f"Failed to submit {tx_type} transaction: {e}")
            raise
    
    def _get_api_account(self):
        """Get the API account for signing transactions"""
        # Use the first account from the blockchain config
        private_key = self.config.get('private_key')
        if not private_key:
            # For development, use a default key
            private_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
        
        return Account.from_key(private_key)
    
    # Convenience methods for common operations
    def register_commuter_async(self, commuter_id: int, address: str, callback: Optional[Callable] = None) -> str:
        """Register commuter asynchronously"""
        if 'facade' not in self.contracts:
            raise ValueError("Facade contract not available")
        
        function_call = self.contracts['facade'].functions.registerCommuter(commuter_id, address)
        return self.submit_transaction_async(
            function_call, 'commuter_registration', 
            {'commuter_id': commuter_id, 'address': address}, 
            callback
        )
    
    def create_request_async(self, commuter_id: int, content_hash: str, callback: Optional[Callable] = None) -> str:
        """Create travel request asynchronously"""
        if 'facade' not in self.contracts:
            raise ValueError("Facade contract not available")
        
        function_call = self.contracts['facade'].functions.createRequestWithHash(commuter_id, content_hash)
        return self.submit_transaction_async(
            function_call, 'request_creation',
            {'commuter_id': commuter_id, 'content_hash': content_hash},
            callback
        )
    
    def submit_offer_async(self, request_id: int, provider_id: int, content_hash: str, 
                          callback: Optional[Callable] = None) -> str:
        """Submit offer asynchronously"""
        if 'facade' not in self.contracts:
            raise ValueError("Facade contract not available")
        
        function_call = self.contracts['facade'].functions.submitOfferHash(request_id, provider_id, content_hash)
        return self.submit_transaction_async(
            function_call, 'offer_submission',
            {'request_id': request_id, 'provider_id': provider_id, 'content_hash': content_hash},
            callback
        )
    
    # State query methods (these are safe to call anytime)
    def is_commuter_registered(self, commuter_id: int) -> bool:
        """Check if commuter is registered (from events)"""
        return f"commuter_{commuter_id}" in self.confirmed_registrations
    
    def is_request_confirmed(self, request_id: int) -> bool:
        """Check if request is confirmed on blockchain"""
        return request_id in self.confirmed_requests
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current statistics"""
        return {
            **self.stats,
            'pending_transactions': len(self.pending_transactions),
            'confirmed_registrations': len(self.confirmed_registrations),
            'confirmed_requests': len(self.confirmed_requests),
            'confirmed_offers': len(self.confirmed_offers),
            'confirmed_matches': len(self.confirmed_matches)
        }
    
    def record_match_async(self, request_id: int, offer_id: int, provider_id: int,
                          price_wei: int, callback: Optional[Callable] = None) -> str:
        """Record match result asynchronously"""
        if 'facade' not in self.contracts:
            raise ValueError("Facade contract not available")

        function_call = self.contracts['facade'].functions.recordMatchResult(
            request_id, offer_id, provider_id, price_wei
        )
        return self.submit_transaction_async(
            function_call, 'match_recording',
            {'request_id': request_id, 'offer_id': offer_id, 'provider_id': provider_id, 'price_wei': price_wei},
            callback
        )

    def wait_for_confirmations(self, timeout: float = 60.0) -> Dict[str, Any]:
        """
        Wait for pending transactions to be confirmed (for testing/demo purposes)
        In production, you would rely purely on events and not wait
        """
        start_time = time.time()
        initial_pending = len(self.pending_transactions)

        self.logger.info(f"Waiting for {initial_pending} pending transactions...")

        while time.time() - start_time < timeout and self.pending_transactions:
            time.sleep(1)
            remaining = len(self.pending_transactions)
            if remaining != initial_pending:
                self.logger.info(f"Progress: {initial_pending - remaining}/{initial_pending} confirmed")

        final_stats = self.get_statistics()
        if self.pending_transactions:
            self.logger.warning(f"{len(self.pending_transactions)} transactions still pending after {timeout}s")
        else:
            self.logger.info("All transactions confirmed!")

        return final_stats

    def shutdown(self):
        """Gracefully shutdown the event monitoring"""
        self.running = False
        if self.event_thread:
            self.event_thread.join(timeout=5)
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5)
