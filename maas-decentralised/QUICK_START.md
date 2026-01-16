# Quick Start Guide - MaaS Decentralized Platform

## 🚀 Getting Started in 5 Minutes

### 1. Run Your First Simulation

```bash
# Quick test (20 steps, 5 commuters, 3 providers)
python abm/agents/run_decentralized_model.py --debug --export-db
```

This will:
- ✅ Start a local blockchain (Hardhat)
- ✅ Deploy smart contracts
- ✅ Run simulation with bundle system enabled
- ✅ Export results to `maas_bundles.db`

### 2. Check the Results

```bash
# Query the database
python -c "import sqlite3; conn = sqlite3.connect('maas_bundles.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM bundles'); print(f'Bundles created: {cursor.fetchone()[0]}'); conn.close()"
```

### 3. Run a Full Simulation

```bash
# 100 steps, 20 commuters, 10 providers
python abm/agents/run_decentralized_model.py \
  --steps 100 \
  --commuters 20 \
  --providers 10 \
  --no-plots \
  --export-db
```

## 📋 Common Commands

### Basic Simulations

```bash
# Debug mode (fastest)
python abm/agents/run_decentralized_model.py --debug --export-db

# Medium test
python abm/agents/run_decentralized_model.py --big-test --export-db

# Custom configuration
python abm/agents/run_decentralized_model.py \
  --steps 50 \
  --commuters 10 \
  --providers 5 \
  --export-db
```

### Bundle System Control

```bash
# With bundles (default)
python abm/agents/run_decentralized_model.py --debug --export-db

# Without bundles
python abm/agents/run_decentralized_model.py --debug --disable-bundles --export-db
```

### Network Options

```bash
# Local blockchain (default)
python abm/agents/run_decentralized_model.py --debug --export-db

# Optimism Sepolia testnet
python abm/agents/run_decentralized_model.py \
  --network optimism-sepolia \
  --steps 50 \
  --export-db

# Base Sepolia testnet
python abm/agents/run_decentralized_model.py \
  --network base-sepolia \
  --steps 50 \
  --export-db
```

## 🎯 What to Expect

### Simulation Output

```
============================================================
SIMPLIFIED MaaS MARKETPLACE SIMULATION
============================================================
🎫 Bundle system enabled: Providers will create proactive route segments
🧪 Running in DEVELOPMENT mode with synchronous blockchain

Model initialized with 5 commuters and 3 providers
Marketplace API connected: True

🔄 Starting simulation...
Step 1/20 - Requests: 1, Matches: 0, Completed: 0
...
Step 20/20 - Requests: 15, Matches: 12, Completed: 8

============================================================
🎯 SIMULATION COMPLETE
============================================================
✅ Decentralized transportation system successfully demonstrated
✅ Bundle system enabled with proactive segment creation
✅ Simulation data exported to database
```

### Database Contents

After running with `--export-db`, you'll have:

- **Simulation runs**: Metadata about each simulation
- **Commuters**: Agent profiles and preferences
- **Providers**: Service provider data
- **Requests**: Travel requests from commuters
- **Bundles**: Multi-modal journey bundles (if created)
- **Bundle segments**: Individual legs of each bundle

## 🔍 Checking Results

### Quick Database Check

```bash
# Count records
python -c "
import sqlite3
conn = sqlite3.connect('maas_bundles.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM runs')
print(f'Simulation runs: {cursor.fetchone()[0]}')

cursor.execute('SELECT COUNT(*) FROM commuters')
print(f'Commuters: {cursor.fetchone()[0]}')

cursor.execute('SELECT COUNT(*) FROM providers')
print(f'Providers: {cursor.fetchone()[0]}')

cursor.execute('SELECT COUNT(*) FROM requests')
print(f'Requests: {cursor.fetchone()[0]}')

cursor.execute('SELECT COUNT(*) FROM bundles')
print(f'Bundles: {cursor.fetchone()[0]}')

conn.close()
"
```

### View Latest Simulation

