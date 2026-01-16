# Getting Started Checklist - MaaS Bundle System

## ✅ Immediate Actions (5 minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

**Verify:**
```bash
python -c "import sqlalchemy, psycopg2; print('✅ Dependencies installed')"
```

---

### Step 2: Setup PostgreSQL Database

**Option A: Quick Setup (Recommended)**
```bash
# Create database (in PostgreSQL shell)
sudo -u postgres psql
CREATE DATABASE maas_simulation;
CREATE USER maas_user WITH PASSWORD 'maas_password';
GRANT ALL PRIVILEGES ON DATABASE maas_simulation TO maas_user;
\q

# Run setup script
python setup_database.py
```

**Option B: Interactive Setup**
```bash
python setup_database.py --interactive
```

**Verify:**
```bash
python -c "from abm.database.models import DatabaseManager; \
           db = DatabaseManager(); \
           print('✅ Database connected')"
```

---

### Step 3: Test Bundle System
```bash
python examples/test_bundles.py
```

**Expected Output:**
```
✅ Found 3 bundle options
✅ Graph has 4 nodes
✅ Found 2 valid paths
🎉 All tests completed successfully!
```

---

## 📚 Review Documentation (10 minutes)

### Essential Reading

- [ ] **Quick Start Guide** - `QUICK_START_BUNDLES.md`
  - 5-minute setup instructions
  - Common use cases
  - Troubleshooting tips

- [ ] **System Overview** - `README_BUNDLE_SYSTEM.md`
  - Architecture overview
  - Key features
  - Examples

- [ ] **Complete Documentation** - `MAAS_BUNDLE_SYSTEM.md`
  - Detailed architecture
  - Database schema
  - API reference

### Optional Reading

- [ ] **Implementation Summary** - `IMPLEMENTATION_SUMMARY.md`
  - Technical details
  - Code structure
  - Performance notes

- [ ] **Changes Summary** - `CHANGES_SUMMARY.md`
  - What was added
  - File structure
  - Statistics

---

## 🧪 Test the System (5 minutes)

### Test 1: Bundle Routing
```bash
python examples/test_bundles.py
```

**What it tests:**
- ✅ Segment graph construction
- ✅ Path finding algorithm
- ✅ Bundle creation with discounts
- ✅ Utility scoring

---

### Test 2: Database Queries
```bash
python examples/query_bundles.py
```

**What it shows:**
- ✅ Recent simulation runs
- ✅ Bundle statistics
- ✅ Mode distribution
- ✅ Provider performance
- ✅ CSV export

**Note:** Will show "No data" until you run a simulation with `--export-db`

---

## 🔍 Explore the Code (15 minutes)

### Core Files to Review

- [ ] **Database Models** - `abm/database/models.py`
  - 9 SQLAlchemy tables
  - Relationships and indexes
  - DatabaseManager class

- [ ] **Bundle Router** - `abm/utils/bundle_router.py`
  - DecentralizedBundleRouter class
  - Graph-based routing
  - DFS path finding

- [ ] **Data Exporter** - `abm/database/exporter.py`
  - SimulationExporter class
  - Export logic
  - Error handling

- [ ] **Blockchain Extensions** - `abm/utils/blockchain_interface.py`
  - Lines 188-194: Bundle router initialization
  - Lines 1404-1596: Bundle methods

---

## 🚀 Next Steps (Integration)

### Step 1: Understand Current Flow

**Current simulation flow:**
```
1. Start Hardhat → npx hardhat node
2. Run simulation → python abm/agents/run_decentralized_model.py
3. View results → Web UI or console output
```

**What's missing:** Database export

---

### Step 2: Add Database Export (To Be Done)

**Modify:** `abm/agents/run_decentralized_model.py`

**Add argument:**
```python
parser.add_argument('--export-db', action='store_true',
                   help='Export simulation results to PostgreSQL')
```

