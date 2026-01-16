# MaaS Decentralized Simulation - Database Usage Guide

## 📚 Table of Contents

1. [Overview](#overview)
2. [Database Structure](#database-structure)
3. [Running Simulations](#running-simulations)
4. [Analyzing Data](#analyzing-data)
5. [Exporting Data](#exporting-data)
6. [SQL Query Examples](#sql-query-examples)
7. [Visualization Tips](#visualization-tips)

---

## 📊 Overview

The MaaS decentralized simulation database stores comprehensive data about:
- **Simulation runs** and configuration
- **Agent behavior** (commuters and providers)
- **Transportation metrics** (mode usage, bundles, requests)
- **Blockchain data** (transactions, gas metrics, NFT marketplace)
- **Performance analytics** (bundle performance, price trends)

**Database File:** `maas_bundles.db` (SQLite)

---

## 🗄️ Database Structure

### **Total Tables: 19**

#### **Core Simulation Tables (9)**
1. `runs` - Simulation run metadata
2. `ticks` - Time-series data per simulation step
3. `commuters` - Commuter agent data
4. `providers` - Provider agent data
5. `requests` - Travel requests
6. `bundles` - Multi-modal journey bundles
7. `bundle_segments` - Segments within bundles
8. `reservations` - Bundle reservations
9. `segment_reservations` - Individual segment reservations

#### **Analytics Tables (3)**
10. `mode_usage_metrics` - Transport mode statistics
11. `bundle_performance_metrics` - Bundle system performance
12. `price_trends` - Price trends over time

#### **Blockchain Tables (7)**
13. `blockchain_transactions` - All blockchain transactions
14. `nft_tokens` - NFT tokens for service segments
15. `nft_listings` - NFT marketplace listings
16. `smart_contract_calls` - Smart contract function calls
17. `blockchain_events` - Blockchain events
18. `gas_metrics` - Gas usage metrics
19. `marketplace_metrics` - NFT marketplace metrics

---

## 🚀 Running Simulations

### **Basic Simulation with Database Export**

```bash
python abm/agents/run_decentralized_model.py --export-db --no-plots
```

### **Recommended Parameters for Analysis**

```bash
# For bundle creation and comprehensive data
python abm/agents/run_decentralized_model.py \
    --steps 50 \
    --commuters 10 \
    --providers 5 \
    --export-db \
    --no-plots
```

### **Parameters Explained**
- `--steps 50` - Run for 50 simulation steps
- `--commuters 10` - Create 10 commuter agents
- `--providers 5` - Create 5 provider agents
- `--export-db` - Export results to database
- `--no-plots` - Skip visualization (faster execution)

---

## 📈 Analyzing Data

### **1. Comprehensive Analysis Script**

```bash
python analyze_simulation_data.py
```

**Output:**
- Simulation runs overview
- Mode usage analysis
- Bundle performance metrics
- Gas metrics
- Provider performance
- Commuter behavior

### **2. Quick Database Check**

```bash
python check_gas_data.py
```

**Shows:**
- Gas metrics data
- Mode usage metrics
- Bundle performance metrics

### **3. Blockchain Tables Verification**

```bash
python verify_blockchain_tables.py
```

**Displays:**
- All 19 tables with record counts
- Complete schema details
- Blockchain capabilities summary

---

## 📤 Exporting Data

### **Export All Data to CSV**

```bash
python export_to_csv.py
```

**Creates:**
- Individual CSV files for each table
- Pre-built analysis reports:
  - `report_mode_usage.csv`
  - `report_bundle_performance.csv`
  - `report_provider_performance.csv`
  - `report_commuter_behavior.csv`
  - `report_gas_metrics.csv`
  - `report_bundle_details.csv`

**Output Directory:** `exports_YYYYMMDD_HHMMSS/`

---

## 🔍 SQL Query Examples

### **1. Get Latest Simulation Run**

```sql
SELECT * FROM runs 
ORDER BY start_time DESC 
LIMIT 1;
```

### **2. Mode Usage Statistics**

```sql
SELECT 
    mode,
    total_trips,
    total_revenue,
    average_price,
    utilization_rate
FROM mode_usage_metrics
WHERE run_id = 'sim_1762629171'
ORDER BY total_revenue DESC;
```

### **3. Bundle Performance**

```sql
SELECT 
    total_bundles_created,
    total_bundles_reserved,
    bundle_reservation_rate,
    average_bundle_price,
    total_discount_given
FROM bundle_performance_metrics
WHERE run_id = 'sim_1762629171';
```

### **4. Provider Rankings**

```sql
SELECT 
    agent_id,
    mode,
    total_revenue,
    successful_matches,
    avg_price
FROM providers
WHERE run_id = 'sim_1762629171'
ORDER BY total_revenue DESC;
```

### **5. Commuter Spending**

```sql
SELECT 
    agent_id,
    total_requests,
    successful_trips,
    total_spent,
    avg_wait_time
FROM commuters
WHERE run_id = 'sim_1762629171'
ORDER BY total_spent DESC;
```

### **6. Gas Metrics Over Time**

```sql
SELECT 
    tick,
    total_gas_used,
    total_gas_cost,
    total_transactions,
    successful_transactions,
    failed_transactions
FROM gas_metrics
WHERE run_id = 'sim_1762629171'
ORDER BY tick;
```

### **7. Bundle Details**

```sql
SELECT 
    bundle_id,
    origin_x,
    origin_y,
    dest_x,
    dest_y,
    base_price,
    discount_amount,
    final_price,
    num_segments,
    description
FROM bundles
WHERE run_id = 'sim_1762629171';
```

### **8. Cross-Table Analysis: Mode Revenue by Run**

```sql
SELECT 
    r.run_id,
    r.start_time,
    r.total_steps,
    m.mode,
    m.total_trips,
    m.total_revenue
FROM runs r
JOIN mode_usage_metrics m ON r.run_id = m.run_id
ORDER BY r.start_time DESC, m.total_revenue DESC;
```

---

## 📊 Visualization Tips

### **Using Python/Pandas**

```python
import pandas as pd
import sqlite3

# Connect to database
conn = sqlite3.connect('maas_bundles.db')

# Load mode usage data
df_modes = pd.read_sql_query('''
    SELECT * FROM mode_usage_metrics
    WHERE run_id = 'sim_1762629171'
''', conn)

# Create visualizations
import matplotlib.pyplot as plt

# Bar chart of revenue by mode
df_modes.plot(x='mode', y='total_revenue', kind='bar')
plt.title('Revenue by Transport Mode')
plt.ylabel('Revenue ($)')
plt.show()

conn.close()
```

### **Using Excel**

1. Open CSV files from `exports_*/` directory
2. Create pivot tables for analysis
3. Use charts to visualize:
   - Mode usage distribution (pie chart)
   - Revenue trends (line chart)
   - Provider performance (bar chart)
   - Bundle adoption (area chart)

### **Using R**

```r
library(RSQLite)
library(ggplot2)

# Connect to database
con <- dbConnect(SQLite(), "maas_bundles.db")

# Query data
modes <- dbGetQuery(con, "
    SELECT * FROM mode_usage_metrics
    WHERE run_id = 'sim_1762629171'
")

# Create visualization
ggplot(modes, aes(x=mode, y=total_revenue, fill=mode)) +
    geom_bar(stat='identity') +
    labs(title='Revenue by Transport Mode', y='Revenue ($)')

dbDisconnect(con)
```

---

## 🎯 Common Analysis Tasks

### **1. Compare Multiple Simulation Runs**

```sql
SELECT 
    r.run_id,
    r.total_steps,
    r.num_commuters,
    r.num_providers,
    SUM(m.total_revenue) as total_revenue,
    COUNT(DISTINCT m.mode) as num_modes
FROM runs r
LEFT JOIN mode_usage_metrics m ON r.run_id = m.run_id
GROUP BY r.run_id
ORDER BY r.start_time DESC;
```

### **2. Calculate Market Share**

```sql
WITH total AS (
    SELECT SUM(total_trips) as total_trips
    FROM mode_usage_metrics
    WHERE run_id = 'sim_1762629171'
)
SELECT 
    mode,
    total_trips,
    ROUND(100.0 * total_trips / total.total_trips, 2) as market_share_pct
FROM mode_usage_metrics, total
WHERE run_id = 'sim_1762629171'
ORDER BY market_share_pct DESC;
```

### **3. Analyze Bundle Efficiency**

```sql
SELECT 
    AVG(num_segments) as avg_segments,
    AVG(discount_amount) as avg_discount,
    AVG(final_price) as avg_price,
    COUNT(*) as total_bundles
FROM bundles
WHERE run_id = 'sim_1762629171';
```

---

## 🔧 Database Maintenance

### **Check Database Size**

```bash
ls -lh maas_bundles.db
```

### **Backup Database**

```bash
cp maas_bundles.db maas_bundles_backup_$(date +%Y%m%d).db
```

### **Clear Old Data**

```sql
-- Delete runs older than 30 days
DELETE FROM runs 
WHERE start_time < datetime('now', '-30 days');
```

---

## 📝 Notes

- **Database Type:** SQLite (file-based, no server required)
- **Location:** `maas_bundles.db` in project root
- **Relationships:** All tables linked via `run_id` foreign key
- **Indexes:** Optimized for common queries
- **JSON Columns:** Used for flexible data storage (preferences, params, etc.)

---

## 🆘 Troubleshooting

### **Database Locked Error**
- Stop the backend server: Kill Python processes
- Close any database browser tools
- Retry the operation

### **No Data in Tables**
- Ensure you run simulations with `--export-db` flag
- Check that simulation completed successfully
- Verify `run_id` exists in `runs` table

### **Missing Blockchain Data**
- Blockchain transaction tracking requires additional instrumentation
- Gas metrics infrastructure is in place but needs blockchain stats
- NFT data requires marketplace activity

---

## 🎓 Learning Resources

- **SQLite Documentation:** https://www.sqlite.org/docs.html
- **Pandas SQL:** https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html
- **Data Visualization:** Matplotlib, Seaborn, Plotly

---

**Last Updated:** 2025-11-08
**Version:** 1.0

