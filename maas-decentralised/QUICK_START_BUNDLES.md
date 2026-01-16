# Quick Start: MaaS Bundle System

Get started with multi-modal journey bundles in 5 minutes!

## Prerequisites

- Python 3.8+
- PostgreSQL 12+ installed and running
- Hardhat blockchain node (or L2 network access)

## Step 1: Install Dependencies (2 minutes)

```bash
# Install Python packages
pip install -r requirements.txt

# Verify installation
python -c "import sqlalchemy, psycopg2; print('✅ Database packages installed')"
```

## Step 2: Setup PostgreSQL Database (2 minutes)

### Option A: Quick Setup (Default Configuration)

```bash
# Create database and user (run in PostgreSQL shell)
sudo -u postgres psql

CREATE DATABASE maas_simulation;
CREATE USER maas_user WITH PASSWORD 'maas_password';
GRANT ALL PRIVILEGES ON DATABASE maas_simulation TO maas_user;
\q

# Run setup script
python setup_database.py
```

### Option B: Interactive Setup (Custom Configuration)

```bash
python setup_database.py --interactive
```

### Option C: Custom Connection String

```bash
python setup_database.py --connection-string "postgresql://user:pass@host:port/db"
```

## Step 3: Test Bundle System (1 minute)

```python
# test_bundles.py
from abm.utils.bundle_router import DecentralizedBundleRouter
from abm.utils.blockchain_interface import BlockchainInterface

# Initialize blockchain
blockchain = BlockchainInterface()

# Get bundle router
router = blockchain.get_bundle_router()

# Create mock segments
segments = [
    {
        'segment_id': 'seg_1',
        'type': 'offer',
        'provider_id': 1,
        'mode': 'bike',
        'origin': [0, 0],
        'destination': [3, 3],
        'depart_time': 10,
        'arrive_time': 20,
        'price': 2.0,
        'capacity': 1,
        'status': 'available'
    },
    {
        'segment_id': 'seg_2',
        'type': 'offer',
        'provider_id': 2,
        'mode': 'bus',
        'origin': [3, 3],
        'destination': [10, 10],
        'depart_time': 22,
        'arrive_time': 35,
        'price': 3.5,
        'capacity': 1,
        'status': 'available'
    }
]

# Build bundles
bundles = router.build_bundles(
    origin=[0, 0],
    destination=[10, 10],
    active_segments=segments,
    start_time=10,
    max_transfers=3,
    time_tolerance=5
)

# Print results
print(f"✅ Found {len(bundles)} bundle options")
for bundle in bundles:
    print(f"  Bundle {bundle['bundle_id']}:")
    print(f"    - Segments: {bundle['num_segments']}")
    print(f"    - Price: ${bundle['total_price']:.2f}")
    print(f"    - Duration: {bundle['total_duration']} ticks")
    print(f"    - Discount: ${bundle['bundle_discount']:.2f}")
```

Run the test:

```bash
python test_bundles.py
```

Expected output:
```
✅ Found 1 bundle options
  Bundle abc123def456:
    - Segments: 2
    - Price: $5.23
    - Duration: 25 ticks
    - Discount: $0.28
```

## Step 4: Run Full Simulation with Bundles

### Start Hardhat Blockchain

```bash
# Terminal 1
npx hardhat node
```

### Run Simulation with Database Export

```bash
# Terminal 2
python abm/agents/run_decentralized_model.py \
    --steps 50 \
    --commuters 10 \
    --providers 5 \
    --export-db
```

**Note:** The `--export-db` flag will be added in the next step.

## Step 5: Query Bundle Data

```python
# query_bundles.py
from abm.database.models import DatabaseManager, Bundle, BundleSegment, Reservation
from sqlalchemy import func

# Connect to database
db = DatabaseManager()
session = db.get_session()

# Query bundles
bundles = session.query(Bundle).filter(Bundle.status == 'completed').all()

print(f"📊 Found {len(bundles)} completed bundles")
print()

for bundle in bundles[:5]:  # Show first 5
    print(f"Bundle {bundle.bundle_id}:")
    print(f"  Price: ${bundle.total_price:.2f}")
    print(f"  Duration: {bundle.total_duration} ticks")
    print(f"  Segments: {bundle.num_segments}")
    print(f"  Discount: ${bundle.bundle_discount:.2f}")
    
    # Show segments
    for segment in bundle.segments:
        print(f"    {segment.sequence}. {segment.mode}: "
              f"{segment.origin} → {segment.destination} (${segment.price:.2f})")
    print()

# Statistics
stats = session.query(
    func.count(Bundle.id).label('total_bundles'),
    func.avg(Bundle.total_price).label('avg_price'),
    func.avg(Bundle.num_segments).label('avg_segments'),
    func.sum(Bundle.bundle_discount).label('total_savings')
).filter(Bundle.status == 'completed').first()

print("📈 Bundle Statistics:")
print(f"  Total Bundles: {stats.total_bundles}")
print(f"  Average Price: ${stats.avg_price:.2f}")
print(f"  Average Segments: {stats.avg_segments:.1f}")
print(f"  Total Savings: ${stats.total_savings:.2f}")

session.close()
```