**Add export logic (after simulation completes):**
```python
if args.export_db:
    from abm.database.exporter import SimulationExporter
    
    exporter = SimulationExporter()
    success = exporter.export_simulation(
        run_id=f"sim_{int(time.time())}",
        model=model,
        blockchain_interface=marketplace,
        advanced_metrics=advanced_metrics,
        config={
            'steps': args.steps,
            'commuters': args.num_commuters,
            'providers': args.num_providers,
            'network': args.network,
            'rpc_url': args.rpc_url
        }
    )
    
    if success:
        print(f"\n✅ Exported simulation data to database")
        print(f"   Query with: python examples/query_bundles.py")
```

---

### Step 3: Integrate Bundle Logic into Agents (To Be Done)

**Modify:** `abm/agents/decentralized_commuter.py`

**In `step()` method, replace current matching logic with:**

```python
# Get active segments from blockchain
active_segments = self.marketplace.get_active_segments()

# Build bundle options
bundle_options = self.marketplace.build_bundles(
    origin=self.origin,
    destination=self.destination,
    start_time=self.model.current_step,
    max_transfers=3,
    time_tolerance=5
)

# If no bundles, trigger direct segment minting
if not bundle_options:
    request_data = {
        'request_id': self.current_request_id,
        'origin': self.origin,
        'destination': self.destination,
        'start_time': self.model.current_step,
        'max_price': self.budget
    }
    self.marketplace.mint_direct_segment_for(request_data)
    
    # Retry building bundles
    bundle_options = self.marketplace.build_bundles(...)

# Select best bundle based on preferences
if bundle_options:
    best_bundle = self._select_best_bundle(bundle_options)
    
    # Reserve bundle
    success, reservation_id = self.marketplace.reserve_bundle(
        commuter_id=self.unique_id,
        request_id=self.current_request_id,
        bundle=best_bundle
    )
    
    if success:
        self.logger.info(f"Reserved bundle {best_bundle['bundle_id']}")
```

---

### Step 4: Add to Web UI (Optional)

**Create:** `src/components/BundleVisualization.js`

**Features to add:**
- Display bundle options
- Show segment breakdown
- Visualize route on map
- Compare single-mode vs multi-modal

---

## 📊 Verify Everything Works

### Checklist

- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] PostgreSQL running (`sudo systemctl status postgresql`)
- [ ] Database created (`psql -l | grep maas_simulation`)
- [ ] Tables created (`python setup_database.py`)
- [ ] Bundle tests pass (`python examples/test_bundles.py`)
- [ ] Can query database (`python examples/query_bundles.py`)

### Troubleshooting

**Database connection failed:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -h localhost -U maas_user -d maas_simulation
```

**Import errors:**
```bash
pip install --upgrade -r requirements.txt
```

**No bundles found in tests:**
- This is expected if no simulation has run yet
- Run `python examples/test_bundles.py` to test with mock data

---

## 🎯 Success Criteria

You're ready to proceed when:

✅ All dependencies installed  
✅ PostgreSQL database created  
✅ Tables created successfully  
✅ Bundle tests pass  
✅ Can query database (even if empty)  
✅ Documentation reviewed  

---

## 📞 Need Help?

### Documentation
- **Quick Start:** `QUICK_START_BUNDLES.md`
- **Full Docs:** `MAAS_BUNDLE_SYSTEM.md`
- **Examples:** `examples/test_bundles.py`, `examples/query_bundles.py`

### Common Issues

**Q: Database connection failed**  
A: Check PostgreSQL is running and credentials are correct

**Q: No bundles found**  
A: Normal if no simulation has run. Test with `examples/test_bundles.py`

**Q: Import errors**  
A: Run `pip install --upgrade -r requirements.txt`

---

## 🎉 You're Ready!

Once all checkboxes are complete, you have:

✅ Working bundle system  
✅ PostgreSQL database  
✅ Testing tools  
✅ Query examples  
✅ Complete documentation  

**Next:** Integrate with your simulation and start analyzing multi-modal journeys! 🚀

