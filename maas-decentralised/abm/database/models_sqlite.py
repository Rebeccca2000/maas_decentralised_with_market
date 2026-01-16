"""
SQLite Database Models for MaaS Bundle System
SQLAlchemy ORM models for storing simulation data with bundle support
Compatible with SQLite (no PostgreSQL required)
"""

from sqlalchemy import create_engine, Column, Integer, BigInteger, String, Float, Boolean, DateTime, JSON, ForeignKey, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os

Base = declarative_base()

# Create SQLite engine
DB_PATH = os.path.join(os.getcwd(), 'maas_bundles.db')
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
SessionLocal = sessionmaker(bind=engine)


class SimulationRun(Base):
    """Metadata for each simulation run"""
    __tablename__ = 'runs'
    
    run_id = Column(String(50), primary_key=True)
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime)
    total_steps = Column(Integer, nullable=False)
    num_commuters = Column(Integer, nullable=False)
    num_providers = Column(Integer, nullable=False)
    network_type = Column(String(50))
    blockchain_rpc = Column(String(200))
    config = Column(JSON)  # JSON instead of JSONB for SQLite
    status = Column(String(20), default='running')
    
    # Relationships - Core simulation data
    ticks = relationship("SimulationTick", back_populates="run", cascade="all, delete-orphan")
    commuters = relationship("Commuter", back_populates="run", cascade="all, delete-orphan")
    providers = relationship("Provider", back_populates="run", cascade="all, delete-orphan")
    requests = relationship("TravelRequest", back_populates="run", cascade="all, delete-orphan")
    bundles = relationship("Bundle", back_populates="run", cascade="all, delete-orphan")
    reservations = relationship("Reservation", back_populates="run", cascade="all, delete-orphan")

    # Relationships - Analytics tables
    mode_usage_metrics = relationship("ModeUsageMetrics", back_populates="run", cascade="all, delete-orphan")
    bundle_performance_metrics = relationship("BundlePerformanceMetrics", back_populates="run", cascade="all, delete-orphan")
    price_trends = relationship("PriceTrend", back_populates="run", cascade="all, delete-orphan")

    # Relationships - Blockchain tables
    blockchain_transactions = relationship("BlockchainTransaction", back_populates="run", cascade="all, delete-orphan")
    nft_tokens = relationship("NFTToken", back_populates="run", cascade="all, delete-orphan")
    nft_listings_table = relationship("NFTListing", back_populates="run", cascade="all, delete-orphan")
    smart_contract_calls = relationship("SmartContractCall", back_populates="run", cascade="all, delete-orphan")
    blockchain_events = relationship("BlockchainEvent", back_populates="run", cascade="all, delete-orphan")
    gas_metrics = relationship("GasMetrics", back_populates="run", cascade="all, delete-orphan")
    marketplace_metrics = relationship("MarketplaceMetrics", back_populates="run", cascade="all, delete-orphan")


class SimulationTick(Base):
    """Time-series data for each simulation step - Enhanced for analytics"""
    __tablename__ = 'ticks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(50), ForeignKey('runs.run_id'), nullable=False)
    tick = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Agent counts
    active_commuters = Column(Integer, default=0)
    active_providers = Column(Integer, default=0)

    # Request and matching metrics
    active_requests = Column(Integer, default=0)
    active_bids = Column(Integer, default=0)
    completed_matches = Column(Integer, default=0)
    pending_requests = Column(Integer, default=0)

    # Bundle metrics
    bundles_created = Column(Integer, default=0)
    bundles_reserved = Column(Integer, default=0)
    active_bundles = Column(Integer, default=0)

    # Transaction metrics
    total_transactions = Column(Integer, default=0)
    active_nft_listings = Column(Integer, default=0)
    completed_trips = Column(Integer, default=0)

    # Financial metrics
    average_nft_price = Column(Float, default=0.0)
    total_revenue = Column(Float, default=0.0)
    average_trip_price = Column(Float, default=0.0)

    # Performance metrics
    average_wait_time = Column(Float, default=0.0)
    average_trip_duration = Column(Float, default=0.0)
    execution_time = Column(Float, default=0.0)

    # Mode distribution (JSON for flexibility)
    mode_distribution = Column(JSON)  # {"car": 10, "bike": 5, "bus": 3}

    run = relationship("SimulationRun", back_populates="ticks")


