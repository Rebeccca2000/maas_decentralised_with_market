# Simulation Interface Updates

## Overview

The simulation interface (`abm/agents/run_decentralized_model.py`) has been updated with all required functionality for the bundle system and database export.

## ✅ Updates Completed

### 1. Command-Line Arguments

Added new arguments to control simulation behavior:

```bash
# Bundle System Control
--enable-bundles        Enable proactive segment creation (default: True)
--disable-bundles       Disable bundle system completely

# Database Export
--export-db             Export simulation results to database (SQLite)

# Existing Arguments (now properly passed)
--network               Blockchain network (localhost, optimism-sepolia, etc.)
--rpc-url               Custom RPC URL for L2 networks
--chain-id              Custom chain ID
--steps                 Number of simulation steps
--commuters             Number of commuter agents
--providers             Number of provider agents
--no-plots              Skip plot generation for faster execution
--debug                 Run in debug mode (5 commuters, 3 providers, 20 steps)
--big-test              Run big test (15 commuters, 8 providers, 50 steps)
```

### 2. Function Signature Updates

**`run_simulation()` function now includes:**
- `enable_proactive_segments` parameter (default: True)
- Proper passing of `network`, `rpc_url`, `chain_id` to all execution paths

**Before:**
```python
run_simulation(steps=20, num_commuters=5, num_providers=3, 
               no_plots=args.no_plots, export_db=args.export_db)
```

**After:**
```python
run_simulation(
    steps=20, 
    num_commuters=5, 
    num_providers=3, 
    no_plots=args.no_plots, 
    network=args.network,
    rpc_url=args.rpc_url,
    chain_id=args.chain_id,
    export_db=args.export_db,
    enable_proactive_segments=enable_bundles
)
```

### 3. Database Export Integration

The database export functionality is fully integrated:

```python
if export_db:
    from abm.database.exporter import SimulationExporter
    
    exporter = SimulationExporter()
    run_id = f"sim_{int(time.time())}"
    
    success = exporter.export_simulation(
        run_id=run_id,
        model=model,
        blockchain_interface=marketplace,
        advanced_metrics=advanced_metrics,
        config={
            'steps': steps,
            'commuters': num_commuters,
            'providers': num_providers,
            'network': network,
            'rpc_url': rpc_url if rpc_url else 'default',
            'chain_id': chain_id if chain_id else 'default'
        }
    )
```

### 4. Bundle System Integration

The bundle system is now properly controlled via command-line arguments:

- **Default behavior**: Bundles enabled (proactive segments created)
- **Disable bundles**: Use `--disable-bundles` flag
- **Explicit enable**: Use `--enable-bundles` flag

The `enable_proactive_segments` parameter is passed to the model:

```python
model = SimplifiedMaaSModel(
    num_commuters=num_commuters,
    num_providers=num_providers,
    total_steps=steps,
    enable_proactive_segments=enable_proactive_segments
)
```

### 5. Status Messages

Updated completion messages to reflect bundle system status:

```python
if enable_proactive_segments:
    print("✅ Bundle system enabled with proactive segment creation")
if export_db:
    print(f"✅ Simulation data exported to database")
```

## 📊 Database Schema

The simulation now exports to SQLite database (`maas_bundles.db`) with the following tables:

- **runs**: Simulation run metadata
- **commuters**: Commuter agent data
- **providers**: Provider agent data
- **requests**: Travel requests
- **bundles**: Multi-modal journey bundles
- **bundle_segments**: Individual segments within bundles
- **tick_data**: Time-series metrics

## 🚀 Usage Examples

### Basic Simulation with Bundles and Database Export

```bash
python abm/agents/run_decentralized_model.py \
  --steps 30 \
  --commuters 5 \
  --providers 5 \
  --no-plots \
  --export-db
```

### Debug Mode (Quick Test)

```bash
python abm/agents/run_decentralized_model.py --debug --export-db
```

### Disable Bundle System

```bash
python abm/agents/run_decentralized_model.py \
  --steps 50 \
  --disable-bundles \
  --export-db
```

### L2 Network with Bundles

```bash
python abm/agents/run_decentralized_model.py \
  --network optimism-sepolia \
  --steps 100 \
  --commuters 20 \
  --providers 10 \
  --export-db
```

### Custom RPC Endpoint

```bash
python abm/agents/run_decentralized_model.py \
  --network base-sepolia \
  --rpc-url https://your-custom-rpc.com \
  --steps 50 \
  --export-db
```

## 🔍 Verification

Run the verification script to confirm all updates:

```bash
python verify_simulation_updates.py
```

Expected output:
```
✅ Test 1: Importing run_decentralized_model...
   ✓ Module imported successfully

✅ Test 2: Checking run_simulation function signature...
   ✓ All required parameters present

✅ Test 3: Checking SimplifiedMaaSModel initialization...
   ✓ Model supports enable_proactive_segments parameter

✅ Test 4: Checking database exporter availability...
   ✓ SimulationExporter imported successfully
   ✓ Exporter has all required parameters

✅ Test 5: Checking database models...
   ✓ All SQLite models imported successfully
   ✓ BundleSegment has all required columns
```

## 📈 Database Queries

After running a simulation with `--export-db`, query the results:

```bash
python examples/query_bundles.py
```

Or query directly with SQL:

```python
import sqlite3

conn = sqlite3.connect('maas_bundles.db')
cursor = conn.cursor()

# Get latest simulation run
cursor.execute("""
    SELECT run_id, total_steps, num_commuters, num_providers
    FROM runs
    ORDER BY created_at DESC
    LIMIT 1
""")

run = cursor.fetchone()
print(f"Latest run: {run}")

# Get bundles from latest run
cursor.execute("""
    SELECT COUNT(*) FROM bundles WHERE run_id = ?
""", (run[0],))

bundle_count = cursor.fetchone()[0]
print(f"Bundles created: {bundle_count}")

conn.close()
```

## 🎯 Key Features

1. **✅ Bundle System**: Fully integrated with enable/disable control
2. **✅ Database Export**: Automatic export to SQLite with complete schema
3. **✅ Network Support**: Works with localhost and L2 networks
4. **✅ Backward Compatible**: All existing functionality preserved
5. **✅ Flexible Configuration**: Command-line control over all features

## 🔧 Technical Details

### Parameter Flow

```
Command Line Args
    ↓
main() function
    ↓
run_simulation() function
    ↓
SimplifiedMaaSModel.__init__()
    ↓
Provider/Commuter agents
    ↓
Bundle creation & Database export
```

### Bundle System Flow

1. **Enabled** (`enable_proactive_segments=True`):
   - Providers create route segments every 10 steps
   - Segments stored in marketplace database
   - Commuters can build multi-modal bundles
   - Bundles exported to database

2. **Disabled** (`enable_proactive_segments=False`):
   - Providers only respond to specific requests
   - No proactive segments created
   - Traditional request-response model

## 📝 Notes

- Database file: `maas_bundles.db` (created automatically)
- Bundle creation depends on random coordinates aligning
- Longer simulations (100+ steps) increase bundle creation probability
- Use `--no-plots` for faster execution during testing

## 🎉 Summary

All required updates have been successfully implemented:

- ✅ Command-line arguments for bundle control
- ✅ Database export integration
- ✅ Proper parameter passing to all execution paths
- ✅ Bundle system enable/disable functionality
- ✅ Updated status messages
- ✅ Full backward compatibility

The simulation interface is now production-ready with complete bundle system and database export support!

