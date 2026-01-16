# 🎨 MaaS Bundle System - UI Integration Plan

## 📊 Current UI Status

### ✅ Existing Components
- **Dashboard** (`src/components/Dashboard.js`) - System overview with metrics
- **SimulationControl** (`src/components/SimulationControl.js`) - Start/stop simulations
- **Analytics** (`src/components/Analytics.js`) - Charts and performance metrics
- **Results** (`src/components/Results.js`) - Simulation results and KPIs
- **BlockchainStatus** (`src/components/BlockchainStatus.js`) - Contract info
- **Header** (`src/components/Header.js`) - Navigation

### ❌ Missing Bundle Integration
- No bundle-specific pages or components
- No bundle metrics in Results page
- No bundle visualization
- No backend API endpoints for bundle data
- No database query integration

---

## 🎯 Integration Goals

### 1. **Backend API Endpoints** (Flask)
Add new endpoints to query bundle data from PostgreSQL:
- `GET /api/bundles/list` - List all bundles with pagination
- `GET /api/bundles/stats` - Bundle statistics and KPIs
- `GET /api/bundles/details/<bundle_id>` - Detailed bundle information
- `GET /api/bundles/recent` - Recent bundle reservations

### 2. **Frontend Components** (React)
Create new components to display bundle information:
- **BundleVisualization** - Main bundle display component
- **BundleCard** - Individual bundle card with segments
- **BundleStats** - Bundle statistics dashboard
- **BundleTimeline** - Timeline of bundle reservations

### 3. **Enhanced Existing Pages**
Update existing components with bundle data:
- **Results.js** - Add bundle KPIs (total bundles, avg segments, savings)
- **Analytics.js** - Add bundle charts (bundle types, discount distribution)
- **Dashboard.js** - Add bundle activity feed
- **SimulationControl.js** - Add bundle system toggle

### 4. **New Routes**
Add new pages to the application:
- `/bundles` - Bundle visualization and management
- `/bundles/:id` - Individual bundle details

---

## 📋 Implementation Checklist

### Phase 1: Backend API (Flask) ✅ Ready to Implement

#### Task 1.1: Add Database Query Functions
**File:** `backend/app.py`

**New Functions:**
```python
def query_bundles_from_db(limit=50, offset=0):
    """Query bundles from PostgreSQL database"""
    # Connect to PostgreSQL
    # Query bundles with segments
    # Return JSON data

def get_bundle_stats():
    """Get bundle statistics from database"""
    # Total bundles
    # Avg segments per bundle
    # Total discount savings
    # Bundle type distribution
    
def get_bundle_details(bundle_id):
    """Get detailed bundle information"""
    # Bundle metadata
    # All segments
    # Reservation info
    # Pricing breakdown
```

#### Task 1.2: Add API Endpoints
**File:** `backend/app.py`

**New Routes:**
```python
@app.route('/api/bundles/list', methods=['GET'])
def get_bundles_list():
    """List all bundles with pagination"""
    
@app.route('/api/bundles/stats', methods=['GET'])
def get_bundles_stats():
    """Get bundle statistics"""
    
@app.route('/api/bundles/details/<bundle_id>', methods=['GET'])
def get_bundle_details_api(bundle_id):
    """Get detailed bundle information"""
    
@app.route('/api/bundles/recent', methods=['GET'])
def get_recent_bundles():
    """Get recent bundle reservations"""
```

---

### Phase 2: Frontend Components (React) ✅ Ready to Implement

#### Task 2.1: Create BundleVisualization Component
**File:** `src/components/BundleVisualization.js`

**Features:**
- Display list of bundles in card format
- Show bundle segments with icons (🚲 bike, 🚇 train, 🚌 bus)
- Display pricing and discounts
- Filter by date, commuter, provider
- Pagination support

**Component Structure:**
```jsx
const BundleVisualization = () => {
  const [bundles, setBundles] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  
  // Fetch bundles from API
  // Display bundle cards
  // Show statistics
  
  return (
    <div className="container">
      <h2>MaaS Bundles</h2>
      <BundleStats stats={stats} />
      <BundleList bundles={bundles} />
    </div>
  );
};
```

#### Task 2.2: Create BundleCard Component
**File:** `src/components/BundleCard.js`

**Features:**
- Display bundle ID and timestamp
- Show origin → destination route
- List all segments with mode icons
- Display pricing breakdown
- Show discount percentage
- Highlight reservation status