class Commuter(Base):
    """Individual commuter agent data"""
    __tablename__ = 'commuters'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(50), ForeignKey('runs.run_id'), nullable=False)
    agent_id = Column(String(50), nullable=False)
    wallet_address = Column(String(100))
    total_requests = Column(Integer, default=0)
    successful_trips = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    avg_wait_time = Column(Float)
    income_level = Column(String(20), default="unknown")
    
    run = relationship("SimulationRun", back_populates="commuters")


class Provider(Base):
    """Individual provider agent data"""
    __tablename__ = 'providers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(50), ForeignKey('runs.run_id'), nullable=False)
    agent_id = Column(String(50), nullable=False)
    wallet_address = Column(String(100))
    mode = Column(String(20))
    total_offers = Column(Integer, default=0)
    successful_matches = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    avg_price = Column(Float)
    utilization_rate = Column(Float)

    run = relationship("SimulationRun", back_populates="providers")
    segments = relationship("BundleSegment", back_populates="provider")


class TravelRequest(Base):
    """Travel request data"""
    __tablename__ = 'requests'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(50), ForeignKey('runs.run_id'), nullable=False)
    request_id = Column(String(50), nullable=False)
    commuter_id = Column(String(50), nullable=False)
    origin_x = Column(Float, nullable=False)
    origin_y = Column(Float, nullable=False)
    dest_x = Column(Float, nullable=False)
    dest_y = Column(Float, nullable=False)
    created_at_tick = Column(Integer, nullable=False)
    matched = Column(Boolean, default=False)
    matched_at_tick = Column(Integer)
    final_price = Column(Float)
    num_bids_received = Column(Integer, default=0)
    
    run = relationship("SimulationRun", back_populates="requests")


class Bundle(Base):
    """Multi-modal journey bundle"""
    __tablename__ = 'bundles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(50), ForeignKey('runs.run_id'), nullable=False)
    bundle_id = Column(String(50), nullable=False, unique=True)
    origin_x = Column(Float, nullable=False)
    origin_y = Column(Float, nullable=False)
    dest_x = Column(Float, nullable=False)
    dest_y = Column(Float, nullable=False)
    base_price = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0.0)
    final_price = Column(Float, nullable=False)
    num_segments = Column(Integer, nullable=False)
    total_duration = Column(Integer)
    description = Column(String(500))  # Human-readable bundle description
    created_at = Column(DateTime, default=datetime.utcnow)
    created_at_tick = Column(Integer)

    run = relationship("SimulationRun", back_populates="bundles")
    segments = relationship("BundleSegment", back_populates="bundle", cascade="all, delete-orphan")
    reservations = relationship("Reservation", back_populates="bundle", cascade="all, delete-orphan")


class BundleSegment(Base):
    """Individual segment within a bundle"""
    __tablename__ = 'bundle_segments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bundle_id = Column(String(50), ForeignKey('bundles.bundle_id'), nullable=False)
    segment_id = Column(String(50), nullable=False)
    sequence = Column(Integer, nullable=False)  # Order in journey (1, 2, 3...)
    provider_id = Column(Integer, ForeignKey('providers.id'), nullable=False)
    mode = Column(String(20), nullable=False)
    origin = Column(JSON, nullable=False)  # SQLite uses JSON instead of ARRAY
    destination = Column(JSON, nullable=False)  # SQLite uses JSON instead of ARRAY
    depart_time = Column(Integer, nullable=False)
    arrive_time = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    distance = Column(Float)
    nft_token_id = Column(String(100))  # If tokenized as NFT
    blockchain_tx_hash = Column(String(66))  # Minting/reservation tx
    status = Column(String(20), default='available')  # available, reserved, consumed, expired

    bundle = relationship("Bundle", back_populates="segments")
    provider = relationship("Provider", back_populates="segments")


class Reservation(Base):
    """Bundle reservation/purchase record"""
    __tablename__ = 'reservations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(50), ForeignKey('runs.run_id'), nullable=False)
    bundle_id = Column(String(50), ForeignKey('bundles.bundle_id'), nullable=False)
    commuter_id = Column(String(50), nullable=False)
    reserved_at = Column(DateTime, default=datetime.utcnow)
    reserved_at_tick = Column(Integer)
    transaction_hash = Column(String(100))
    status = Column(String(20), default='reserved')
    
    run = relationship("SimulationRun", back_populates="reservations")
    bundle = relationship("Bundle", back_populates="reservations")
    segment_reservations = relationship("SegmentReservation", back_populates="reservation", cascade="all, delete-orphan")


