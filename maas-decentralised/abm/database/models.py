"""
PostgreSQL Database Models for MaaS Bundle System
SQLAlchemy ORM models for storing simulation data with bundle support
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from datetime import datetime
import os

Base = declarative_base()


class SimulationRun(Base):
    """Metadata for each simulation run"""
    __tablename__ = 'runs'
    
    run_id = Column(String(50), primary_key=True)
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime)
    total_steps = Column(Integer, nullable=False)
    num_commuters = Column(Integer, nullable=False)
    num_providers = Column(Integer, nullable=False)
    network_type = Column(String(50))  # 'localhost', 'optimism-sepolia', etc.
    blockchain_rpc = Column(String(200))
    config = Column(JSONB)  # Full simulation configuration
    status = Column(String(20), default='running')  # running, completed, failed
    
    # Relationships
    ticks = relationship("SimulationTick", back_populates="run", cascade="all, delete-orphan")
    commuters = relationship("Commuter", back_populates="run", cascade="all, delete-orphan")
    providers = relationship("Provider", back_populates="run", cascade="all, delete-orphan")
    requests = relationship("TravelRequest", back_populates="run", cascade="all, delete-orphan")
    bundles = relationship("Bundle", back_populates="run", cascade="all, delete-orphan")
    reservations = relationship("Reservation", back_populates="run", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_run_start_time', 'start_time'),
        Index('idx_run_status', 'status'),
    )


class SimulationTick(Base):
    """Time-series data for each simulation step"""
    __tablename__ = 'ticks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(50), ForeignKey('runs.run_id'), nullable=False)
    tick = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    active_commuters = Column(Integer, default=0)
    active_providers = Column(Integer, default=0)
    active_requests = Column(Integer, default=0)
    active_bundles = Column(Integer, default=0)
    completed_reservations = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    avg_bundle_size = Column(Float, default=0.0)  # Average segments per bundle
    
    run = relationship("SimulationRun", back_populates="ticks")
    
    __table_args__ = (
        Index('idx_tick_run_tick', 'run_id', 'tick'),
    )


class Commuter(Base):
    """Commuter agent demographics and preferences"""
    __tablename__ = 'commuters'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(50), ForeignKey('runs.run_id'), nullable=False)
    commuter_id = Column(Integer, nullable=False)
    blockchain_address = Column(String(42))
    origin_area = Column(ARRAY(Float))  # [x, y]
    destination_area = Column(ARRAY(Float))  # [x, y]
    preferences = Column(JSONB)  # price_weight, time_weight, mode_preferences
    budget = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    run = relationship("SimulationRun", back_populates="commuters")
    requests = relationship("TravelRequest", back_populates="commuter")
    reservations = relationship("Reservation", back_populates="commuter")
    
    __table_args__ = (
        Index('idx_commuter_run_id', 'run_id', 'commuter_id'),
    )


class Provider(Base):
    """Provider agent capacity and pricing"""
    __tablename__ = 'providers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(50), ForeignKey('runs.run_id'), nullable=False)
    provider_id = Column(Integer, nullable=False)
    blockchain_address = Column(String(42))
    mode = Column(String(20))  # 'car', 'bike', 'bus', 'train'
    capacity = Column(Integer)
    base_price = Column(Float)
    pricing_strategy = Column(String(30))  # 'fixed', 'dynamic', 'auction'
    service_area = Column(JSONB)  # Geographic coverage
    created_at = Column(DateTime, default=datetime.utcnow)
    
    run = relationship("SimulationRun", back_populates="providers")
    segments = relationship("BundleSegment", back_populates="provider")
    
    __table_args__ = (
        Index('idx_provider_run_mode', 'run_id', 'mode'),
    )


class TravelRequest(Base):
    """Travel requests from commuters"""
    __tablename__ = 'requests'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(50), ForeignKey('runs.run_id'), nullable=False)
    request_id = Column(Integer, nullable=False)
    commuter_id = Column(Integer, ForeignKey('commuters.id'), nullable=False)
    origin = Column(ARRAY(Float), nullable=False)  # [x, y]
    destination = Column(ARRAY(Float), nullable=False)  # [x, y]
    start_time = Column(Integer, nullable=False)  # Simulation tick
    time_window = Column(Integer)  # Flexibility in ticks
    max_price = Column(Float)
    preferences = Column(JSONB)  # mode preferences, comfort level, etc.
    status = Column(String(20), default='active')  # active, matched, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    blockchain_tx_hash = Column(String(66))  # On-chain request hash
    
    run = relationship("SimulationRun", back_populates="requests")
    commuter = relationship("Commuter", back_populates="requests")
    bundles = relationship("Bundle", back_populates="request")
    
    __table_args__ = (
        Index('idx_request_run_status', 'run_id', 'status'),
        Index('idx_request_commuter', 'commuter_id'),
    )


class Bundle(Base):
    """Multi-modal journey bundles"""
    __tablename__ = 'bundles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(50), ForeignKey('runs.run_id'), nullable=False)
    bundle_id = Column(String(50), nullable=False, unique=True)
    request_id = Column(Integer, ForeignKey('requests.id'), nullable=False)
    expected_depart_time = Column(Integer)  # Simulation tick
    expected_arrive_time = Column(Integer)  # Simulation tick
    total_price = Column(Float, nullable=False)
    total_distance = Column(Float)
    total_duration = Column(Integer)  # In ticks
    num_segments = Column(Integer, default=0)
    bundle_discount = Column(Float, default=0.0)  # Discount for multi-modal
    utility_score = Column(Float)  # Commuter utility
    description = Column(String(500))  # Human-readable bundle description
    status = Column(String(20), default='proposed')  # proposed, reserved, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    reserved_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    run = relationship("SimulationRun", back_populates="bundles")
    request = relationship("TravelRequest", back_populates="bundles")
    segments = relationship("BundleSegment", back_populates="bundle", cascade="all, delete-orphan")
    reservation = relationship("Reservation", back_populates="bundle", uselist=False)
    
    __table_args__ = (
        Index('idx_bundle_run_status', 'run_id', 'status'),
        Index('idx_bundle_request', 'request_id'),
    )


class BundleSegment(Base):
    """Individual legs/segments within a bundle"""
    __tablename__ = 'bundle_segments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    bundle_id = Column(String(50), ForeignKey('bundles.bundle_id'), nullable=False)
    segment_id = Column(String(50), nullable=False)
    sequence = Column(Integer, nullable=False)  # Order in journey (1, 2, 3...)
    provider_id = Column(Integer, ForeignKey('providers.id'), nullable=False)
    mode = Column(String(20), nullable=False)
    origin = Column(ARRAY(Float), nullable=False)
    destination = Column(ARRAY(Float), nullable=False)
    depart_time = Column(Integer, nullable=False)
    arrive_time = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    distance = Column(Float)
    nft_token_id = Column(String(100))  # If tokenized as NFT
    blockchain_tx_hash = Column(String(66))  # Minting/reservation tx
    status = Column(String(20), default='available')  # available, reserved, consumed, expired
    
    bundle = relationship("Bundle", back_populates="segments")
    provider = relationship("Provider", back_populates="segments")
    segment_reservations = relationship("SegmentReservation", back_populates="segment")
    
    __table_args__ = (
        Index('idx_segment_bundle_seq', 'bundle_id', 'sequence'),
        Index('idx_segment_provider', 'provider_id'),
        Index('idx_segment_status', 'status'),
    )


class Reservation(Base):
    """Confirmed bookings/reservations"""
    __tablename__ = 'reservations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(50), ForeignKey('runs.run_id'), nullable=False)
    reservation_id = Column(String(50), nullable=False, unique=True)
    bundle_id = Column(String(50), ForeignKey('bundles.bundle_id'), nullable=False)
    commuter_id = Column(Integer, ForeignKey('commuters.id'), nullable=False)
    request_id = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    cleared_price = Column(Float)  # Final price after auction/negotiation
    lead_time = Column(Integer)  # Ticks between request and reservation
    created_tick = Column(Integer, nullable=False)
    confirmed_at = Column(DateTime, default=datetime.utcnow)
    blockchain_tx_hash = Column(String(66))
    payment_status = Column(String(20), default='pending')  # pending, paid, refunded
    
    run = relationship("SimulationRun", back_populates="reservations")
    bundle = relationship("Bundle", back_populates="reservation")
    commuter = relationship("Commuter", back_populates="reservations")
    segment_reservations = relationship("SegmentReservation", back_populates="reservation", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_reservation_run', 'run_id'),
        Index('idx_reservation_commuter', 'commuter_id'),
    )


class SegmentReservation(Base):
    """Link between reservations and consumed segments"""
    __tablename__ = 'segment_reservations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    reservation_id = Column(String(50), ForeignKey('reservations.reservation_id'), nullable=False)
    segment_id = Column(String(50), ForeignKey('bundle_segments.segment_id'), nullable=False)
    seats_consumed = Column(Integer, default=1)
    actual_price = Column(Float)  # May differ from segment price due to discounts
    
    reservation = relationship("Reservation", back_populates="segment_reservations")
    segment = relationship("BundleSegment", back_populates="segment_reservations")
    
    __table_args__ = (
        Index('idx_seg_res_reservation', 'reservation_id'),
        Index('idx_seg_res_segment', 'segment_id'),
    )


# Database connection and session management
class DatabaseManager:
    """Manages PostgreSQL database connections and operations"""
    
    def __init__(self, connection_string=None):
        """
        Initialize database manager
        
        Args:
            connection_string: PostgreSQL connection string
                             Format: postgresql://user:password@host:port/database
        """
        if connection_string is None:
            # Default to environment variable or local PostgreSQL
            connection_string = os.getenv(
                'DATABASE_URL',
                'postgresql://maas_user:maas_password@localhost:5432/maas_simulation'
            )
        
        self.engine = create_engine(connection_string, echo=False)
        self.Session = sessionmaker(bind=self.engine)
    
    def create_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(self.engine)
    
    def drop_tables(self):
        """Drop all tables (use with caution!)"""
        Base.metadata.drop_all(self.engine)
    
    def get_session(self):
        """Get a new database session"""
        return self.Session()
    
    def reset_database(self):
        """Drop and recreate all tables"""
        self.drop_tables()
        self.create_tables()

