# MaaS Bundle System Documentation

## Overview

This document describes the **Mobility-as-a-Service (MaaS) Bundle System** implemented in the decentralized simulation platform. The system enables multi-modal trip bundling where a single journey combines multiple transport segments (e.g., bike + train + bus).

## Key Concepts

### What is a Bundle?

A **bundle** is a multi-modal journey composed of multiple **segments**:
- Each segment represents one leg of the journey (e.g., bike from home to station)
- Segments are provided by different providers (bike share, bus company, train operator)
- Segments are tokenized as NFTs representing capacity (e.g., "2 seats from Stop A → Stop B at 08:05")
- Bundles offer discounts for combining multiple modes (5% per additional segment, max 15%)

### Example Bundle

```
Origin: [0, 0] → Destination: [10, 10]

Bundle ID: abc123def456
├─ Segment 1: BikeShare (0,0) → (3,3) | $2.00 | 10 min
├─ Segment 2: BusCompany (3,3) → (7,7) | $3.50 | 15 min
└─ Segment 3: TaxiCo (7,7) → (10,10) | $5.00 | 8 min

Total Price: $10.50 → $9.45 (10% bundle discount)
Total Duration: 33 minutes
Transfers: 2
```

## Architecture

### 1. Database Schema (PostgreSQL)

The system uses PostgreSQL with SQLAlchemy ORM for persistent storage:

#### Core Tables

- **`runs`** - Simulation run metadata
  - `run_id`, `start_time`, `end_time`, `total_steps`
  - `num_commuters`, `num_providers`, `network_type`
  - `config` (JSONB) - Full simulation configuration

- **`ticks`** - Time-series data for each simulation step
  - `run_id`, `tick`, `timestamp`
  - `active_commuters`, `active_providers`, `active_requests`
  - `active_bundles`, `completed_reservations`, `total_revenue`

- **`commuters`** - Commuter agent demographics
  - `commuter_id`, `blockchain_address`, `origin_area`, `destination_area`
  - `preferences` (JSONB) - price_weight, time_weight, mode_preferences
  - `budget`

- **`providers`** - Provider agent capacity and pricing
  - `provider_id`, `blockchain_address`, `mode`, `capacity`
  - `base_price`, `pricing_strategy`, `service_area` (JSONB)

- **`requests`** - Travel requests from commuters
  - `request_id`, `commuter_id`, `origin`, `destination`
  - `start_time`, `time_window`, `max_price`
  - `status` (active, matched, completed, cancelled)
  - `blockchain_tx_hash`

- **`bundles`** - Multi-modal journey bundles
  - `bundle_id`, `request_id`, `expected_depart_time`, `expected_arrive_time`
  - `total_price`, `total_duration`, `num_segments`, `bundle_discount`
  - `utility_score`, `status` (proposed, reserved, completed, cancelled)

- **`bundle_segments`** - Individual legs within bundles
  - `bundle_id`, `segment_id`, `sequence` (order in journey)
  - `provider_id`, `mode`, `origin`, `destination`
  - `depart_time`, `arrive_time`, `price`, `distance`
  - `nft_token_id`, `blockchain_tx_hash`
  - `status` (available, reserved, consumed, expired)

- **`reservations`** - Confirmed bookings
  - `reservation_id`, `bundle_id`, `commuter_id`, `request_id`
  - `total_price`, `cleared_price`, `lead_time`
  - `created_tick`, `blockchain_tx_hash`, `payment_status`

- **`segment_reservations`** - Link between reservations and segments
  - `reservation_id`, `segment_id`, `seats_consumed`, `actual_price`

### 2. Decentralized Bundle Router

**File:** `abm/utils/bundle_router.py`

The `DecentralizedBundleRouter` implements **peer-to-peer bundle discovery** to avoid centralization:

#### Key Features

✅ **Distributed Segment Discovery**
- Reads NFT mint events directly from blockchain
- Queries marketplace offers from decentralized storage
- No central database dependency