```bash
python -c "
import sqlite3
conn = sqlite3.connect('maas_bundles.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT run_id, total_steps, num_commuters, num_providers, network
    FROM runs
    ORDER BY created_at DESC
    LIMIT 1
''')

run = cursor.fetchone()
if run:
    print(f'Latest Run:')
    print(f'  ID: {run[0]}')
    print(f'  Steps: {run[1]}')
    print(f'  Commuters: {run[2]}')
    print(f'  Providers: {run[3]}')
    print(f'  Network: {run[4]}')
else:
    print('No simulation runs found')

conn.close()
"
```

## 🎓 Understanding Bundles

### What are Bundles?

Bundles are multi-modal journeys that combine segments from different providers:

**Example Bundle:**
```
Origin [5, 10] → Destination [20, 25]

Segment 1: Bike from [5, 10] to [12, 12] - $5.00
Segment 2: Bus from [12, 12] to [18, 18] - $3.00
Segment 3: Scooter from [18, 18] to [20, 25] - $4.00

Total: $12.00 (with 10% bundle discount = $10.80)
```

### When are Bundles Created?

Bundles are created when:
1. ✅ Bundle system is enabled (`--enable-bundles` or default)
2. ✅ Providers create proactive segments (every 10 steps)
3. ✅ Commuter origin is near a segment start point
4. ✅ Chain of connecting segments exists
5. ✅ Destination is reachable via the segment network
6. ✅ Time windows overlap

**Note**: Due to random coordinates, bundles may not be created in every simulation. Longer simulations (100+ steps) with more providers increase the probability.

## 🛠️ Troubleshooting

### No Bundles Created

This is normal! Bundle creation depends on:
- Random coordinates aligning
- Sufficient segment density
- Time window overlaps

**Solutions:**
```bash
# Run longer simulation
python abm/agents/run_decentralized_model.py --steps 200 --export-db

# More providers for more segments
python abm/agents/run_decentralized_model.py --providers 20 --export-db

# Both
python abm/agents/run_decentralized_model.py \
  --steps 200 \
  --commuters 30 \
  --providers 20 \
  --export-db
```

### Database Not Created

Make sure you use the `--export-db` flag:

```bash
python abm/agents/run_decentralized_model.py --debug --export-db
```

### Blockchain Connection Issues

If you see blockchain errors:

```bash
# Make sure Hardhat is running
cd blockchain
npx hardhat node

# In another terminal, run simulation
python abm/agents/run_decentralized_model.py --debug --export-db
```

## 📊 Next Steps

### 1. Explore the Database

```bash
# Install SQLite browser (optional)
# Or use Python to query

python -c "
import sqlite3
import pandas as pd

conn = sqlite3.connect('maas_bundles.db')

# Get all bundles
bundles = pd.read_sql_query('SELECT * FROM bundles', conn)
print(bundles)

conn.close()
"
```

### 2. Run Advanced Queries

```bash
# Use the query script
python examples/query_bundles.py
```

### 3. Visualize Results

```bash
# Run with plots enabled
python abm/agents/run_decentralized_model.py \
  --steps 100 \
  --export-db
  # (remove --no-plots flag)
```

### 4. Test on L2 Networks

```bash
# Optimism Sepolia
python abm/agents/run_decentralized_model.py \
  --network optimism-sepolia \
  --steps 50 \
  --export-db
```

## 🎉 Success Checklist

After running your first simulation, you should have:

- ✅ Simulation completed without errors
- ✅ Database file `maas_bundles.db` created
- ✅ Data in all tables (runs, commuters, providers, requests)
- ✅ Possibly some bundles (depends on random coordinates)
- ✅ Blockchain transactions confirmed

## 📚 Additional Resources

- **Full Documentation**: `SIMULATION_INTERFACE_UPDATES.md`
- **Bundle System**: `BUNDLE_SYSTEM_README.md`
- **Database Schema**: `abm/database/models_sqlite.py`
- **Verification**: Run `python verify_simulation_updates.py`

## 💡 Tips

1. **Start small**: Use `--debug` for quick tests
2. **Use `--no-plots`**: Faster execution during development
3. **Always use `--export-db`**: To save results
4. **Check the database**: After each run to verify data
5. **Longer simulations**: Increase bundle creation probability

---

**Ready to start?**

```bash
python abm/agents/run_decentralized_model.py --debug --export-db
```

🚀 Happy simulating!