**Component Structure:**
```jsx
const BundleCard = ({ bundle }) => {
  return (
    <div className="card bundle-card">
      <div className="bundle-header">
        <h4>Bundle #{bundle.bundle_id}</h4>
        <span className="bundle-status">{bundle.status}</span>
      </div>
      
      <div className="bundle-route">
        <span>{bundle.origin}</span> → <span>{bundle.destination}</span>
      </div>
      
      <div className="bundle-segments">
        {bundle.segments.map(segment => (
          <SegmentItem key={segment.id} segment={segment} />
        ))}
      </div>
      
      <div className="bundle-pricing">
        <div>Base Price: ${bundle.base_price}</div>
        <div>Discount: -{bundle.discount_percentage}%</div>
        <div><strong>Total: ${bundle.total_price}</strong></div>
      </div>
    </div>
  );
};
```

#### Task 2.3: Create BundleStats Component
**File:** `src/components/BundleStats.js`

**Features:**
- Total bundles created
- Average segments per bundle
- Total discount savings
- Bundle type distribution (2-segment, 3-segment, etc.)

---

### Phase 3: Enhance Existing Pages ✅ Ready to Implement

#### Task 3.1: Update Results.js
**File:** `src/components/Results.js`

**Add Bundle KPIs:**
```jsx
const renderBundleKPIs = () => {
  const bundleStats = metrics?.bundle_stats || {};
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px' }}>
      <KeyValue label="Total Bundles" value={bundleStats.total_bundles || 0} />
      <KeyValue label="Avg Segments/Bundle" value={bundleStats.avg_segments?.toFixed(2) || '—'} />
      <KeyValue label="Total Savings" value={bundleStats.total_savings ? `$${bundleStats.total_savings.toFixed(2)}` : '—'} />
      <KeyValue label="Bundle Match Rate" value={bundleStats.bundle_match_rate ? `${bundleStats.bundle_match_rate.toFixed(1)}%` : '—'} />
    </div>
  );
};
```

#### Task 3.2: Update SimulationControl.js
**File:** `src/components/SimulationControl.js`

**Add Bundle Toggle:**
```jsx
const [config, setConfig] = useState({
  steps: 50,
  commuters: 10,
  providers: 5,
  debug: false,
  no_plots: false,
  export_db: false,  // NEW: Database export toggle
  seed: null,
  network: 'localhost',
  rpc_url: '',
  chain_id: null
});

// Add checkbox in UI
<div className="form-group">
  <label>
    <input
      type="checkbox"
      checked={config.export_db}
      onChange={(e) => setConfig({...config, export_db: e.target.checked})}
    />
    Export to Database (enables bundle tracking)
  </label>
</div>
```

#### Task 3.3: Update Analytics.js
**File:** `src/components/Analytics.js`

**Add Bundle Charts:**
- Bundle type distribution (pie chart)
- Discount savings over time (line chart)
- Segments per bundle histogram (bar chart)

---

### Phase 4: Add New Routes ✅ Ready to Implement

#### Task 4.1: Update App.js
**File:** `src/App.js`

**Add Bundle Route:**
```jsx
import BundleVisualization from './components/BundleVisualization';

<Route 
  path="/bundles" 
  element={<BundleVisualization />} 
/>
```

#### Task 4.2: Update Header.js
**File:** `src/components/Header.js`

**Add Navigation Link:**
```jsx
<Link to="/bundles" className={location.pathname === '/bundles' ? 'active' : ''}>
  🎫 Bundles
</Link>
```

---

## 🎨 UI Design Mockup

### Bundle Card Design
```
┌─────────────────────────────────────────────┐
│ Bundle #bundle_abc123          [Reserved]   │
├─────────────────────────────────────────────┤
│ Route: [0, 0] → [5, 5]                      │
│                                             │
│ Segments:                                   │
│ 🚲 Bike    [0,0] → [2,2]    $5.00          │
│ 🚇 Train   [2,2] → [4,4]    $8.00          │
│ 🚌 Bus     [4,4] → [5,5]    $3.00          │
│                                             │
│ Base Price:        $16.00                   │
│ Discount (10%):    -$1.60                   │
│ ─────────────────────────                   │
│ Total Price:       $14.40                   │
│                                             │
│ Commuter: commuter_5                        │
│ Reserved: 2025-10-25 14:30:22              │
└─────────────────────────────────────────────┘
```