class SegmentReservation(Base):
    """Individual segment reservation within a bundle reservation"""
    __tablename__ = 'segment_reservations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    reservation_id = Column(Integer, ForeignKey('reservations.id'), nullable=False)
    segment_id = Column(Integer, ForeignKey('bundle_segments.id'), nullable=False)
    nft_token_id = Column(String(100))
    transaction_hash = Column(String(100))

    reservation = relationship("Reservation", back_populates="segment_reservations")


class ModeUsageMetrics(Base):
    """Transport mode usage statistics per simulation run"""
    __tablename__ = 'mode_usage_metrics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(50), ForeignKey('runs.run_id'), nullable=False)
    mode = Column(String(20), nullable=False)  # car, bike, bus, train, etc.

    # Usage statistics
    total_trips = Column(Integer, default=0)
    total_segments = Column(Integer, default=0)  # For bundles
    total_revenue = Column(Float, default=0.0)
    total_distance = Column(Float, default=0.0)

    # Performance metrics
    average_price = Column(Float, default=0.0)
    average_duration = Column(Float, default=0.0)
    average_wait_time = Column(Float, default=0.0)
    utilization_rate = Column(Float, default=0.0)  # % of capacity used

    # Demand metrics
    peak_demand_tick = Column(Integer)
    peak_demand_count = Column(Integer, default=0)

    # Index for faster queries
    __table_args__ = (Index('idx_mode_usage_run_mode', 'run_id', 'mode'),)

    # Relationship
    run = relationship("SimulationRun", back_populates="mode_usage_metrics")


class BundlePerformanceMetrics(Base):
    """Bundle system performance metrics per simulation run"""
    __tablename__ = 'bundle_performance_metrics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(50), ForeignKey('runs.run_id'), nullable=False, unique=True)

    # Bundle creation metrics
    total_bundles_created = Column(Integer, default=0)
    total_bundles_reserved = Column(Integer, default=0)
    bundle_reservation_rate = Column(Float, default=0.0)  # % of bundles reserved

    # Segment metrics
    total_segments_created = Column(Integer, default=0)
    average_segments_per_bundle = Column(Float, default=0.0)
    max_segments_in_bundle = Column(Integer, default=0)

    # Financial metrics
    total_bundle_revenue = Column(Float, default=0.0)
    total_discount_given = Column(Float, default=0.0)
    average_bundle_price = Column(Float, default=0.0)
    average_discount_percentage = Column(Float, default=0.0)

    # Efficiency metrics
    multi_modal_adoption_rate = Column(Float, default=0.0)  # % of trips using bundles
    average_bundle_creation_time = Column(Float, default=0.0)
    bundle_routing_success_rate = Column(Float, default=0.0)

    # Popular combinations (JSON)
    popular_mode_combinations = Column(JSON)  # [{"modes": ["bike", "train"], "count": 5}]

    # Time distribution
    peak_bundle_creation_tick = Column(Integer)
    peak_bundle_count = Column(Integer, default=0)

    # Relationship
    run = relationship("SimulationRun", back_populates="bundle_performance_metrics")


class PriceTrend(Base):
    """Price trends over time for different transport modes"""
    __tablename__ = 'price_trends'

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(50), ForeignKey('runs.run_id'), nullable=False)
    tick = Column(Integer, nullable=False)
    mode = Column(String(20), nullable=False)

    # Price metrics
    average_price = Column(Float, nullable=False)
    min_price = Column(Float, nullable=False)
    max_price = Column(Float, nullable=False)
    median_price = Column(Float)

    # Market metrics
    supply_count = Column(Integer, default=0)  # Available offers
    demand_count = Column(Integer, default=0)  # Active requests
    transaction_count = Column(Integer, default=0)  # Completed in this tick

    # Index for time-series queries
    __table_args__ = (Index('idx_price_trend_run_tick_mode', 'run_id', 'tick', 'mode'),)

    # Relationship
    run = relationship("SimulationRun", back_populates="price_trends")


# ============================================================================
# BLOCKCHAIN-RELATED TABLES
# ============================================================================