✅ **Peer-to-Peer Route Assembly**
- Each commuter independently builds routes using graph traversal
- Depth-first search to find all valid paths
- No central coordinator needed

✅ **Auction-Driven Path Formation**
- Contested segments trigger auctions
- Competitive pricing through market mechanisms
- Decentralized price discovery

#### Core Methods

```python
# Get active segments from blockchain
segments = router.get_active_segments(time_window=(0, 100))

# Build bundle options using graph traversal
bundles = router.build_bundles(
    origin=[0, 0],
    destination=[10, 10],
    active_segments=segments,
    start_time=50,
    max_transfers=3,
    time_tolerance=5
)

# Returns sorted list of bundles by utility score
# [
#   {
#     'bundle_id': 'abc123',
#     'segments': [...],
#     'total_price': 9.45,
#     'bundle_discount': 1.05,
#     'utility_score': -15.2,
#     'num_transfers': 2
#   },
#   ...
# ]
```

### 3. Blockchain Interface Extensions

**File:** `abm/utils/blockchain_interface.py`

New methods added to support bundles:

```python
# Get active segments (decentralized)
segments = blockchain.get_active_segments(time_window=(0, 100))

# Build bundles using decentralized routing
bundles = blockchain.build_bundles(
    origin=[0, 0],
    destination=[10, 10],
    start_time=50,
    max_transfers=3,
    time_tolerance=5
)

# Fallback: Mint direct segment if no bundles available
success = blockchain.mint_direct_segment_for(request)

# Reserve bundle atomically
success, reservation_id = blockchain.reserve_bundle(
    commuter_id=123,
    request_id=456,
    bundle=best_bundle
)
```

### 4. Data Exporter

**File:** `abm/database/exporter.py`

The `SimulationExporter` handles PostgreSQL export:

```python
from abm.database.exporter import SimulationExporter

exporter = SimulationExporter(
    connection_string='postgresql://user:pass@localhost:5432/maas_simulation'
)

# Export complete simulation
success = exporter.export_simulation(
    run_id='sim_20251025_001',
    model=model,
    blockchain_interface=blockchain,
    advanced_metrics=metrics,
    config=config
)
```

**Export Order (respects dependencies):**
1. Simulation run metadata
2. Agents (commuters, providers)
3. Travel requests
4. Bundles and segments
5. Reservations and segment reservations
6. Time-series tick data

## Usage Flow

### Commuter Perspective

```python
# 1. Commuter creates travel request
req = commuter.create_request()

# 2. Get active segments from blockchain (decentralized)
active_segments = blockchain.get_active_segments()

# 3. Build bundle options using local graph traversal
bundle_options = blockchain.build_bundles(
    req.origin,
    req.destination,
    req.start_time
)

# 4. If no bundles available, trigger direct segment minting
if not bundle_options:
    blockchain.mint_direct_segment_for(req)
    # Wait for providers to respond
    bundle_options = blockchain.build_bundles(...)

# 5. Select best bundle based on preferences
best_bundle = select_best(bundle_options, commuter.preferences)

# 6. Reserve bundle atomically
success, reservation_id = blockchain.reserve_bundle(
    commuter.id,
    req.id,
    best_bundle
)

# 7. Record reservation in database
if success:
    record_reservation(run_id, req, best_bundle, reservation_id)
```

### Provider Perspective

```python
# 1. Provider mints NFT segments for their capacity
blockchain.list_nft(
    provider_id=provider.id,
    origin=[0, 0],
    destination=[3, 3],
    start_time=50,
    price=2.00,
    mode='bike'
)

# 2. Provider receives notifications for unmatched requests
notifications = blockchain.get_provider_notifications(provider.id)

# 3. Provider submits offers for unmatched requests
for notification in notifications:
    if can_serve(notification):
        blockchain.submit_offer_marketplace(
            provider_id=provider.id,
            request_id=notification['request_id'],
            price=calculate_price(...),
            ...
        )
```