Run the query:

```bash
python query_bundles.py
```

## Common Use Cases

### 1. Find All Multi-Modal Journeys

```python
from abm.database.models import DatabaseManager, Bundle

db = DatabaseManager()
session = db.get_session()

# Bundles with 2+ segments (multi-modal)
multi_modal = session.query(Bundle).filter(Bundle.num_segments >= 2).all()

print(f"Found {len(multi_modal)} multi-modal journeys")
```

### 2. Calculate Provider Revenue from Bundles

```python
from abm.database.models import DatabaseManager, Provider, BundleSegment
from sqlalchemy import func

db = DatabaseManager()
session = db.get_session()

# Revenue by provider
revenue = session.query(
    Provider.mode,
    func.sum(BundleSegment.price).label('total_revenue'),
    func.count(BundleSegment.id).label('segments_sold')
).join(BundleSegment).group_by(Provider.mode).all()

for mode, rev, count in revenue:
    print(f"{mode}: ${rev:.2f} from {count} segments")
```

### 3. Analyze Bundle Discounts

```python
from abm.database.models import DatabaseManager, Bundle
from sqlalchemy import func

db = DatabaseManager()
session = db.get_session()

# Discount analysis
discounts = session.query(
    Bundle.num_segments,
    func.avg(Bundle.bundle_discount).label('avg_discount'),
    func.count(Bundle.id).label('count')
).group_by(Bundle.num_segments).all()

print("Discount by Bundle Size:")
for segments, discount, count in discounts:
    print(f"  {segments} segments: ${discount:.2f} avg discount ({count} bundles)")
```

### 4. Export to CSV for Analysis

```python
from abm.database.models import DatabaseManager, Bundle
import pandas as pd

db = DatabaseManager()
session = db.get_session()

# Query bundles
bundles = session.query(Bundle).all()

# Convert to DataFrame
data = [{
    'bundle_id': b.bundle_id,
    'total_price': b.total_price,
    'num_segments': b.num_segments,
    'bundle_discount': b.bundle_discount,
    'total_duration': b.total_duration,
    'status': b.status
} for b in bundles]

df = pd.DataFrame(data)
df.to_csv('bundles_export.csv', index=False)
print(f"✅ Exported {len(df)} bundles to bundles_export.csv")
```

## Troubleshooting

### Database Connection Failed

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list | grep postgresql  # macOS

# Test connection manually
psql -h localhost -U maas_user -d maas_simulation
```

### Tables Not Created

```bash
# Reset database
python setup_database.py --reset

# Verify tables
python -c "from abm.database.models import DatabaseManager; \
           from sqlalchemy import inspect; \
           db = DatabaseManager(); \
           inspector = inspect(db.engine); \
           print(inspector.get_table_names())"
```

### No Bundles Found

- Ensure simulation ran with bundle support enabled
- Check if providers minted segments
- Verify commuters created requests
- Review simulation logs for errors

### Import Errors

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Verify imports
python -c "from abm.database.models import DatabaseManager; \
           from abm.utils.bundle_router import DecentralizedBundleRouter; \
           print('✅ All imports successful')"
```

## Next Steps

1. **Read Full Documentation:** `MAAS_BUNDLE_SYSTEM.md`
2. **Customize Bundle Logic:** Edit `abm/utils/bundle_router.py`
3. **Add Custom Metrics:** Extend database models in `abm/database/models.py`
4. **Integrate with Web UI:** Add bundle visualization to React frontend
5. **Deploy to Production:** Use managed PostgreSQL (AWS RDS, Google Cloud SQL)

## Environment Variables

Create a `.env` file:

```bash
# Database
DATABASE_URL=postgresql://maas_user:maas_password@localhost:5432/maas_simulation

# Blockchain
BLOCKCHAIN_NETWORK=localhost
BLOCKCHAIN_RPC=http://127.0.0.1:8545

# Optional: L2 Networks
# BLOCKCHAIN_NETWORK=arbitrum-sepolia
# BLOCKCHAIN_RPC=https://sepolia-rollup.arbitrum.io/rpc
```

Load environment:

```bash
export $(cat .env | xargs)
```

## Performance Tips

1. **Use Connection Pooling**
   ```python
   db = DatabaseManager()
   db.engine.pool_size = 10
   db.engine.max_overflow = 20
   ```

2. **Batch Inserts**
   ```python
   session.bulk_insert_mappings(Bundle, bundle_dicts)
   session.commit()
   ```

3. **Index Optimization**
   - Already included in schema
   - Monitor with `EXPLAIN ANALYZE` in PostgreSQL

4. **Cache Frequently Accessed Data**
   - Use Redis for hot data
   - Cache bundle router segment graph

## Support

- **Documentation:** `MAAS_BUNDLE_SYSTEM.md`
- **Database Schema:** `abm/database/models.py`
- **Bundle Router:** `abm/utils/bundle_router.py`
- **Examples:** `test_bundles.py`, `query_bundles.py`

---

**Ready to build decentralized multi-modal mobility! 🚀**