class BlockchainTransaction(Base):
    """Record of all blockchain transactions"""
    __tablename__ = 'blockchain_transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(50), ForeignKey('runs.run_id'), nullable=False)
    tx_hash = Column(String(100), nullable=False, unique=True)
    tx_type = Column(String(50), nullable=False)  # registration, request, offer, match, nft_mint, nft_list, nft_purchase
    function_name = Column(String(100), nullable=False)

    # Transaction details
    sender_address = Column(String(100))
    sender_id = Column(String(50))  # Agent ID (commuter/provider)
    block_number = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    tick = Column(Integer)  # Simulation tick when transaction was created

    # Gas and fees
    gas_price = Column(BigInteger)  # in wei
    gas_limit = Column(Integer)
    gas_used = Column(Integer)
    transaction_fee = Column(BigInteger)  # gas_used * gas_price

    # Transaction state
    status = Column(String(20))  # pending, confirmed, failed
    confirmation_time = Column(Float)  # Time to confirm (seconds)
    retry_count = Column(Integer, default=0)
    error_message = Column(String(500))

    # Transaction data (JSON)
    params = Column(JSON)  # Function parameters
    result = Column(JSON)  # Transaction result/receipt

    run = relationship("SimulationRun", back_populates="blockchain_transactions")


class NFTToken(Base):
    """NFT tokens minted for service segments"""
    __tablename__ = 'nft_tokens'

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(50), ForeignKey('runs.run_id'), nullable=False)
    token_id = Column(String(100), nullable=False)
    contract_address = Column(String(100))

    # NFT metadata
    owner_id = Column(String(50))  # Current owner (agent ID)
    original_minter_id = Column(String(50))  # Original creator
    service_type = Column(String(50))  # Transport mode

    # Service details
    origin_x = Column(Float)
    origin_y = Column(Float)
    dest_x = Column(Float)
    dest_y = Column(Float)
    start_time = Column(Integer)
    end_time = Column(Integer)
    duration = Column(Integer)
    distance = Column(Float)

    # Pricing
    base_price = Column(Float)
    current_price = Column(Float)

    # Status
    status = Column(String(20))  # minted, listed, sold, expired, burned
    minted_at = Column(DateTime, default=datetime.utcnow)
    minted_at_tick = Column(Integer)
    listed_at = Column(DateTime)
    sold_at = Column(DateTime)

    # Blockchain reference
    mint_tx_hash = Column(String(100), ForeignKey('blockchain_transactions.tx_hash'))

    run = relationship("SimulationRun", back_populates="nft_tokens")


class NFTListing(Base):
    """NFT marketplace listings"""
    __tablename__ = 'nft_listings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(50), ForeignKey('runs.run_id'), nullable=False)
    listing_id = Column(String(100), nullable=False, unique=True)
    token_id = Column(String(100), nullable=False)

    # Seller information
    seller_id = Column(String(50), nullable=False)
    seller_address = Column(String(100))

    # Pricing
    initial_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    min_price = Column(Float)
    final_price = Column(Float)

    # Dynamic pricing
    dynamic_pricing = Column(Boolean, default=False)
    decay_rate = Column(Float)
    price_decay_start = Column(DateTime)
    price_decay_end = Column(DateTime)

    # Listing status
    status = Column(String(20))  # active, sold, cancelled, expired
    listed_at = Column(DateTime, default=datetime.utcnow)
    listed_at_tick = Column(Integer)
    sold_at = Column(DateTime)
    cancelled_at = Column(DateTime)

    # Sale information
    buyer_id = Column(String(50))
    buyer_address = Column(String(100))
    sale_price = Column(Float)

    # Blockchain reference
    list_tx_hash = Column(String(100), ForeignKey('blockchain_transactions.tx_hash'))
    sale_tx_hash = Column(String(100), ForeignKey('blockchain_transactions.tx_hash'))

    run = relationship("SimulationRun", back_populates="nft_listings_table")


class SmartContractCall(Base):
    """Smart contract function calls"""
    __tablename__ = 'smart_contract_calls'

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(50), ForeignKey('runs.run_id'), nullable=False)
    tx_hash = Column(String(100), ForeignKey('blockchain_transactions.tx_hash'))

    # Contract details
    contract_name = Column(String(100), nullable=False)  # MaaSPlatform, MaaSNFT, MaaSMarket
    contract_address = Column(String(100))
    function_name = Column(String(100), nullable=False)

    # Call details
    caller_id = Column(String(50))
    caller_address = Column(String(100))
    call_data = Column(JSON)  # Function parameters
    return_data = Column(JSON)  # Function return values

    # Execution
    timestamp = Column(DateTime, default=datetime.utcnow)
    tick = Column(Integer)
    execution_time = Column(Float)  # Execution time in seconds
    success = Column(Boolean, default=True)
    error_message = Column(String(500))

    # Events emitted
    events_emitted = Column(JSON)  # List of events emitted by this call

    run = relationship("SimulationRun", back_populates="smart_contract_calls")