### Bundle Stats Dashboard
```
┌─────────────────────────────────────────────┐
│ Bundle Statistics                           │
├─────────────────────────────────────────────┤
│ Total Bundles:           42                 │
│ Avg Segments/Bundle:     2.3                │
│ Total Savings:           $127.50            │
│ Bundle Match Rate:       68.5%              │
└─────────────────────────────────────────────┘
```

---

## 🔧 Technical Implementation Details

### Database Connection (Backend)
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from abm.database.models import SimulationRun, Bundle, BundleSegment

# Database connection
DATABASE_URL = "postgresql://maas_user:maas_password@localhost:5432/maas_db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def query_bundles():
    session = Session()
    try:
        bundles = session.query(Bundle).order_by(Bundle.created_at.desc()).limit(50).all()
        return [bundle.to_dict() for bundle in bundles]
    finally:
        session.close()
```

### API Service (Frontend)
```javascript
// src/services/ApiService.js

export const ApiService = {
  // Existing methods...
  
  // NEW: Bundle methods
  getBundlesList: async (limit = 50, offset = 0) => {
    const response = await fetch(`${API_BASE_URL}/bundles/list?limit=${limit}&offset=${offset}`);
    return response.json();
  },
  
  getBundleStats: async () => {
    const response = await fetch(`${API_BASE_URL}/bundles/stats`);
    return response.json();
  },
  
  getBundleDetails: async (bundleId) => {
    const response = await fetch(`${API_BASE_URL}/bundles/details/${bundleId}`);
    return response.json();
  },
  
  getRecentBundles: async (limit = 10) => {
    const response = await fetch(`${API_BASE_URL}/bundles/recent?limit=${limit}`);
    return response.json();
  }
};
```

---

## 📝 Implementation Order

### Priority 1: Critical (Must Have)
1. ✅ Add backend API endpoints for bundle data
2. ✅ Create BundleVisualization component
3. ✅ Add Bundles page to router
4. ✅ Enhance Results page with bundle metrics

### Priority 2: Important (Should Have)
5. ✅ Add bundle toggle to SimulationControl
6. ✅ Test UI integration end-to-end

### Priority 3: Nice to Have (Future)
7. ⏳ Add bundle charts to Analytics
8. ⏳ Add bundle activity feed to Dashboard
9. ⏳ Add bundle filtering and search
10. ⏳ Add bundle export to CSV/JSON

---

## 🧪 Testing Plan

### Test 1: Backend API
```bash
# Start backend
cd backend
python app.py

# Test endpoints
curl http://localhost:5000/api/bundles/stats
curl http://localhost:5000/api/bundles/list
curl http://localhost:5000/api/bundles/recent
```

### Test 2: Database Integration
```bash
# Run simulation with database export
python abm/agents/run_decentralized_model.py --steps 30 --export-db

# Verify data in PostgreSQL
python examples/query_bundles.py
```

### Test 3: Frontend Integration
```bash
# Start frontend
cd ..
npm start

# Navigate to http://localhost:3000/bundles
# Verify bundle data displays correctly
```

### Test 4: End-to-End
1. Start Hardhat node: `npx hardhat node`
2. Start backend: `cd backend && python app.py`
3. Start frontend: `npm start`
4. Run simulation with `--export-db`
5. Navigate to `/bundles` page
6. Verify bundle data appears

---

## 🎯 Success Criteria

- ✅ Backend API endpoints return bundle data from PostgreSQL
- ✅ Frontend displays bundle list with segments and pricing
- ✅ Results page shows bundle-specific KPIs
- ✅ SimulationControl has database export toggle
- ✅ End-to-end test passes (simulation → database → UI)
- ✅ No errors in browser console
- ✅ No errors in backend logs

---

## 📖 Documentation Updates Needed

After implementation:
1. Update `README.md` with bundle UI features
2. Update `QUICK_START_BUNDLES.md` with UI instructions
3. Create `UI_BUNDLE_GUIDE.md` with screenshots
4. Update `MAAS_BUNDLE_SYSTEM.md` with UI section

---

**Estimated Implementation Time:** 2-3 hours  
**Complexity:** Medium  
**Dependencies:** PostgreSQL setup, simulation with --export-db  
**Status:** Ready to implement ✅