## Database Setup

### PostgreSQL Installation

```bash
# Install PostgreSQL
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Windows
# Download from https://www.postgresql.org/download/windows/
```

### Database Creation

```bash
# Create database and user
sudo -u postgres psql

CREATE DATABASE maas_simulation;
CREATE USER maas_user WITH PASSWORD 'maas_password';
GRANT ALL PRIVILEGES ON DATABASE maas_simulation TO maas_user;
\q
```

### Python Dependencies

```bash
pip install sqlalchemy psycopg2-binary
```

### Environment Configuration

```bash
# Set database connection string
export DATABASE_URL='postgresql://maas_user:maas_password@localhost:5432/maas_simulation'
```

### Initialize Tables

```python
from abm.database.models import DatabaseManager

# Create database manager
db_manager = DatabaseManager()

# Create all tables
db_manager.create_tables()

# Or reset database (drops and recreates)
db_manager.reset_database()
```

## Decentralization Design

### Problem: Central Coordinator

Traditional MaaS platforms use a central router (like OpenTripPlanner) that:
- Maintains a centralized database of all routes
- Performs route planning on behalf of users
- Acts as a single point of failure
- Can manipulate results or pricing

### Solution: Peer-to-Peer Discovery

Our decentralized approach:

1. **Blockchain as Truth Source**
   - All segments published as NFTs or offers on blockchain
   - Immutable, transparent, censorship-resistant

2. **Local Route Assembly**
   - Each commuter runs graph traversal locally
   - No need to trust a central router
   - Privacy-preserving (origin/destination not shared)

3. **Auction-Driven Pricing**
   - Contested segments trigger on-chain auctions
   - Market-based price discovery
   - No central price manipulation

4. **Distributed Execution**
   - Providers independently mint segments
   - Commuters independently discover routes
   - Blockchain coordinates without centralization

## Performance Considerations

### Database Indexing

The schema includes strategic indexes:
- `idx_run_start_time` - Fast run queries by time
- `idx_bundle_run_status` - Filter bundles by status
- `idx_segment_bundle_seq` - Ordered segment retrieval
- `idx_reservation_commuter` - Commuter history queries

### Caching Strategy

- Bundle router caches segment graph locally
- Blockchain interface caches NFT listings (TTL: 300s)
- Database session pooling for concurrent access

### Scalability

- PostgreSQL handles millions of records efficiently
- JSONB columns for flexible schema evolution
- Partitioning possible for large-scale deployments

## Future Enhancements

1. **Real-Time Bundle Updates**
   - WebSocket notifications for segment availability
   - Dynamic re-routing when segments become unavailable

2. **Machine Learning Integration**
   - Predict optimal bundle configurations
   - Learn commuter preferences over time

3. **Cross-Chain Bundles**
   - Segments from multiple blockchain networks
   - Atomic swaps for cross-chain reservations

4. **Privacy Enhancements**
   - Zero-knowledge proofs for route privacy
   - Encrypted segment details

## Troubleshooting

### Database Connection Issues

```python
# Test connection
from abm.database.models import DatabaseManager

db = DatabaseManager('postgresql://user:pass@localhost:5432/maas_simulation')
session = db.get_session()
print("Connected successfully!")
session.close()
```

### No Bundles Found

- Check if providers have minted segments
- Verify time_window matches segment availability
- Increase `max_transfers` parameter
- Increase `time_tolerance` for flexibility

### Export Failures

- Check database permissions
- Verify all foreign key relationships
- Review logs for specific SQL errors
- Ensure database schema is up to date

## References

- **Database Models:** `abm/database/models.py`
- **Bundle Router:** `abm/utils/bundle_router.py`
- **Data Exporter:** `abm/database/exporter.py`
- **Blockchain Interface:** `abm/utils/blockchain_interface.py`

