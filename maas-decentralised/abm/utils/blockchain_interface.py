"""
Enhanced BlockchainInterface for Decentralized MaaS
Provides an optimized bridge between ABM simulation and blockchain contracts
with support for NFT marketplace operations, caching, and asynchronous transactions.
"""

import json
import hashlib
import logging
import time
import uuid
from web3 import Web3
"""
Web3 v6 removed the old geth_poa_middleware symbol. To keep compatibility
without changing behavior, import the POA middleware lazily and support both
names (v5: geth_poa_middleware, v6: ExtraDataToPOAMiddleware).
"""
from concurrent.futures import ThreadPoolExecutor
import os
from typing import Dict, List, Any, Tuple, Optional, Union, Callable
from dataclasses import dataclass, field
from collections import deque
import math
from eth_account import Account
from collections import deque, defaultdict
import threading
from enum import Enum


class TransactionState(Enum):
    """Transaction state machine for proper state management"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    RETRYING = "retrying"
    ROLLED_BACK = "rolled_back"


@dataclass
class TransactionData:
    """Enhanced data structure for pending transactions with state management"""
    tx_type: str
    function_name: str
    params: dict
    sender_id: Union[int, str]
    callback: Optional[Callable] = None
    created_at: float = field(default_factory=time.time)
    tx_hash: Optional[str] = None
    state: TransactionState = TransactionState.PENDING
    gas_price: int = 2000000000  # 2 gwei
    gas_limit: int = 500000
    retry_count: int = 0
    max_retries: int = 3
    last_error: Optional[str] = None
    rollback_data: Optional[dict] = None  # Data needed for rollback


class BlockchainInterface:
    def __init__(self, config_file="blockchain_config.json", using_hardhat=True,
                 max_workers=None, cache_ttl=300, async_mode=False):
        """
        Initialize connection to blockchain and load contracts with enhanced performance features
        
        Args:
            config_file: Path to blockchain configuration file
            using_hardhat: Whether using local Hardhat node
            max_workers: Maximum number of worker threads for async operations
            cache_ttl: Time-to-live for cached data in seconds
            async_mode: Whether to use asynchronous transaction processing
        """
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("MarketplaceAPI")  # Renamed to reflect true purpose
        
        
        # Load configuration
        self.config = self._load_config(config_file)
        self.w3 = self._connect_to_blockchain(using_hardhat)
        self.contracts = self._load_contracts()
        self.gas_limit = 1000000  # Default gas limit
        
        # Account management
        self.accounts = {}
        self.nonce_tracker = {}  # Track local nonces for each account
        self.nonce_lock = threading.RLock()  # Synchronize nonce access

        # Enhanced initialization
        # Calculate optimal worker count based on your system
        if max_workers is None:
            # For I/O-bound blockchain operations, can use more threads
            import os
            max_workers = min(32, (os.cpu_count() or 1) * 4)  # 4x CPU cores, cap at 32
        
        self.max_workers = max_workers
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.async_mode = async_mode
        self.cache_ttl = cache_ttl
        
        # Enhanced transaction queue and processing with thread safety
        self.tx_queue = deque()
        self.tx_queue_lock = threading.RLock()  # Protect transaction queue
        self.pending_transactions = {}
        self.pending_transactions_lock = threading.RLock()  # Protect pending transactions
        self.tx_nonce_map = {}  # To track nonces for each account
        self.tx_count = 0

        # Thread-safe offer ID mapping for match recording
        self.offer_id_mapping = {}  # marketplace_offer_id -> blockchain_offer_id
        self.offer_mapping_lock = threading.RLock()  # Protect offer mappings
        self.provider_request_mapping = {}  # "request_id_provider_id" -> blockchain_offer_id
        self._fallback_offer_counter = 0  # Counter for fallback offer IDs

        # Blockchain statistics tracking
        self.blockchain_stats = {
            'total_transactions': 0,
            'successful_transactions': 0,
            'failed_transactions': 0,
            'total_gas_used': 0,
            'recent_tx_hashes': [],
            'transaction_times': [],
            'commuter_registrations': 0,
            'provider_registrations': 0,
            'travel_requests': 0,
            'service_offers': 0,
            'nft_listings': 0,
            'completed_matches': 0,
            'start_time': time.time()
        }

        # Detailed booking tracking
        self.booking_details = []
        self.commuter_profiles = {}
        self.provider_profiles = {}
        self.request_details = {}
        self.offer_details = {}
        self.match_details = {}
        self._booking_ids = set()  # Track unique bookings by match_id
        
        # State caching
        self.state_cache = {
            'commuters': {},
            'providers': {},
            'requests': {},
            'auctions': {},
            'offers': {},
            'nfts': {},
            'marketplace': {},
            'last_updated': {}
        }
        
        # Batch processing tracking
        self.batch_size_limit = 10
        self.current_batch = {
            'registrations': [],
            'requests': [],
            'transactions':[],
            'offers': []
        }
        
        # Statistics and monitoring
        self.stats = {
            'transactions_submitted': 0,
            'transactions_confirmed': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'batch_operations': 0
        }
        
        # Start background tasks if using async mode
        if self.async_mode:
            self.running = True
            self.tx_processor_task = None
            self.cache_updater_task = None
            self._start_background_tasks()
        
        self.logger.info("BlockchainInterface initialized with enhanced performance features")
        
        # MARKETPLACE DATABASE (off-chain storage) with thread safety
        self.marketplace_db = {
            'requests': {},      # Full request data
            'offers': {},        # Full offer data
            'providers': {},     # Provider profiles
            'commuters': {},     # Commuter profiles
            'matches': {},       # Matching results
            'listings': {},      # Secondary market listings
            'nfts': {},          # NFT metadata and ownership
            'notifications': defaultdict(list)  # Provider notifications
        }
        self.marketplace_db_lock = threading.RLock()  # Protect marketplace database

        # Transaction rollback tracking
        self.rollback_operations = {}  # tx_hash -> rollback_function
        self.rollback_lock = threading.RLock()  # Protect rollback operations

        self.steps_per_day = 144   # 144 steps = 1 day
        self.minutes_per_step = 10  # 10 minutes per step

        # Bundle router for decentralized multi-modal routing
        self.bundle_router = None  # Lazy initialization

        self.model = None

    def __del__(self):
        """Cleanup when object is destroyed"""
        self.running = False
        if hasattr(self, 'thread_pool'):
            self.thread_pool.shutdown(wait=False)
            
    def _start_background_tasks(self):
        """Start background tasks for async processing"""
        self.thread_pool.submit(self._transaction_processor)
        self.thread_pool.submit(self._periodic_cache_update)

    def _transaction_processor(self):
        """Continuously process queued transactions in batches."""
        try:
            while getattr(self, 'running', False):
                try:
                    self._process_transaction_batch()
                except Exception as e:
                    self.logger.debug(f"Transaction processor error: {e}")
                time.sleep(0.5)
        except Exception:
            # Ensure background thread never crashes the app
            pass

    def _periodic_cache_update(self):
        """Periodic placeholder for cache updates (no-op for now)."""
        try:
            while getattr(self, 'running', False):
                # Could refresh derived stats or TTL-based invalidation
                self.state_cache['last_updated']['marketplace'] = time.time()
                time.sleep(5)
        except Exception:
            pass
        
    def _load_config(self, config_file):
        """Load blockchain configuration"""
        # Try multiple paths, starting with relative paths to root
        possible_config_paths = [
            config_file,  # As provided
            "../../" + config_file,  # Up two levels (to root)
            "../../../" + config_file,  # Just in case
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../", config_file)  # Absolute path
        ]
        
        for path in possible_config_paths:
            if os.path.exists(path):
                self.logger.info(f"Found config file at {path}")
                with open(path, 'r') as f:
                    return json.load(f)
        
        # Default configuration if no file found
        self.logger.warning(f"Config file {config_file} not found in any location, using defaults")
        default_config = {
            "rpc_url": "http://127.0.0.1:8545",  # Default Hardhat URL
            "chain_id": 31337,                   # Default Hardhat chain ID
                                                 #it ensures transactions don't accidentally get sent to mainnet Ethereum (chain ID 1) or other networks
            "deployment_info": "../../deployment-info.json",  # Point to root
            "max_batch_size": 10,
            "tx_confirmation_blocks": 1,
            "gas_price_strategy": "medium",
            "retry_count": 3,
            "retry_delay": 2  # seconds
        }
        return default_config
    
    def _connect_to_blockchain(self, using_hardhat=True):
        """Connect to the blockchain network with optimized middleware"""
        w3 = Web3(Web3.HTTPProvider(self.config["rpc_url"]))

        # Add POA middleware only when not using Hardhat (e.g., Polygon/POA chains)
        if not using_hardhat:
            poa_middleware = None
            try:
                # Web3 v5 style
                from web3.middleware import geth_poa_middleware as poa_middleware  # type: ignore
            except Exception:
                try:
                    # Web3 v6 replacement
                    from web3.middleware import ExtraDataToPOAMiddleware as poa_middleware  # type: ignore
                except Exception:
                    poa_middleware = None

            if poa_middleware is not None:
                w3.middleware_onion.inject(poa_middleware, layer=0)

        if not w3.is_connected():
            raise ConnectionError(f"Failed to connect to blockchain at {self.config['rpc_url']}")

        self.logger.info(f"Connected to blockchain: {w3.is_connected()}")
        return w3
    
    def _load_contracts(self):
        """Load contract ABIs and addresses with error handling"""
        contracts = {}
        
        try:
            # Go up two directories to find deployment info
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            deployment_info_path = os.path.join(base_dir, "deployment-info.json")
            
            if not os.path.exists(deployment_info_path): 
                self.logger.error(f"Deployment info file {deployment_info_path} not found")
                return {}
                
            with open(deployment_info_path, 'r') as f:
                deployment_info = json.load(f)
                
            # Set correct path to artifacts directory
            abi_dir = os.path.join(base_dir, "artifacts", "contracts")
            
            # Define contracts to load
            contract_keys = [
                "registry", "request", "auction", 
                "nft", "market", "facade", "mockToken"
            ]
            
            # Map contract keys to ABI file patterns
            abi_patterns = {
                "registry": "MaaSRegistry.sol/MaaSRegistry.json",
                "request": "MaaSRequest.sol/MaaSRequest.json",
                "auction": "MaaSAuction.sol/MaaSAuction.json",
                "nft": "MaaSNFT.sol/MaaSNFT.json",
                "market": "MaaSMarket.sol/MaaSMarket.json",
                "facade": "MaaSFacade.sol/MaaSFacade.json",
                "mockToken": "MockERC20.sol/MockERC20.json"
            }
            
            # Load each contract
            for key in contract_keys:
                if key in deployment_info:
                    address = deployment_info[key]
                    abi_file = os.path.join(abi_dir, abi_patterns.get(key, ""))
                    
                    self.logger.info(f"Looking for ABI file at: {abi_file}")
                    
                    try:
                        if os.path.exists(abi_file):
                            with open(abi_file, 'r') as abi_f:
                                abi_data = json.load(abi_f)
                                abi = abi_data["abi"]
                                contracts[key] = self.w3.eth.contract(address=address, abi=abi)
                        else:
                            self.logger.warning(f"ABI file {abi_file} not found for {key}")
                    except Exception as e:
                        self.logger.error(f"Error loading ABI for {key}: {e}")
                else:
                    self.logger.warning(f"No address found for {key} in deployment info")
            
            return contracts
            
        except Exception as e:
            self.logger.error(f"Error loading contracts: {e}")
            return {}
    
    # ================ Enhanced Account Management ================
    
    def create_account(self, agent_id, agent_type):
        """
        Create or assign an Ethereum account for an agent with improved error handling
        
        Args:
            agent_id: Unique identifier for the agent
            agent_type: Type of agent ('commuter' or 'provider')
            
        Returns:
            str: Account address or None if failed
        """
        try:
            # In production, you might load existing keys from secure storage
            # For simulation, create a NEW account
            acct = self.w3.eth.account.create() 
            
            # Store account details
            self.accounts[agent_id] = {
                "address": acct.address,
                "private_key": acct.key.hex(),
                "type": agent_type,
                "created_at": time.time(),
                "tx_count": 0
            }
            
            # Fund account with ETH for gas (in development)
            self._fund_account(acct.address)
            
            # Initialize nonce tracking
            with self.nonce_lock:
                self.nonce_tracker[acct.address] = self.w3.eth.get_transaction_count(acct.address)
                self.tx_nonce_map[acct.address] = self.nonce_tracker[acct.address]
            
            self.logger.info(f"Created account {acct.address} for {agent_type} {agent_id}")
            return acct.address
            
        except Exception as e:
            self.logger.error(f"Error creating account: {e}")
            return None
    
    def _fund_account(self, address, amount=1.0):
        """Fund an account with ETH and tokens for simulation"""
        try:
            # Get the first account from the node (usually has funds)
            admin = self.w3.eth.accounts[0]
            
            # Send ETH
            tx_hash = self.w3.eth.send_transaction({
                'from': admin,
                'to': address,
                'value': Web3.to_wei(amount, 'ether')
            })
            
            # Wait for transaction
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # If using mock token, send some tokens too
            if "mockToken" in self.contracts:
                token = self.contracts["mockToken"]
                tx = token.functions.transfer(
                    address,
                    Web3.to_wei(amount, 'ether')
                ).transact({'from': admin})
                self.w3.eth.wait_for_transaction_receipt(tx)
                
            self.logger.info(f"Funded account {address} with {amount} ETH and 1000 tokens")
            return True
            
        except Exception as e:
            self.logger.error(f"Error funding account: {e}")
            return False
    
    # ================ MARKETPLACE API FUNCTIONS ================
    
    def create_travel_request_marketplace(self, commuter, request):
        """
        MARKETPLACE API: Create travel request
        1. Store full request in marketplace DB
        2. Push only hash to blockchain
        """
        request_id = request.get('request_id', int(uuid.uuid4().int & (2**64 - 1)))

        # Prepare full request data
        full_request = {
            'request_id': request_id,
            'commuter_id': commuter.unique_id,
            'origin': request['origin'],
            'destination': request['destination'],
            'start_time': request.get('start_time'),
            'travel_purpose': request.get('travel_purpose', 'work'),
            'flexible_time': request.get('flexible_time', 'medium'),
            'requirement_keys': request.get('requirement_keys', []),
            'requirement_values': request.get('requirement_values', []),
            'max_price': request.get('max_price', 100),
            'created_at': time.time(),
            'status': 'active'
        }

        # Generate content hash
        content_hash = self._generate_content_hash(full_request)

        # Prepare blockchain transaction data
        blockchain_data = {
            'request_id': request_id,
            'commuter_id': commuter.unique_id,
            'content_hash': content_hash,
            'timestamp': int(time.time())
        }

        tx_data = TransactionData(
            tx_type="request",
            function_name="createRequestWithHash",
            params=blockchain_data,
            sender_id=commuter.unique_id
        )

        # Define off-chain operation
        def off_chain_operation():
            with self.marketplace_db_lock:
                self.marketplace_db['requests'][request_id] = full_request

            # Filter and notify eligible providers
            self._notify_eligible_providers(request_id, full_request)

            return request_id

        # Define rollback operation
        def rollback_operation():
            with self.marketplace_db_lock:
                if request_id in self.marketplace_db['requests']:
                    del self.marketplace_db['requests'][request_id]

            self.logger.info(f"🔄 Rolled back request {request_id} from marketplace DB")

        # Execute atomically
        if self.async_mode:
            # For async mode, queue the transaction with rollback info
            tx_data.rollback_data = {'operation': rollback_operation}
            try:
                off_chain_operation()  # Execute off-chain first
                self.queue_transaction(tx_data)
                self.logger.info(f"Request {request_id} created in marketplace, hash {content_hash[:8]}... queued for blockchain")
                return True, request_id
            except Exception as e:
                self.logger.error(f"Error creating marketplace request: {e}")
                return False, None
        else:
            # For sync mode, use atomic transaction
            success, result = self.atomic_transaction(tx_data, off_chain_operation, rollback_operation)
            if success:
                self.logger.info(f"Request {request_id} created in marketplace, hash {content_hash[:8]}... confirmed on blockchain")
                return True, request_id
            else:
                self.logger.error(f"Failed to create request {request_id} atomically")
                return False, None
    
    def submit_offer_marketplace(self, provider, request_id, price, details=None):
        """
        MARKETPLACE API: Submit offer from provider
        1. Store full offer in marketplace DB
        2. Push only essential data to blockchain
        """
        # Generate offer ID
        offer_id = int(request_id * 1000 + provider.unique_id)

        # Prepare full offer data
        full_offer = {
            'offer_id': offer_id,
            'request_id': request_id,
            'provider_id': provider.unique_id,
            'price': price,
            'mode': self._get_provider_mode(provider),
            'route_details': details.get('route', []) if details else [],
            'estimated_time': details.get('time', 30) if details else 30,
            'depart_time': details.get('depart_time') if details else None,
            'start_time': details.get('start_time') if details else None,
            'arrive_time': details.get('arrive_time') if details else None,
            'origin': details.get('route', [None, None])[0] if details else None,
            'destination': details.get('route', [None, None])[-1] if details else None,
            'capacity': getattr(provider, 'available_capacity', 1),
            'quality_score': getattr(provider, 'quality_score', 70),
            'reliability': getattr(provider, 'reliability', 70),
            'created_at': time.time(),
            'status': 'submitted'
        }

        # Generate offer hash
        offer_hash = self._generate_content_hash(full_offer)

        # Prepare blockchain transaction data
        blockchain_data = {
            'offer_id': offer_id,
            'request_id': request_id,
            'provider_id': provider.unique_id,
            'price_hash': hashlib.sha256(str(price).encode()).hexdigest(),
            'offer_hash': offer_hash,
            'timestamp': int(time.time())
        }

        tx_data = TransactionData(
            tx_type="offer",
            function_name="submitOfferHash",
            params=blockchain_data,
            sender_id=provider.unique_id
        )

        # Define off-chain operation
        def off_chain_operation():
            with self.marketplace_db_lock:
                self.marketplace_db['offers'][offer_id] = full_offer
            # Capture offer details for analytics (mode attribution)
            self.store_offer_details(offer_id, full_offer)
            return offer_id

        # Define rollback operation
        def rollback_operation():
            with self.marketplace_db_lock:
                if offer_id in self.marketplace_db['offers']:
                    del self.marketplace_db['offers'][offer_id]

            # Remove from offer mapping if exists
            with self.offer_mapping_lock:
                if offer_id in self.offer_id_mapping:
                    del self.offer_id_mapping[offer_id]

            self.logger.info(f"🔄 Rolled back offer {offer_id} from marketplace DB")

        # Execute atomically
        if self.async_mode:
            # For async mode, queue the transaction with rollback info
            tx_data.rollback_data = {'operation': rollback_operation}
            try:
                off_chain_operation()  # Execute off-chain first
                self.queue_transaction(tx_data)
                self.logger.info(f"Offer {offer_id} submitted to marketplace for request {request_id}")
                return True
            except Exception as e:
                self.logger.error(f"Error submitting marketplace offer: {e}")
                return False
        else:
            # For sync mode, use atomic transaction
            success, result = self.atomic_transaction(tx_data, off_chain_operation, rollback_operation)
            if success:
                self.logger.info(f"Offer {offer_id} submitted to marketplace for request {request_id} and confirmed on blockchain")
                return True
            else:
                self.logger.error(f"Failed to submit offer {offer_id} atomically")
                return False

    def list_nft_for_sale(self, nft_id, price, time_parameters=None):
        """
        MARKETPLACE API: List NFT for secondary sale with dynamic pricing support.
        """
        try:
            if price is None or price <= 0:
                self.logger.error(f"Invalid listing price for NFT {nft_id}: {price}")
                return False

            current_time = time.time()
            initial_price = time_parameters.get('initial_price', price) if time_parameters else price
            final_price = time_parameters.get('final_price', price) if time_parameters else price
            decay_duration = time_parameters.get('decay_duration', 0) if time_parameters else 0
            decay_rate = time_parameters.get('decay_rate', 0.0) if time_parameters else 0.0

            listing_id = f"list_{nft_id}_{int(current_time)}"

            # Prepare off-chain listing payload (time/value fields will be filled in off_chain_operation)
            listing_data = {
                'listing_id': listing_id,
                'nft_id': nft_id,
                'price': price,
                'current_price': price,
                'initial_price': initial_price,
                'final_price': final_price,
                'decay_duration': decay_duration,
                'decay_rate': decay_rate,
                'listed_at': current_time,
                'status': 'active'
            }

            def off_chain_operation():
                with self.marketplace_db_lock:
                    nft_store = self.marketplace_db.setdefault('nfts', {})
                    listing_store = self.marketplace_db.setdefault('listings', {})

                    owner_id = nft_store.get(nft_id, {}).get('owner_id', 'unknown')
                    nft_store.setdefault(nft_id, {})['owner_id'] = owner_id
                    nft_store[nft_id]['status'] = 'listed'

                    # Pull timing/route/mode metadata from NFT if available
                    nft_meta = nft_store.get(nft_id, {})
                    service_time = nft_meta.get('service_time')
                    duration_val = nft_meta.get('duration', 0)
                    origin = nft_meta.get('origin', [0, 0])
                    destination = nft_meta.get('destination', [0, 0])
                    mode = nft_meta.get('mode', nft_meta.get('details', {}).get('mode') if isinstance(nft_meta.get('details'), dict) else 'unknown')
                    arrive_time = None
                    if service_time is not None and duration_val is not None:
                        arrive_time = service_time + duration_val

                    listing_data.update({
                        'seller_id': owner_id,
                        'origin': origin,
                        'destination': destination,
                        'mode': mode,
                        'depart_time': service_time,
                        'start_time': service_time,
                        'estimated_time': duration_val,
                        'arrive_time': arrive_time
                    })
                    listing_store[listing_id] = listing_data

                return listing_id

            def rollback_operation():
                with self.marketplace_db_lock:
                    listings = self.marketplace_db.get('listings', {})
                    if listing_id in listings:
                        del listings[listing_id]
                    if nft_id in self.marketplace_db.get('nfts', {}):
                        self.marketplace_db['nfts'][nft_id]['status'] = 'active'

                self.logger.info(f"🔄 Rolled back NFT listing {listing_id}")

            tx_data = TransactionData(
                tx_type="nft_list",
                function_name="listNFTWithDynamicPricing",
                params={
                    'tokenId': nft_id,
                    'initialPrice': initial_price,
                    'finalPrice': final_price,
                    'decayDuration': decay_duration
                },
                sender_id=self.marketplace_db.get('nfts', {}).get(nft_id, {}).get('owner_id', 'unknown')
            )

            if self.async_mode:
                tx_data.rollback_data = {'operation': rollback_operation}
                off_chain_operation()
                self.queue_transaction(tx_data)
                self.logger.info(f"✅ NFT {nft_id} listed for sale at {price} (Dynamic: {time_parameters is not None})")
                return True

            success, _ = self.atomic_transaction(tx_data, off_chain_operation, rollback_operation)
            if success:
                self.logger.info(f"✅ NFT {nft_id} listed for sale at {price} (Dynamic: {time_parameters is not None})")
                return True

            self.logger.warning(f"Failed to list NFT {nft_id} for sale")
            return False

        except Exception as e:
            self.logger.error(f"Error listing NFT {nft_id}: {e}")
            return False

    def purchase_nft(self, nft_id, buyer_id):
        """
        MARKETPLACE API: Execute secondary market purchase of an NFT.
        Transfers ownership from seller to buyer and records the trade for analytics.
        """
        try:
            # -----------------------
            # 1) Off-chain checks and updates
            # -----------------------
            with self.marketplace_db_lock:
                listings = self.marketplace_db.get('listings', {})
                listing_id = next(
                    (lid for lid, l in listings.items()
                     if l.get('nft_id') == nft_id and l.get('status') == 'active'),
                    None
                )

                if not listing_id:
                    self.logger.warning(f"No active listing found for NFT {nft_id}")
                    return False

                listing = listings[listing_id]
                price = listing.get('current_price', listing.get('price', 0))
                seller_id = listing.get('seller_id', 'unknown')

                # Update ownership
                nft_store = self.marketplace_db.setdefault('nfts', {})
                nft = nft_store.get(nft_id)
                if nft:
                    nft['owner_id'] = buyer_id
                    nft['status'] = 'active'

                # Close listing
                listing['status'] = 'sold'
                listing['buyer_id'] = buyer_id

                # Record match for analytics (marks as secondary via source)
                match_id = f"sec_sale_{int(time.time())}_{nft_id}_{buyer_id}"
                offer_id = listing.get('offer_id', '')
                actual_mode = listing.get('mode') or listing.get('details', {}).get('mode') or 'unknown'
                provider_type = actual_mode
                sale_record = {
                    'booking_id': match_id,
                    'match_id': match_id,
                    'commuter_id': buyer_id,
                    'provider_id': seller_id,
                    'price': price,
                    'source': 'nft_market_secondary',
                    'timestamp': time.time(),
                    'status': 'completed',
                    'origin': listing.get('origin', [0, 0]),
                    'destination': listing.get('destination', [0, 0]),
                    'provider_type': provider_type,
                    'mode': actual_mode,
                    'offer_id': offer_id
                }
                self.store_match_details(match_id, sale_record)
                if match_id not in self._booking_ids:
                    self.booking_details.append(sale_record)
                    self._booking_ids.add(match_id)

            # -----------------------
            # 2) Blockchain transaction (simulated in skip mode)
            # -----------------------
            tx_data = TransactionData(
                tx_type="nft_buy",
                function_name="purchaseNFT",
                params={'tokenId': nft_id, 'price': price},
                sender_id=buyer_id
            )

            success, _ = self.atomic_transaction(tx_data)

            if success:
                current_tick = getattr(self.model, "current_step", None) if hasattr(self, "model") else None
                self._record_transaction(
                    offer_id,
                    buyer_id,
                    price,
                    tx_type="secondary",
                    explicit_tick=current_tick,
                    source_override='nft_market_secondary',
                    start_time=listing.get('depart_time') or listing.get('start_time'),
                    duration=listing.get('estimated_time'),
                    mode_override=actual_mode
                )
                self.logger.info(f"✅ NFT {nft_id} purchased by {buyer_id} for ${price:.2f}")
                return True

        except Exception as e:
            self.logger.error(f"Error purchasing NFT {nft_id}: {e}")
            return False

        return False
    
    def run_marketplace_matching(self, request_id):
        """
        MARKETPLACE API: Run matching algorithm off-chain
        Complex matching logic happens here, not on blockchain
        """
        try:
            # Get request from marketplace DB
            request = self.marketplace_db['requests'].get(request_id)
            if not request:
                return False, None
            
            # Get all offers for this request
            relevant_offers = [
                offer for offer in self.marketplace_db['offers'].values()
                if offer.get('request_id') == request_id and offer['status'] == 'submitted'
            ]
            
            if not relevant_offers:
                return False, None
            
            # Run complex matching algorithm (off-chain)
            best_offer = self._run_matching_algorithm(request, relevant_offers)
            
            if not best_offer:
                return False, None
            
            # Store match result
            match_result = {
                'request_id': request_id,
                'winning_offer_id': best_offer['offer_id'],
                'provider_id': best_offer['provider_id'],
                'final_price': best_offer['price'],
                'match_time': time.time(),
                'match_score': best_offer.get('match_score', 0)
            }

            self.marketplace_db['matches'][request_id] = match_result

            # Store comprehensive match details for booking analysis
            request_details = self.request_details.get(request_id, {})
            offer_details = self.offer_details.get(best_offer['offer_id'], {})

            match_data = {
                'match_id': request_id,  # Use request_id as match_id
                'commuter_id': request.get('commuter_id'),
                'provider_id': best_offer['provider_id'],
                'request_id': request_id,
                'offer_id': best_offer['offer_id'],
                'price': best_offer['price'],
                'mode': best_offer.get('mode'),
                'origin': request.get('origin'),
                'destination': request.get('destination'),
                'route_details': {
                    'distance': offer_details.get('distance', 0),
                    'duration': offer_details.get('estimated_time', 0),
                    'route': offer_details.get('route', [])
                },
                'match_time': time.time(),
                'match_score': best_offer.get('match_score', 0)
            }

            self.store_match_details(request_id, match_data)
            
            # Push match result to blockchain for settlement
            blockchain_result = {
                'request_id': request_id,
                'winning_offer_id': best_offer['offer_id'],
                'provider_id': best_offer['provider_id'],
                'price': best_offer['price']
            }
            
            if self.async_mode:
                self.queue_transaction(
                    TransactionData(
                        tx_type="match",
                        function_name="recordMatchResult",
                        params=blockchain_result,
                        sender_id=0  # System transaction
                    )
                )
            
            self.logger.info(f"Matching completed for request {request_id}, winner: offer {best_offer['offer_id']}")
            return True, match_result
            
        except Exception as e:
            self.logger.error(f"Error in marketplace matching: {e}")
            return False, None
    
    def _notify_eligible_providers(self, request_id, request_data):
        """Filter and notify only eligible providers"""
        origin = request_data['origin']
        max_distance = 10  # Configurable
        
        for provider_id, provider_data in self.marketplace_db['providers'].items():
            # Check distance
            if 'location' in provider_data:
                distance = self._calculate_distance(origin, provider_data['location'])
                if distance <= max_distance:
                    # Add to notification queue
                    notification = {
                        'request_id': request_id,
                        'notified_at': time.time(),
                        'distance': distance
                    }
                    self.marketplace_db['notifications'][provider_id].append(notification)
                    self.logger.debug(f"Provider {provider_id} notified about request {request_id}")
    
    def _run_matching_algorithm(self, request, offers):
        """
        Complex matching algorithm (runs off-chain in marketplace)
        This replaces the on-chain auction logic
        """
        scored_offers = []
        
        for offer in offers:
            score = 0
            
            # Price score (40% weight)
            max_price = request.get('max_price', 100)
            if offer['price'] <= max_price:
                price_score = (max_price - offer['price']) / max_price * 40
                score += price_score
            
            # Quality score (30% weight)
            quality_score = offer.get('quality_score', 50) / 100 * 30
            score += quality_score
            
            # Reliability score (20% weight)
            reliability_score = offer.get('reliability', 50) / 100 * 20
            score += reliability_score
            
            # Time score (10% weight)
            time_score = 10 if offer.get('estimated_time', 60) < 45 else 5
            score += time_score
            
            offer['match_score'] = score
            scored_offers.append(offer)
        
        # Return best offer
        if scored_offers:
            return max(scored_offers, key=lambda x: x['match_score'])
        return None
    
    def _generate_content_hash(self, data):
        """Generate hash of content for blockchain storage"""
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()

    def process_requests_batch(self, request_batch):
        """
        Handle a batch of travel requests safely.
        - Skips duplicates that are already in the marketplace DB
        - Falls back to a minimal commuter stub if the agent isn't available
        - Returns list of (success, request_id or error) tuples
        """
        results = []

        for request in request_batch:
            request_id = request.get('request_id')
            commuter_id = request.get('commuter_id')

            # Ensure we have a request_id to work with
            if request_id is None:
                request_id = int(uuid.uuid4().int & (2**64 - 1))
                request['request_id'] = request_id

            try:
                # If the request is already stored, treat it as processed
                with self.marketplace_db_lock:
                    if request_id in self.marketplace_db.get('requests', {}):
                        results.append((True, request_id))
                        continue

                # Look up the commuter agent from the model if available
                commuter = None
                if hasattr(self, "model") and hasattr(self.model, "commuters"):
                    commuter = self.model.commuters.get(commuter_id)

                # Fall back to a lightweight stub with just the ID
                if commuter is None:
                    commuter = type("CommuterStub", (), {"unique_id": commuter_id})()

                success, created_id = self.create_travel_request(commuter, request)
                results.append((success, created_id))

            except Exception as e:
                self.logger.error(f"Error processing request {request_id}: {e}")
                results.append((False, str(e)))

        return results
    
    def _get_provider_mode(self, provider):
        """Get provider mode"""
        if hasattr(provider, 'mode_type'):
            return provider.mode_type
        return 'car'
    
    def _calculate_distance(self, point1, point2):
        """Calculate distance between two points"""
        return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
    
    # ================ BACKWARDS COMPATIBILITY ================
    # Keep these method names but redirect to marketplace functions
    
    def create_travel_request(self, commuter, request):
        """Redirect to marketplace function"""
        return self.create_travel_request_marketplace(commuter, request)
    
    def submit_offer(self, provider, request_id, price, details=None):
        """Redirect to marketplace function"""
        return self.submit_offer_marketplace(provider, request_id, price, details)
    
    def finalize_auction(self, request_id):
        """Now runs marketplace matching instead of blockchain auction"""
        return self.run_marketplace_matching(request_id)
    
    # ================ REGISTRATION FUNCTIONS (Keep as is) ================

    def is_commuter_registered(self, commuter_id):
        """Return True if a commuter account exists."""
        return commuter_id in self.accounts

    def is_provider_registered(self, provider_id):
        """Return True if a provider account exists."""
        return provider_id in self.accounts

    def register_commuter(self, commuter_agent):
        """Register commuter - stores profile in marketplace DB and blockchain"""
        try:
            if commuter_agent.unique_id in self.accounts:
                return True, self.accounts[commuter_agent.unique_id]["address"]

            # Create account
            account = Account.create()
            address = account.address
            private_key = account.key.hex()

            self.accounts[commuter_agent.unique_id] = {
                "address": address,
                "private_key": private_key
            }

            # Store profile in marketplace DB
            self.marketplace_db['commuters'][commuter_agent.unique_id] = {
                'id': commuter_agent.unique_id,
                'age': getattr(commuter_agent, 'age', 30),
                'income_level': getattr(commuter_agent, 'income_level', 'middle'),
                'preferences': getattr(commuter_agent, 'preferences', {}),
                'registered_at': time.time()
            }

            # Register on blockchain
            try:
                self.register_commuter_on_blockchain(commuter_agent.unique_id, address)
            except Exception as e:
                # If already registered on-chain (e.g., same commuter_id from prior runs), keep going
                if "exists" in str(e).lower():
                    self.logger.warning(f"Commuter {commuter_agent.unique_id} already registered on-chain, reusing account")
                else:
                    raise

            self.logger.info(f"Commuter {commuter_agent.unique_id} registered in marketplace and blockchain")
            return True, address

        except Exception as e:
            self.logger.error(f"Error registering commuter: {e}")
            return False, None
    
    def register_provider(self, provider_agent):
        """Register provider - stores profile in marketplace DB"""
        try:
            if provider_agent.unique_id in self.accounts:
                return True, self.accounts[provider_agent.unique_id]["address"]
            
            # Create account
            account = Account.create()
            address = account.address
            private_key = account.key.hex()
            
            self.accounts[provider_agent.unique_id] = {
                "address": address,
                "private_key": private_key
            }
            
            # Store profile in marketplace DB
            profile = {
                'id': provider_agent.unique_id,
                'company_name': getattr(provider_agent, 'company_name', f"Provider-{provider_agent.unique_id}"),
                'mode_type': getattr(provider_agent, 'mode_type', 'car'),
                'capacity': getattr(provider_agent, 'capacity', 4),
                'base_price': getattr(provider_agent, 'base_price', 10),
                'location': getattr(provider_agent, 'service_center', [0, 0]),
                'quality_score': getattr(provider_agent, 'quality_score', 70),
                'reliability': getattr(provider_agent, 'reliability', 70),
                'registered_at': time.time()
            }
            self.marketplace_db['providers'][provider_agent.unique_id] = profile
            # Also store for analytics/mode attribution
            self.provider_profiles[provider_agent.unique_id] = profile

            # Register on blockchain
            mode_mapping = {'car': 1, 'bike': 2, 'bus': 3, 'train': 4}
            mode_id = mode_mapping.get(getattr(provider_agent, 'mode_type', 'car'), 1)
            self.register_provider_on_blockchain(provider_agent.unique_id, address, mode_id)

            self.logger.info(f"Provider {provider_agent.unique_id} registered in marketplace and blockchain")
            return True, address
            
        except Exception as e:
            self.logger.error(f"Error registering provider: {e}")
            return False, None
    
    # ================ ATOMIC OPERATIONS & ROLLBACK MECHANISMS ================

    def atomic_transaction(self, tx_data, off_chain_operation=None, rollback_operation=None):
        """
        Execute transaction atomically with proper rollback on failure

        Args:
            tx_data: Transaction data to execute
            off_chain_operation: Function to execute off-chain changes
            rollback_operation: Function to rollback off-chain changes on failure

        Returns:
            Tuple of (success, result)
        """
        tx_data.state = TransactionState.PENDING
        rollback_needed = False
        skip_chain = os.getenv("SKIP_CHAIN_PROCESSING", "").lower() in ("1", "true", "yes")

        try:
            # Execute off-chain operation first if provided
            if off_chain_operation:
                off_chain_result = off_chain_operation()
                rollback_needed = True

                # Store rollback operation for later use
                if rollback_operation:
                    tx_data.rollback_data = {'operation': rollback_operation, 'result': off_chain_result}

            # Short-circuit blockchain processing when running in skip mode
            if skip_chain:
                tx_data.state = TransactionState.CONFIRMED
                self.blockchain_stats['total_transactions'] += 1
                self.blockchain_stats['successful_transactions'] += 1
                # Ensure type-specific counters still increment so analytics/plots work in skip mode
                self._update_transaction_stats(tx_data, success=True)
                self.logger.info(f"⚡ SKIP_CHAIN_PROCESSING: simulated success for {tx_data.tx_type} - {tx_data.function_name}")
                return True, {"tx_hash": "skipped", "simulated": True}

            # Execute blockchain transaction
            tx_data.state = TransactionState.SUBMITTED
            blockchain_result = self._execute_blockchain_transaction_with_retry(tx_data)

            tx_data.state = TransactionState.CONFIRMED
            self.logger.info(f"✅ ATOMIC TX SUCCESS: {tx_data.tx_type} - {tx_data.function_name}")

            return True, blockchain_result

        except Exception as e:
            # Treat idempotent "exists" errors as successful no-ops to keep the simulation flowing
            if "exists" in str(e).lower():
                self.logger.warning(f"ℹ️ Transaction already exists, treating as success: {tx_data.tx_type}")
                return True, None

            tx_data.state = TransactionState.FAILED
            tx_data.last_error = str(e)

            # Rollback off-chain changes if needed
            if rollback_needed and rollback_operation:
                try:
                    rollback_operation()
                    tx_data.state = TransactionState.ROLLED_BACK
                    self.logger.info(f"🔄 ROLLBACK SUCCESS: {tx_data.tx_type}")
                except Exception as rollback_error:
                    self.logger.error(f"❌ ROLLBACK FAILED: {tx_data.tx_type} - {rollback_error}")

            self.logger.error(f"❌ ATOMIC TX FAILED: {tx_data.tx_type} - {e}")
            return False, None

    def _execute_blockchain_transaction_with_retry(self, tx_data):
        """Execute blockchain transaction with retry logic"""
        for attempt in range(tx_data.max_retries):
            try:
                tx_data.retry_count = attempt
                if attempt > 0:
                    tx_data.state = TransactionState.RETRYING
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    self.logger.info(f"🔄 RETRY {attempt}/{tx_data.max_retries} for {tx_data.tx_type} in {wait_time}s")
                    time.sleep(wait_time)

                return self._execute_blockchain_transaction(tx_data)

            except Exception as e:
                tx_data.last_error = str(e)

                # Check if error is recoverable
                if not self._is_recoverable_error(e) or attempt == tx_data.max_retries - 1:
                    raise

                self.logger.warning(f"⚠️ RECOVERABLE ERROR (attempt {attempt + 1}): {e}")

        raise Exception(f"Transaction failed after {tx_data.max_retries} attempts")

    def _is_recoverable_error(self, error):
        """Determine if an error is recoverable and worth retrying"""
        error_str = str(error).lower()

        # Recoverable errors
        recoverable_errors = [
            "nonce too low",
            "replacement transaction underpriced",
            "network error",
            "connection timeout",
            "gas price too low"
        ]

        # Non-recoverable errors
        non_recoverable_errors = [
            "insufficient funds",
            "execution reverted",
            "invalid signature",
            "contract not found"
        ]

        # Check for non-recoverable errors first
        for non_recoverable in non_recoverable_errors:
            if non_recoverable in error_str:
                return False

        # Check for recoverable errors
        for recoverable in recoverable_errors:
            if recoverable in error_str:
                return True

        # Default to non-recoverable for unknown errors
        return False

    def rollback_failed_transaction(self, tx_data):
        """Rollback off-chain state changes for failed transactions"""
        try:
            if tx_data.rollback_data and 'operation' in tx_data.rollback_data:
                rollback_op = tx_data.rollback_data['operation']
                rollback_op()
                tx_data.state = TransactionState.ROLLED_BACK
                self.logger.info(f"🔄 ROLLBACK COMPLETED: {tx_data.tx_type}")
                return True
        except Exception as e:
            self.logger.error(f"❌ ROLLBACK FAILED: {tx_data.tx_type} - {e}")
            return False

        return False

    # ================ TRANSACTION PROCESSING (Enhanced) ================
    
    def queue_transaction(self, transaction_data):
        """Queue transaction for batch processing with thread safety"""
        with self.tx_queue_lock:
            self.tx_queue.append(transaction_data)
            queue_size = len(self.tx_queue)

        if queue_size >= self.batch_size_limit and self.async_mode:
            self.thread_pool.submit(self._process_transaction_batch)
    
    def _process_transaction_batch(self):
        """Process queued transactions with enhanced error handling and atomicity"""
        # Thread-safe queue access
        with self.tx_queue_lock:
            if not self.tx_queue:
                return

            # Extract all queued transactions
            batch = []
            while self.tx_queue:
                batch.append(self.tx_queue.popleft())

        if not batch:
            return

        # Add delay to encourage proper blockchain communication patterns
        time.sleep(0.1)  # 100ms delay before processing batch

        self.logger.info(f"Processing {len(batch)} transactions - SENDING TO BLOCKCHAIN")

        # Send transactions sequentially to avoid nonce conflicts
        for i, tx in enumerate(batch):
            self.logger.info(f"Processing transaction {i+1}/{len(batch)}: {tx.tx_type} - {tx.function_name}")

            # Add small delay between transactions for better blockchain communication
            if i > 0:  # Don't delay the first transaction
                time.sleep(0.02)  # 20ms delay between transactions

            # Use atomic transaction processing
            success, result = self.atomic_transaction(tx)

            if success:
                self.tx_count += 1
                self.logger.info(f"✅ TX SUCCESS: {tx.tx_type} - {tx.function_name}")

                # Update blockchain statistics
                self.blockchain_stats['successful_transactions'] += 1
                self._update_transaction_stats(tx, success=True)
            else:
                self.logger.error(f"❌ TX FAILED: {tx.tx_type} - {tx.function_name}: {tx.last_error}")

                # Update blockchain statistics
                self.blockchain_stats['failed_transactions'] += 1
                self._update_transaction_stats(tx, success=False)

                # Handle specific error types
                if tx.last_error and "nonce" in tx.last_error.lower():
                    self.logger.warning(f"Nonce error detected, resetting tracker")
                    self._reset_nonce_tracker()

            # Small delay between transactions to ensure proper ordering
            time.sleep(0.2)  # Increased delay for better nonce management

    def _execute_blockchain_transaction(self, tx_data):
        """Execute a single transaction on the blockchain"""
        # In skip-chain mode, short-circuit blockchain calls for speed
        if os.getenv("SKIP_CHAIN_PROCESSING", "").lower() in ("1", "true", "yes"):
            self.blockchain_stats['total_transactions'] += 1
            self.blockchain_stats['successful_transactions'] += 1
            self.logger.info(f"⚡ SKIP_CHAIN_PROCESSING: bypassed on-chain call for {tx_data.tx_type} - {tx_data.function_name}")
            return {"tx_hash": "skipped", "simulated": True}

        try:
            # Get the marketplace API account (should have ETH for gas)
            api_account = self._get_api_account()

            # Route to appropriate contract function based on transaction type
            if tx_data.tx_type == "request":
                return self._execute_request_transaction(tx_data, api_account)
            elif tx_data.tx_type == "offer":
                return self._execute_offer_transaction(tx_data, api_account)
            elif tx_data.tx_type == "match":
                return self._execute_match_transaction(tx_data, api_account)
            elif tx_data.tx_type == "completion":
                return self._execute_completion_transaction(tx_data, api_account)
            elif tx_data.tx_type == "registration":
                return self._execute_registration_transaction(tx_data, api_account)
            elif tx_data.tx_type == "nft_list":
                return self._execute_nft_listing_transaction(tx_data, api_account)
            else:
                raise ValueError(f"Unknown transaction type: {tx_data.tx_type}")

        except Exception as e:
            self.logger.error(f"Transaction execution failed: {str(e)}")
            raise

    def _get_api_account(self):
        """Get the marketplace API account with private key for signing transactions"""
        # Use the API private key from config
        api_private_key = self.config.get("api_private_key", "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80")
        account = Account.from_key(api_private_key)

        # Initialize nonce tracker for API account if not exists
        if account.address not in self.nonce_tracker:
            with self.nonce_lock:
                self.nonce_tracker[account.address] = self.w3.eth.get_transaction_count(account.address)

        return account

    def _execute_request_transaction(self, tx_data, api_account):
        """Execute a request creation transaction"""
        facade_contract = self.contracts['facade']

        # Build transaction
        function_call = facade_contract.functions.submitRequestHash(
            tx_data.params['commuter_id'],
            tx_data.params['content_hash']
        )

        return self._send_transaction(function_call, api_account)

    def _execute_offer_transaction(self, tx_data, api_account):
        """Execute an offer submission transaction"""
        facade_contract = self.contracts['facade']

        # Build transaction
        function_call = facade_contract.functions.submitOfferHash(
            tx_data.params['request_id'],
            tx_data.params['provider_id'],
            tx_data.params['offer_hash']
        )

        # Send transaction and get receipt
        tx_hash = self._send_transaction(function_call, api_account)

        # Get the blockchain offer ID from the transaction receipt
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            # Parse OfferSubmitted event to get the blockchain offer ID
            auction_contract = self.contracts['auction']
            offer_submitted_events = auction_contract.events.OfferSubmitted().processReceipt(receipt)

            if offer_submitted_events:
                blockchain_offer_id = offer_submitted_events[0]['args']['offerId']
                marketplace_offer_id = tx_data.params['offer_id']

                # Store mapping between marketplace offer ID and blockchain offer ID (thread-safe)
                with self.offer_mapping_lock:
                    self.offer_id_mapping[marketplace_offer_id] = blockchain_offer_id

                    # Also store reverse mapping for easier lookup
                    key = f"{tx_data.params['request_id']}_{tx_data.params['provider_id']}"
                    self.provider_request_mapping[key] = blockchain_offer_id

                self.logger.info(f"✅ Mapped marketplace offer {marketplace_offer_id} to blockchain offer {blockchain_offer_id}")
                self.logger.info(f"✅ Mapped provider-request {key} to blockchain offer {blockchain_offer_id}")
            else:
                self.logger.warning(f"No OfferSubmitted events found in transaction receipt")
        except Exception as e:
            self.logger.warning(f"Could not extract blockchain offer ID: {e}")
            # Try to create a fallback mapping using the transaction data
            try:
                key = f"{tx_data.params['request_id']}_{tx_data.params['provider_id']}"
                # Use a simple counter as fallback blockchain offer ID
                if not hasattr(self, '_fallback_offer_counter'):
                    self._fallback_offer_counter = 0
                self._fallback_offer_counter += 1
                self.provider_request_mapping[key] = self._fallback_offer_counter
                self.logger.info(f"Created fallback mapping for {key} -> {self._fallback_offer_counter}")
            except Exception as fallback_error:
                self.logger.error(f"Failed to create fallback mapping: {fallback_error}")

        return tx_hash

    def _execute_match_transaction(self, tx_data, api_account):
        """Execute a match recording transaction"""
        facade_contract = self.contracts['facade']

        # Get the correct blockchain offer ID
        marketplace_offer_id = tx_data.params['winning_offer_id']
        request_id = tx_data.params['request_id']
        provider_id = tx_data.params['provider_id']

        blockchain_offer_id = None

        # Try multiple methods to find the blockchain offer ID (thread-safe)
        # Method 1: Direct mapping from marketplace offer ID
        with self.offer_mapping_lock:
            if hasattr(self, 'offer_id_mapping') and marketplace_offer_id in self.offer_id_mapping:
                blockchain_offer_id = self.offer_id_mapping[marketplace_offer_id]
                self.logger.info(f"Found blockchain offer ID {blockchain_offer_id} via direct mapping")

            # Method 2: Provider-request mapping
            elif hasattr(self, 'provider_request_mapping'):
                key = f"{request_id}_{provider_id}"
            if key in self.provider_request_mapping:
                blockchain_offer_id = self.provider_request_mapping[key]
                self.logger.info(f"Found blockchain offer ID {blockchain_offer_id} via provider-request mapping")

        # Method 3: Query blockchain directly
        if blockchain_offer_id is None:
            blockchain_offer_id = self._find_blockchain_offer_id(request_id, provider_id)
            if blockchain_offer_id is not None:
                self.logger.info(f"Found blockchain offer ID {blockchain_offer_id} via blockchain query")

        # If still not found, log warning and skip this transaction gracefully
        if blockchain_offer_id is None:
            self.logger.warning(f"Skipping match recording: Could not find blockchain offer ID for marketplace offer {marketplace_offer_id}")
            self.logger.warning(f"Request: {request_id}, Provider: {provider_id}")
            # Return a dummy transaction hash to indicate the transaction was "processed" but skipped
            return "0x0000000000000000000000000000000000000000000000000000000000000000"

        # Build transaction
        function_call = facade_contract.functions.recordMatch(
            request_id,
            blockchain_offer_id,  # Use blockchain offer ID
            provider_id,
            int(tx_data.params['price'])  # Convert to wei
        )

        return self._send_transaction(function_call, api_account)

    def _find_blockchain_offer_id(self, request_id, provider_id):
        """Find the blockchain offer ID for a given request and provider"""
        try:
            auction_contract = self.contracts['auction']

            # Get all offers for this request
            offers = auction_contract.functions.getOffers(request_id).call()
            self.logger.debug(f"Found {len(offers)} offers for request {request_id}")

            # Find the offer from this provider
            for i, offer in enumerate(offers):
                # offer structure: [providerId, price, timestamp, isActive]
                if len(offer) > 0 and offer[0] == provider_id:  # offer[0] is providerId
                    self.logger.debug(f"Found matching offer at index {i} for provider {provider_id}")
                    return i

            self.logger.warning(f"No offer found for provider {provider_id} in request {request_id}")
            return None
        except Exception as e:
            self.logger.error(f"Error finding blockchain offer ID: {e}")
            return None

    def reset_offer_mappings(self):
        """Reset offer ID mappings for a new simulation (thread-safe)"""
        with self.offer_mapping_lock:
            self.offer_id_mapping.clear()
            self.provider_request_mapping.clear()
            self._fallback_offer_counter = 0
        self.logger.info("Reset offer ID mappings for new simulation")

    def _execute_completion_transaction(self, tx_data, api_account):
        """Execute a completion confirmation transaction"""
        facade_contract = self.contracts['facade']

        # Build transaction
        function_call = facade_contract.functions.confirmCompletion(
            tx_data.params['request_id']
        )

        return self._send_transaction(function_call, api_account)

    def _execute_registration_transaction(self, tx_data, api_account):
        """Execute a user/provider registration transaction"""
        facade_contract = self.contracts['facade']

        if tx_data.params.get('is_provider', False):
            # Provider registration
            function_call = facade_contract.functions.registerAsProvider(
                tx_data.params['provider_id'],
                tx_data.params['address'],
                tx_data.params['mode']
            )
        else:
            # Commuter registration
            function_call = facade_contract.functions.registerAsCommuter(
                tx_data.params['commuter_id'],
                tx_data.params['address']
            )

        return self._send_transaction(function_call, api_account)

    def _execute_nft_listing_transaction(self, tx_data, api_account):
        """
        Execute or simulate an NFT listing transaction on-chain.
        Falls back to a simulated receipt when contract interaction is unavailable.
        """
        market_contract = self.contracts.get('market')

        if market_contract:
            try:
                initial_price_param = tx_data.params.get('initialPrice')
                final_price_param = tx_data.params.get('finalPrice')
                decay_duration_param = tx_data.params.get('decayDuration', 0)

                function_call = market_contract.functions.listNFTWithDynamicPricing(
                    int(tx_data.params.get('tokenId')),
                    int(initial_price_param) if initial_price_param is not None else 0,
                    int(final_price_param) if final_price_param is not None else 0,
                    int(decay_duration_param)
                )
                return self._send_transaction(function_call, api_account)
            except Exception as e:
                self.logger.warning(f"On-chain NFT listing failed, simulating listing transaction: {e}")

        # Simulated transaction receipt for environments without an active contract
        simulated_tx_hash = f"sim_{uuid.uuid4().hex[:12]}"
        self.blockchain_stats['recent_tx_hashes'].append(simulated_tx_hash)
        if len(self.blockchain_stats['recent_tx_hashes']) > 20:
            self.blockchain_stats['recent_tx_hashes'] = self.blockchain_stats['recent_tx_hashes'][-20:]

        return {
            'status': 'simulated',
            'tx_hash': simulated_tx_hash,
            'function': tx_data.function_name,
            'params': tx_data.params
        }

    def _get_next_nonce(self, address):
        """Get the next nonce for an account with proper synchronization"""
        with self.nonce_lock:
            # Initialize nonce tracker if not exists
            if address not in self.nonce_tracker:
                self.nonce_tracker[address] = self.w3.eth.get_transaction_count(address)

            # Get current nonce and increment for next transaction
            current_nonce = self.nonce_tracker[address]
            self.nonce_tracker[address] += 1

            return current_nonce

    def _reset_nonce_tracker(self, address=None):
        """
        Reset cached nonces after a nonce-related failure.
        If an address is provided, only reset that address; otherwise reset all tracked accounts.
        """
        with self.nonce_lock:
            if address:
                try:
                    fresh_nonce = self.w3.eth.get_transaction_count(address)
                    self.nonce_tracker[address] = fresh_nonce
                    self.tx_nonce_map[address] = fresh_nonce
                except Exception as e:
                    self.logger.error(f"Failed to reset nonce for {address}: {e}")
                return

            for tracked_address in list(self.nonce_tracker.keys()):
                try:
                    fresh_nonce = self.w3.eth.get_transaction_count(tracked_address)
                    self.nonce_tracker[tracked_address] = fresh_nonce
                    self.tx_nonce_map[tracked_address] = fresh_nonce
                except Exception as e:
                    self.logger.error(f"Failed to reset nonce for {tracked_address}: {e}")

    def _send_transaction(self, function_call, account):
        """Send a transaction to the blockchain and wait for confirmation"""
        try:
            # Add small delay to encourage proper blockchain communication
            time.sleep(0.05)  # 50ms delay between transactions

            # Atomically: get nonce -> build -> sign -> send
            with self.nonce_lock:
                nonce = self._get_next_nonce(account.address)

                transaction = function_call.build_transaction({
                    'from': account.address,
                    'nonce': nonce,
                    'gas': self.gas_limit,
                    'gasPrice': self.w3.eth.gas_price,
                    'chainId': self.w3.eth.chain_id
                })

                signed_txn = account.sign_transaction(transaction)

                # web3 v7 uses raw_transaction, older versions exposed rawTransaction
                raw_tx = getattr(signed_txn, "raw_transaction", None) or getattr(signed_txn, "rawTransaction", None)
                tx_hash = self.w3.eth.send_raw_transaction(raw_tx)

            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)

            if receipt.status == 1:
                self.logger.info(f"✅ Transaction confirmed: {tx_hash.hex()} (nonce: {nonce})")

                # Track successful transaction hash
                self.blockchain_stats['recent_tx_hashes'].append(tx_hash.hex())
                if len(self.blockchain_stats['recent_tx_hashes']) > 20:  # Keep only last 20
                    self.blockchain_stats['recent_tx_hashes'] = self.blockchain_stats['recent_tx_hashes'][-20:]

                return receipt
            else:
                # If transaction failed, we need to reset the nonce tracker
                with self.nonce_lock:
                    self.nonce_tracker[account.address] = self.w3.eth.get_transaction_count(account.address)
                raise Exception(f"Transaction failed: {tx_hash.hex()}")

        except Exception as e:
            # If transaction failed due to nonce issues, reset nonce tracker
            if "nonce" in str(e).lower() or "replacement transaction underpriced" in str(e).lower():
                with self.nonce_lock:
                    self.nonce_tracker[account.address] = self.w3.eth.get_transaction_count(account.address)
                    self.logger.warning(f"Reset nonce tracker for {account.address} due to nonce error")

            self.logger.error(f"Transaction sending failed: {str(e)}")
            raise

    def register_commuter_on_blockchain(self, commuter_id, address):
        """Register a commuter on the blockchain"""
        tx_data = TransactionData(
            tx_type="registration",
            function_name="registerAsCommuter",
            params={
                'commuter_id': commuter_id,
                'address': address,
                'is_provider': False
            },
            sender_id=commuter_id
        )

        if self.async_mode:
            self.queue_transaction(tx_data)
        else:
            self._execute_blockchain_transaction(tx_data)

    def register_provider_on_blockchain(self, provider_id, address, mode):
        """Register a provider on the blockchain"""
        tx_data = TransactionData(
            tx_type="registration",
            function_name="registerAsProvider",
            params={
                'provider_id': provider_id,
                'address': address,
                'mode': mode,
                'is_provider': True
            },
            sender_id=provider_id
        )

        if self.async_mode:
            self.queue_transaction(tx_data)
        else:
            self._execute_blockchain_transaction(tx_data)

    def store_commuter_profile(self, commuter_id, profile_data):
        """Store detailed commuter profile for booking analysis"""
        self.commuter_profiles[commuter_id] = profile_data

    def store_provider_profile(self, provider_id, profile_data):
        """Store detailed provider profile for booking analysis"""
        pid_str = str(provider_id)
        self.provider_profiles[pid_str] = profile_data
        # Keep marketplace_db in sync as a fallback
        with self.marketplace_db_lock:
            if 'providers' not in self.marketplace_db:
                self.marketplace_db['providers'] = {}
            self.marketplace_db['providers'][pid_str] = profile_data

    def store_request_details(self, request_id, request_data):
        """Store detailed request information for booking analysis"""
        self.request_details[request_id] = request_data

    def store_offer_details(self, offer_id, offer_data):
        """Store detailed offer information for booking analysis"""
        self.offer_details[offer_id] = offer_data

    def store_match_details(self, match_id, match_data):
        """Store detailed match/booking information for analysis"""
        # Avoid duplicate booking records for the same match/request
        if match_id in self.match_details:
            self.match_details[match_id].update(match_data)
        else:
            self.match_details[match_id] = match_data

        # Derive mode/provider_type for downstream analytics
        provider_id = match_data.get('provider_id')
        offer_id = match_data.get('offer_id')
        offer_details = self.offer_details.get(offer_id, {})
        pid_str = str(provider_id) if provider_id is not None else None
        provider_profile = self.provider_profiles.get(pid_str, {})
        if not provider_profile:
            # Try alternate type and marketplace_db
            with self.marketplace_db_lock:
                provider_profile = self.marketplace_db.get('providers', {}).get(pid_str, {})
            if not provider_profile:
                try:
                    provider_profile = self.provider_profiles.get(int(provider_id)) or self.provider_profiles.get(str(provider_id), {})
                except Exception:
                    provider_profile = {}
        source = 'bundle' if match_data.get('bundle') else match_data.get('source', 'direct')
        mode = (
            match_data.get('mode')
            or offer_details.get('mode')
            or provider_profile.get('mode_type')
            or 'unknown'
        )
        # Heuristic fallback based on provider name if still unknown
        if mode == 'unknown' and provider_profile:
            name = str(provider_profile.get('provider_name', '')).lower()
            if 'bus' in name:
                mode = 'bus'
            elif 'train' in name:
                mode = 'train'
            elif 'uber' in name or 'taxi' in name or 'car' in name:
                mode = 'car'
            elif 'bike' in name:
                mode = 'bike'

        # Create comprehensive booking record
        booking_record = {
            'booking_id': match_id,
            'timestamp': time.time(),
            'commuter_id': match_data.get('commuter_id'),
            'provider_id': match_data.get('provider_id'),
            'provider_type': mode,
            'source': source,
            'request_id': match_data.get('request_id'),
            'offer_id': match_data.get('offer_id'),
            'price': match_data.get('price'),
            'origin': match_data.get('origin'),
            'destination': match_data.get('destination'),
            'route_details': match_data.get('route_details'),
            'commuter_profile': self.commuter_profiles.get(match_data.get('commuter_id'), {}),
            'provider_profile': self.provider_profiles.get(match_data.get('provider_id'), {}),
            'request_details': self.request_details.get(match_data.get('request_id'), {}),
            'offer_details': offer_details
        }
        if match_id not in self._booking_ids:
            self.booking_details.append(booking_record)
            self._booking_ids.add(match_id)

    # ================ QUERY FUNCTIONS ================
    
    def get_marketplace_requests(self, status='active'):
        """Get requests from marketplace DB"""
        return [r for r in self.marketplace_db['requests'].values() if r['status'] == status]

    def check_request_status(self, request_id):
        """
        Lightweight status lookup for a request stored in the off-chain marketplace DB.
        Returns a status string such as 'matched', 'active', or 'unknown'.
        """
        with self.marketplace_db_lock:
            req = self.marketplace_db.get('requests', {}).get(request_id)
            if not req:
                return "unknown"
            if request_id in self.marketplace_db.get('matches', {}):
                return "matched"
            return req.get('status', 'unknown')
    
    def get_provider_notifications(self, provider_id):
        """Get notifications for a provider"""
        return self.marketplace_db['notifications'].get(provider_id, [])
    
    def get_request_offers(self, request_id):
        """Get all offers for a request"""
        return [o for o in self.marketplace_db['offers'].values() if o.get('request_id') == request_id]
    
    # ================ REMOVE/DEPRECATE THESE FUNCTIONS ================
    # These are unnecessary for the simplified marketplace approach
    
    def create_nft(self, service_details, provider_id, commuter_id):
        """UNNECESSARY - Keep for backwards compatibility but log warning"""
        self.logger.warning("NFT creation called but not needed in marketplace flow")
        return False, None
    
    def create_bundle(self, bundle_segments):
        """UNNECESSARY - Too complex for MVP"""
        self.logger.warning("Bundle creation called but not needed in simplified flow")
        return False, None

    # ==================== BUNDLE ROUTING METHODS ====================

    def search_nfts(self, origin_area=None, destination_area=None, time_window=None, max_price=None):
        """
        Search for NFT-based segments on the blockchain

        This method queries the blockchain for minted NFT segments.
        Currently returns empty list as NFT contracts are not yet deployed.
        Falls back to marketplace offers instead.

        Args:
            origin_area: Optional origin area filter
            destination_area: Optional destination area filter
            time_window: Optional (start_time, end_time) tuple for filtering
            max_price: Optional maximum price filter

        Returns:
            List of NFT segment dictionaries
        """
        nft_segments = []

        try:
            # TODO: Implement actual NFT event log querying when contracts are deployed
            # For now, this is a placeholder that returns empty list
            # The bundle router will fall back to using marketplace offers

            # Future implementation would:
            # 1. Query NFT contract for Mint events
            # 2. Filter by origin_area, destination_area, time_window, max_price
            # 3. Parse event logs into segment dictionaries
            # 4. Return list of available NFT segments

            # Example structure (when implemented):
            # events = self.nft_contract.events.SegmentMinted.getLogs(fromBlock=0)
            # for event in events:
            #     segment = {
            #         'type': 'nft',
            #         'segment_id': f"nft_{event.args.tokenId}",
            #         'origin': event.args.origin,
            #         'destination': event.args.destination,
            #         'start_time': event.args.startTime,
            #         'price': event.args.price,
            #         'mode': event.args.mode,
            #         'provider_id': event.args.provider
            #     }
            #     nft_segments.append(segment)

            self.logger.debug(f"Searched for NFT segments (found {len(nft_segments)}, contracts not deployed yet)")
            return nft_segments

        except Exception as e:
            self.logger.error(f"Error searching NFTs: {e}")
            return []

    def get_bundle_router(self):
        """
        Lazy initialization of bundle router

        Returns:
            DecentralizedBundleRouter instance
        """
        if self.bundle_router is None:
            from abm.utils.bundle_router import DecentralizedBundleRouter
            self.bundle_router = DecentralizedBundleRouter(self, self.logger)
        return self.bundle_router

    def get_active_segments(self, time_window: Tuple[int, int] = None) -> List[Dict]:
        """
        Get all active segments from blockchain (NFTs and offers)

        This is a decentralized operation - reads directly from blockchain state

        Args:
            time_window: (start_tick, end_tick) for filtering

        Returns:
            List of segment dictionaries
        """
        router = self.get_bundle_router()
        return router.get_active_segments(time_window)

    def get_all_available_segments(self, time_window: Tuple[int, int] = None) -> List[Dict]:
        """
        Aggregate primary offers and secondary listings for routing.
        """
        segments = []
        with self.marketplace_db_lock:
            offers = self.marketplace_db.get('offers', {})
            listings = self.marketplace_db.get('listings', {})

            for offer in offers.values():
                if offer.get('status') not in ['available', 'submitted']:
                    continue
                origin = offer.get('origin')
                destination = offer.get('destination')
                depart_time = offer.get('depart_time', offer.get('start_time', 0))
                arrive_time = offer.get('arrive_time', depart_time + offer.get('estimated_time', 0))
                segments.append({
                    'segment_id': f"offer_{offer.get('offer_id')}",
                    'type': offer.get('type', 'offer'),
                    'offer_id': offer.get('offer_id'),
                    'provider_id': offer.get('provider_id'),
                    'mode': offer.get('mode', 'unknown'),
                    'origin': origin,
                    'destination': destination,
                    'depart_time': depart_time,
                    'arrive_time': arrive_time,
                    'price': offer.get('price', 0),
                    'capacity': offer.get('capacity', 1),
                    'status': offer.get('status', 'available')
                })

            for listing in listings.values():
                if listing.get('status') != 'active':
                    continue
                details = listing.get('details', {})
                origin = details.get('origin')
                destination = details.get('destination')
                service_time = details.get('service_time', 0)
                duration = details.get('duration', 0)
                segments.append({
                    'segment_id': f"listing_{listing.get('listing_id', listing.get('nft_id'))}",
                    'type': 'listing',
                    'nft_id': listing.get('nft_id'),
                    'provider_id': listing.get('seller_id'),
                    'mode': details.get('mode', 'unknown'),
                    'origin': origin,
                    'destination': destination,
                    'depart_time': service_time,
                    'arrive_time': service_time + duration,
                    'price': listing.get('current_price', listing.get('price', 0)),
                    'capacity': 1,
                    'status': listing.get('status', 'active')
                })
        return segments

    def broadcast_offer(self, offer):
        """
        Allow providers to broadcast offers (segments) to the off-chain database.
        Simulates a P2P gossip layer for primary (non-NFT) segments.
        """
        try:
            offer_id = offer.get('offer_id')
            if not offer_id:
                self.logger.error("Cannot broadcast offer without offer_id")
                return False

            with self.marketplace_db_lock:
                offers = self.marketplace_db.setdefault('offers', {})
                offers[offer_id] = offer
                # Log occasionally to avoid spam
                if len(offers) % 10 == 0:
                    self.logger.info(f"Broadcasted offer {offer_id} ({offer.get('mode')}). Total offers: {len(offers)}")
            return True
        except Exception as e:
            self.logger.error(f"Error broadcasting offer: {e}")
            return False

    def build_bundles(
        self,
        origin: List[float],
        destination: List[float],
        start_time: int,
        max_transfers: int = 3,
        time_tolerance: int = 5,
        segments_override: List[Dict] = None
    ) -> List[Dict]:
        """
        Build multi-modal bundle options using decentralized routing

        Each commuter independently assembles routes from available segments.
        No central coordinator - pure peer-to-peer discovery.

        Args:
            origin: Starting location [x, y]
            destination: Target location [x, y]
            start_time: Desired departure tick
            max_transfers: Maximum number of segments in bundle
            time_tolerance: Acceptable time deviation (ticks)

        Returns:
            List of bundle options sorted by utility
        """
        router = self.get_bundle_router()
        active_segments = segments_override if segments_override is not None else router.get_active_segments()

        return router.build_bundles(
            origin,
            destination,
            active_segments,
            start_time,
            max_transfers,
            time_tolerance
        )

    def mint_and_buy(self, offer_id: str, buyer_id, start_time: Optional[int] = None,
                     duration: Optional[int] = None, source_override: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        JIT minting for primary offers: check capacity, mint NFT, assign to buyer.
        """
        with self.marketplace_db_lock:
            offer = self.marketplace_db.get('offers', {}).get(offer_id)
            if not offer:
                return False, None
            if offer.get('sold_count', 0) >= offer.get('capacity', 1):
                offer['status'] = 'sold_out'
                return False, None

            offer['sold_count'] = offer.get('sold_count', 0) + 1
            if offer['sold_count'] >= offer.get('capacity', 1):
                offer['status'] = 'sold_out'

            # Derive timing for this minted ticket
            depart_val = start_time if start_time is not None else offer.get('depart_time', offer.get('start_time', 0))
            duration_val = duration if duration is not None else (
                offer.get('estimated_time') or (offer.get('arrive_time', 0) - offer.get('depart_time', offer.get('start_time', 0)))
            )
            if duration_val is None:
                duration_val = 0

            new_nft_id = f"nft_{offer_id}_{uuid.uuid4().hex[:6]}"
            nft_details = {
                'nft_id': new_nft_id,
                'owner_id': buyer_id,
                'source_offer_id': offer_id,
                'origin': offer.get('origin'),
                'destination': offer.get('destination'),
                'service_time': depart_val,
                'duration': duration_val,
                'price': offer.get('price', 0),
                'mode': offer.get('mode', 'unknown'),
                'status': 'active'
            }
            self.marketplace_db.setdefault('nfts', {})[new_nft_id] = nft_details
            current_tick = getattr(self.model, "current_step", None) if hasattr(self, "model") else None
            self._record_transaction(
                offer_id,
                buyer_id,
                offer.get('price', 0),
                "mint",
                explicit_tick=current_tick,
                source_override=source_override,
                start_time=depart_val,
                duration=duration_val,
                mode_override=offer.get('mode')
            )

        return True, new_nft_id

    def buy_secondary_nft(self, nft_id, buyer_id) -> bool:
        """
        Wrapper for secondary purchase using existing purchase_nft.
        """
        return self.purchase_nft(nft_id, buyer_id)

    def _record_transaction(self, offer_id, buyer_id, price, tx_type="mint",
                             explicit_tick=None, source_override=None,
                             start_time: Optional[int] = None, duration: Optional[int] = None,
                             mode_override: Optional[str] = None):
        """
        Record a transaction for analytics/statistics (Internal Helper)
        Fixed to include origin/destination and provider profile for proper visualization.
        """
        try:
            # 1) Simulated tx hash
            tx_hash = f"tx_{int(time.time())}_{uuid.uuid4().hex[:8]}"

            # 2) Update basic stats
            self.blockchain_stats['total_transactions'] += 1
            self.blockchain_stats['successful_transactions'] += 1
            self.blockchain_stats['recent_tx_hashes'].append(tx_hash)

            timestamp = time.time()
            match_id = f"jit_{int(timestamp)}_{offer_id}"

            # 3) Fetch offer and profiles
            offer = {}
            provider_profile = {}
            commuter_profile = self.commuter_profiles.get(buyer_id, {})

            with self.marketplace_db_lock:
                offer = self.marketplace_db.get('offers', {}).get(offer_id, {}) or {}
                if offer:
                    provider_id = offer.get('provider_id')
                    p_id_str = str(provider_id) if provider_id is not None else None
                    provider_profile = (
                        self.marketplace_db.get('providers', {}).get(p_id_str, {}) or
                        self.provider_profiles.get(p_id_str, {})
                    )
                    # Try cross-type lookup (int<->str) if still empty
                    if not provider_profile and provider_id is not None:
                        try:
                            provider_profile = (
                                self.provider_profiles.get(int(provider_id)) or
                                self.provider_profiles.get(str(provider_id), {})
                            )
                        except Exception:
                            provider_profile = {}

            # 4) Build booking record with full context
            current_tick = explicit_tick
            if current_tick is None and hasattr(self, "model") and hasattr(self.model, "current_step"):
                current_tick = self.model.current_step

            # Derive timing
            start_time = start_time or offer.get('depart_time') or offer.get('start_time') or current_tick
            if duration is None:
                arrive_time = offer.get('arrive_time')
                est_time = offer.get('estimated_time', 0)
                if arrive_time is not None and offer.get('depart_time') is not None:
                    duration = max(0, arrive_time - offer.get('depart_time'))
                else:
                    duration = est_time
            if duration is None:
                duration = 0

            # Determine mode/provider_type robustly
            allowed_sources = ['bus', 'train', 'car', 'bike']
            mode = None
            # 1) explicit override
            if mode_override:
                mode = mode_override
            # 2) source override if it is a known mode
            if mode is None and source_override in allowed_sources:
                mode = source_override
            # 3) offer/profile
            if mode is None:
                mode = offer.get('mode') or provider_profile.get('mode_type') or provider_profile.get('mode') or 'unknown'
            # 4) heuristic on provider name
            if mode == 'unknown' and provider_profile:
                name = str(provider_profile.get('company_name') or provider_profile.get('provider_name') or '').lower()
                if 'bus' in name:
                    mode = 'bus'
                elif 'train' in name:
                    mode = 'train'
                elif 'uber' in name or 'taxi' in name or 'car' in name:
                    mode = 'car'
                elif 'bike' in name:
                    mode = 'bike'

            booking_record = {
                'booking_id': match_id,
                'match_id': match_id,
                'commuter_id': buyer_id,
                'provider_id': offer.get('provider_id', 'unknown'),
                'provider_type': mode,
                'source': source_override if source_override else ('jit_mint' if tx_type == 'mint' else 'nft_market_secondary'),
                'request_id': f"req_{offer_id}",
                'offer_id': offer_id,
                'price': price,
                'timestamp': timestamp,
                'tick': current_tick,
                'start_time': start_time,
                'end_time': start_time + duration if duration is not None else start_time,
                'duration': duration,
                'status': 'completed',
                # Fix route display [] -> [] by populating origin/destination
                'origin': offer.get('origin', [0, 0]),
                'destination': offer.get('destination', [0, 0]),
                # Attach profiles for downstream summaries
                'provider_profile': provider_profile,
                'commuter_profile': commuter_profile,
                'route_details': {
                    'distance': 0,
                    'duration': offer.get('estimated_time', 0) or (offer.get('arrive_time', 0) - offer.get('depart_time', 0)),
                    'route': [offer.get('origin'), offer.get('destination')]
                }
            }

            if match_id not in self._booking_ids:
                self.booking_details.append(booking_record)
                self._booking_ids.add(match_id)

            self.logger.info(f"✅ Recorded {tx_type} transaction {tx_hash} for offer {offer_id}")
            return tx_hash

        except Exception as e:
            self.logger.error(f"Error recording transaction: {e}")
            import traceback
            traceback.print_exc()
            return None

    def mint_direct_segment_for(self, request: Dict) -> bool:
        """
        Fallback: Mint a direct segment when no bundles are available

        This triggers providers to create new NFTs for the request

        Args:
            request: Request dictionary with origin, destination, time

        Returns:
            True if segment minted successfully
        """
        try:
            # Broadcast request to all providers via marketplace
            request_id = request.get('request_id')

            # Notify all providers about this unmatched request
            with self.marketplace_db_lock:
                providers = self.marketplace_db.get('providers', {})
                for provider_id in providers.keys():
                    notification = {
                        'type': 'unmatched_request',
                        'request_id': request_id,
                        'origin': request.get('origin'),
                        'destination': request.get('destination'),
                        'start_time': request.get('start_time'),
                        'max_price': request.get('max_price')
                    }
                    self.marketplace_db['notifications'][provider_id].append(notification)

            self.logger.info(f"Broadcasted unmatched request {request_id} to providers")
            return True

        except Exception as e:
            self.logger.error(f"Error minting direct segment: {e}")
            return False

    def reserve_bundle(
        self,
        commuter_id: int,
        request_id: int,
        bundle: Dict
    ) -> Tuple[bool, Optional[str]]:
        """
        Reserve all segments in a bundle atomically

        This is the key operation that converts a bundle proposal into a confirmed reservation

        Args:
            commuter_id: Commuter agent ID
            request_id: Travel request ID
            bundle: Bundle dictionary with segments

        Returns:
            (success, reservation_id)
        """
        try:
            reservation_id = f"res_{uuid.uuid4().hex[:12]}"

            with self.marketplace_db_lock:
                # Check if all segments are still available
                segments = bundle.get('segments', [])
                for segment in segments:
                    segment_id = segment.get('segment_id')

                    # Check NFT availability
                    if segment.get('type') == 'nft':
                        # Would check NFT ownership on blockchain
                        pass

                    # Check offer availability
                    elif segment.get('type') == 'offer':
                        offer_id = segment_id.replace('offer_', '')
                        offer = self.marketplace_db['offers'].get(int(offer_id))
                        if not offer or offer.get('status') != 'submitted':
                            self.logger.warning(f"Segment {segment_id} no longer available")
                            return False, None

                # All segments available - create reservation
                reservation = {
                    'reservation_id': reservation_id,
                    'bundle_id': bundle.get('bundle_id'),
                    'commuter_id': commuter_id,
                    'request_id': request_id,
                    'segments': segments,
                    'total_price': bundle.get('total_price'),
                    'created_at': time.time(),
                    'status': 'confirmed'
                }

                # Store reservation
                if 'reservations' not in self.marketplace_db:
                    self.marketplace_db['reservations'] = {}
                self.marketplace_db['reservations'][reservation_id] = reservation

                # Mark segments as reserved
                for segment in segments:
                    if segment.get('type') == 'offer':
                        offer_id = segment.get('segment_id').replace('offer_', '')
                        if int(offer_id) in self.marketplace_db['offers']:
                            self.marketplace_db['offers'][int(offer_id)]['status'] = 'reserved'

                # Update request status
                if request_id in self.marketplace_db['requests']:
                    self.marketplace_db['requests'][request_id]['status'] = 'matched'

                # Create match record for compatibility
                match_id = len(self.marketplace_db.get('matches', {}))
                self.marketplace_db['matches'][match_id] = {
                    'match_id': match_id,
                    'request_id': request_id,
                    'commuter_id': commuter_id,
                    'bundle': bundle,
                    'reservation_id': reservation_id,
                    'timestamp': time.time()
                }

            self.logger.info(f"Reserved bundle {bundle.get('bundle_id')} as {reservation_id}")
            return True, reservation_id

        except Exception as e:
            self.logger.error(f"Error reserving bundle: {e}")
            return False, None

    def _update_transaction_stats(self, tx, success=True):
        """Update blockchain statistics for a transaction (only count successful ones)"""
        # Only count successful transactions in type-specific stats
        if success:
            self.blockchain_stats['total_transactions'] += 1

            # Track transaction types only for successful transactions
            if tx.tx_type == "registration":
                if "commuter" in tx.function_name.lower():
                    self.blockchain_stats['commuter_registrations'] += 1
                elif "provider" in tx.function_name.lower():
                    self.blockchain_stats['provider_registrations'] += 1
            elif tx.tx_type == "request":
                self.blockchain_stats['travel_requests'] += 1
            elif tx.tx_type == "offer":
                self.blockchain_stats['service_offers'] += 1
            elif tx.tx_type == "match":
                self.blockchain_stats['completed_matches'] += 1
            elif tx.tx_type == "nft_list":
                self.blockchain_stats['nft_listings'] += 1
            elif tx.tx_type == "nft_buy":
                self.blockchain_stats.setdefault('nft_sales', 0)
                self.blockchain_stats['nft_sales'] += 1

    def get_blockchain_summary(self):
        """Generate comprehensive blockchain storage summary"""
        try:
            # Calculate success rate
            total_tx = self.blockchain_stats['total_transactions']
            success_rate = (self.blockchain_stats['successful_transactions'] / total_tx * 100) if total_tx > 0 else 0

            # Calculate average transaction time
            avg_tx_time = sum(self.blockchain_stats['transaction_times']) / len(self.blockchain_stats['transaction_times']) if self.blockchain_stats['transaction_times'] else 0

            # Calculate peak TPS (simplified)
            runtime = time.time() - self.blockchain_stats['start_time']
            peak_tps = self.blockchain_stats['successful_transactions'] / runtime if runtime > 0 else 0

            # Estimate ETH spent (simplified calculation)
            avg_gas_per_tx = 50000  # Rough estimate
            gas_price_gwei = 20  # 20 gwei
            total_gas = self.blockchain_stats['successful_transactions'] * avg_gas_per_tx
            eth_spent = total_gas * gas_price_gwei / 1e9  # Convert to ETH

            # Off-chain derived stats (useful when SKIP_CHAIN_PROCESSING is enabled)
            marketplace_db = getattr(self, "marketplace_db", {})
            listings = marketplace_db.get('listings', {}) if isinstance(marketplace_db, dict) else {}
            offchain_listing_count = len([l for l in listings.values() if l.get('status') in ('active', 'sold')])
            offchain_secondary_sales = sum(
                1 for b in self.booking_details
                if b.get('source') in ['nft_market', 'secondary', 'market']
            )

            # Prefer on-chain counters but fill gaps from off-chain data
            self.blockchain_stats['nft_listings'] = max(self.blockchain_stats.get('nft_listings', 0), offchain_listing_count)
            self.blockchain_stats['completed_matches'] = max(
                self.blockchain_stats.get('completed_matches', 0),
                len(self.booking_details)
            )

            return {
                'total_transactions': total_tx,
                'successful_transactions': self.blockchain_stats['successful_transactions'],
                'failed_transactions': self.blockchain_stats['failed_transactions'],
                'success_rate': success_rate,
                'total_gas_used': total_gas,
                'eth_spent': eth_spent,
                'commuter_registrations': self.blockchain_stats['commuter_registrations'],
                'provider_registrations': self.blockchain_stats['provider_registrations'],
                'travel_requests': self.blockchain_stats['travel_requests'],
                'service_offers': self.blockchain_stats['service_offers'],
                'completed_matches': self.blockchain_stats['completed_matches'],
                'nft_listings': self.blockchain_stats.get('nft_listings', 0),
                'nft_sales': self.blockchain_stats.get('nft_sales', 0),
                'secondary_sales': offchain_secondary_sales,
                'blockchain_connected': self.w3.is_connected(),
                'avg_tx_time': avg_tx_time,
                'peak_tps': peak_tps,
                'congestion_level': 'Low' if success_rate > 80 else 'Medium' if success_rate > 60 else 'High',
                'recent_tx_hashes': self.blockchain_stats['recent_tx_hashes'][-10:],  # Last 10 transactions
                'booking_details': self.booking_details,
                'commuter_profiles': self.commuter_profiles,
                'provider_profiles': self.provider_profiles
            }
        except Exception as e:
            self.logger.error(f"Error generating blockchain summary: {e}")
            return {
                'total_transactions': self.blockchain_stats.get('total_transactions', 0),
                'successful_transactions': self.blockchain_stats.get('successful_transactions', 0),
                'failed_transactions': self.blockchain_stats.get('failed_transactions', 0),
                'success_rate': 0,
                'blockchain_connected': self.w3.is_connected()
            }