class BlockchainEvent(Base):
    """Blockchain events emitted by smart contracts"""
    __tablename__ = 'blockchain_events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(50), ForeignKey('runs.run_id'), nullable=False)
    tx_hash = Column(String(100), ForeignKey('blockchain_transactions.tx_hash'))

    # Event details
    event_name = Column(String(100), nullable=False)
    contract_name = Column(String(100))
    contract_address = Column(String(100))

    # Event data
    event_data = Column(JSON)  # Event parameters
    indexed_params = Column(JSON)  # Indexed parameters for filtering

    # Block information
    block_number = Column(Integer)
    block_timestamp = Column(DateTime)
    log_index = Column(Integer)

    # Simulation context
    tick = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

    run = relationship("SimulationRun", back_populates="blockchain_events")


class GasMetrics(Base):
    """Gas usage metrics per simulation tick"""
    __tablename__ = 'gas_metrics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(50), ForeignKey('runs.run_id'), nullable=False)
    tick = Column(Integer, nullable=False)

    # Gas statistics
    total_gas_used = Column(BigInteger, default=0)
    total_gas_cost = Column(BigInteger, default=0)  # in wei
    average_gas_price = Column(BigInteger, default=0)
    min_gas_price = Column(BigInteger, default=0)
    max_gas_price = Column(BigInteger, default=0)

    # Transaction counts
    total_transactions = Column(Integer, default=0)
    successful_transactions = Column(Integer, default=0)
    failed_transactions = Column(Integer, default=0)
    pending_transactions = Column(Integer, default=0)

    # Transaction types
    registration_txs = Column(Integer, default=0)
    request_txs = Column(Integer, default=0)
    offer_txs = Column(Integer, default=0)
    match_txs = Column(Integer, default=0)
    nft_mint_txs = Column(Integer, default=0)
    nft_list_txs = Column(Integer, default=0)
    nft_purchase_txs = Column(Integer, default=0)

    # Performance metrics
    average_confirmation_time = Column(Float, default=0.0)
    min_confirmation_time = Column(Float, default=0.0)
    max_confirmation_time = Column(Float, default=0.0)

    timestamp = Column(DateTime, default=datetime.utcnow)

    run = relationship("SimulationRun", back_populates="gas_metrics")


class MarketplaceMetrics(Base):
    """NFT marketplace metrics per simulation tick"""
    __tablename__ = 'marketplace_metrics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(50), ForeignKey('runs.run_id'), nullable=False)
    tick = Column(Integer, nullable=False)

    # Listing metrics
    total_listings = Column(Integer, default=0)
    active_listings = Column(Integer, default=0)
    sold_listings = Column(Integer, default=0)
    expired_listings = Column(Integer, default=0)
    cancelled_listings = Column(Integer, default=0)

    # NFT metrics
    total_nfts_minted = Column(Integer, default=0)
    total_nfts_sold = Column(Integer, default=0)
    total_nfts_burned = Column(Integer, default=0)

    # Trading volume
    total_volume = Column(Float, default=0.0)  # Total trading volume
    average_sale_price = Column(Float, default=0.0)
    min_sale_price = Column(Float, default=0.0)
    max_sale_price = Column(Float, default=0.0)

    # Price dynamics
    average_listing_price = Column(Float, default=0.0)
    average_price_change = Column(Float, default=0.0)  # Average price change due to dynamic pricing
    total_discount_given = Column(Float, default=0.0)

    # Market activity
    unique_sellers = Column(Integer, default=0)
    unique_buyers = Column(Integer, default=0)
    transactions_count = Column(Integer, default=0)

    # Liquidity metrics
    listing_to_sale_ratio = Column(Float, default=0.0)  # Percentage of listings that sold
    average_time_to_sale = Column(Float, default=0.0)  # Average time from listing to sale

    timestamp = Column(DateTime, default=datetime.utcnow)

    run = relationship("SimulationRun", back_populates="marketplace_metrics")
