# 🎫 Bundle Configuration Guide

## ✅ How to Run Simulations with Bundle Configuration

### 🎯 **Overview**

The MaaS platform now includes **bundle-specific configuration** that allows you to customize how multi-modal bundles are created and priced during simulations.

---

## 🚀 **Quick Start**

### **Step 1: Navigate to Bundle Page**
```
http://localhost:3000/bundles
```

### **Step 2: Switch to Scenario Builder**
Click the **"🎯 Run Scenario"** tab

### **Step 3: Configure Bundle Settings**
Scroll down to the **"🎫 Bundle Configuration"** section

### **Step 4: Customize Parameters**
- ✅ **Enable Multi-Modal Bundles** (checkbox)
- 📊 **Max Bundle Segments** (2-6)
- 💰 **Discount per Segment** (0-20%)
- 🎯 **Maximum Total Discount** (0-50%)

### **Step 5: Run Simulation**
Click **"🚀 Run Scenario"**

---

## ⚙️ **Bundle Configuration Parameters**

### **1. Enable Multi-Modal Bundles**
```
Type: Checkbox (boolean)
Default: ✅ Enabled
Purpose: Turn bundle generation on/off
```

**When Enabled:**
- Simulation will attempt to create multi-modal journeys
- Commuters can use multiple transport modes
- Bundles receive automatic discounts

**When Disabled:**
- Only single-mode trips are created
- No bundle discounts applied
- Faster simulation execution

---

### **2. Max Bundle Segments**
```
Type: Number
Range: 2-6
Default: 4
Purpose: Limit complexity of bundles
```

**Examples:**
- **2 segments**: Bike → Train
- **3 segments**: Bike → Train → Bus
- **4 segments**: Bike → Train → Bus → Car
- **5+ segments**: Complex multi-modal journeys

**Recommendations:**
- **Quick Tests**: 2-3 segments
- **Standard**: 4 segments
- **Complex Scenarios**: 5-6 segments

**Impact:**
- Higher values = More complex bundles
- Lower values = Simpler, faster matching
- More segments = Higher potential discounts

---

### **3. Discount per Segment (%)**
```
Type: Number
Range: 0-20%
Default: 5%
Purpose: Incentivize multi-modal travel
```

**How It Works:**
```
Discount = (Number of additional segments) × (Discount rate)
Capped at: Maximum Total Discount
```

**Examples with 5% rate:**
- **2 segments**: 5% discount (1 additional segment)
- **3 segments**: 10% discount (2 additional segments)
- **4 segments**: 15% discount (3 additional segments)

**Recommendations:**
- **Conservative**: 3-5% (realistic pricing)
- **Standard**: 5-7% (balanced incentive)
- **Aggressive**: 10-15% (strong incentive)

---

### **4. Maximum Total Discount (%)**
```
Type: Number
Range: 0-50%
Default: 15%
Purpose: Cap maximum discount to prevent losses
```

**Purpose:**
Prevents excessive discounts on very complex bundles

**Examples:**
```
With 5% per segment, 15% max:
- 2 segments: 5% (under cap)
- 3 segments: 10% (under cap)
- 4 segments: 15% (at cap)
- 5 segments: 15% (capped, not 20%)
- 6 segments: 15% (capped, not 25%)
```

**Recommendations:**
- **Conservative**: 10-15% (protect revenue)
- **Standard**: 15-20% (balanced)
- **Aggressive**: 25-30% (maximize adoption)

---

## 💡 **Discount Preview**

The UI shows a **real-time discount preview** based on your settings:

```
💰 Discount Preview:

2 segments:  5% discount
3 segments:  10% discount
4+ segments: 15% discount (max)
```

This updates automatically as you change the discount parameters!

---

## 📋 **Configuration Presets**

### **Quick Test (Fast)**
```yaml
Steps: 20
Commuters: 3
Providers: 2
Bundles: ✅ Enabled
Max Segments: 3
Discount Rate: 5%
Max Discount: 15%
```

### **Standard (Balanced)**
```yaml
Steps: 50
Commuters: 10
Providers: 5
Bundles: ✅ Enabled
Max Segments: 4
Discount Rate: 5%
Max Discount: 15%
```

### **Large Scale (Comprehensive)**
```yaml
Steps: 100
Commuters: 20
Providers: 10
Bundles: ✅ Enabled
Max Segments: 5
Discount Rate: 7%
Max Discount: 20%
```

---

## 🎨 **UI Features**

### **Bundle Configuration Section**
- **Location**: Below simulation parameters
- **Style**: Gradient background (light blue)
- **Border**: Purple accent
- **Collapsible**: Hides when bundles disabled

### **Discount Preview Card**
- **Real-time Updates**: Changes as you adjust settings
- **Visual Examples**: Shows 2, 3, and 4+ segment discounts
- **Gradient Design**: Purple gradient with white text
- **Clear Labels**: Easy to understand

---

## 🔧 **Technical Details**

### **Frontend State**
```javascript
const [scenarioConfig, setScenarioConfig] = useState({
  // ... other config ...
  enable_bundles: true,
  max_bundle_segments: 4,
  bundle_discount_rate: 0.05,  // 5%
  max_bundle_discount: 0.15     // 15%
});
```

### **API Request**
```json
POST /api/simulation/start
{
  "steps": 50,
  "commuters": 10,
  "providers": 5,
  "export_db": true,
  "no_plots": false,
  "enable_bundles": true,
  "max_bundle_segments": 4,
  "bundle_discount_rate": 0.05,
  "max_bundle_discount": 0.15
}
```

### **Backend Processing**
The backend will:
1. Extract bundle configuration from request
2. Pass to simulation engine
3. Apply settings during bundle creation
4. Store configuration in database

---

## 📊 **Example Scenarios**

### **Scenario 1: Conservative Pricing**
```
Goal: Test bundles with minimal discounts
Settings:
  - Enable Bundles: ✅
  - Max Segments: 3
  - Discount Rate: 3%
  - Max Discount: 10%

Result:
  - 2 segments: 3% discount
  - 3 segments: 6% discount
  - 4+ segments: 10% discount (capped)
```

### **Scenario 2: Aggressive Incentives**
```
Goal: Maximize multi-modal adoption
Settings:
  - Enable Bundles: ✅
  - Max Segments: 6
  - Discount Rate: 10%
  - Max Discount: 30%

Result:
  - 2 segments: 10% discount
  - 3 segments: 20% discount
  - 4 segments: 30% discount (capped)
  - 5+ segments: 30% discount (capped)
```

### **Scenario 3: Single-Mode Only**
```
Goal: Baseline comparison without bundles
Settings:
  - Enable Bundles: ❌
  - (Other settings ignored)

Result:
  - All trips are single-mode
  - No discounts applied
  - Faster execution
```

---

## 🎯 **Best Practices**

### **For Testing**
✅ Start with default settings (5%, 15% max)  
✅ Enable database export to see results  
✅ Use Quick Test preset for fast iteration  
✅ Compare with bundles disabled as baseline  

### **For Analysis**
✅ Run multiple scenarios with different discount rates  
✅ Export data to Excel for comparison  
✅ Track bundle adoption rates  
✅ Analyze price sensitivity  

### **For Production**
✅ Use conservative discounts (3-7%)  
✅ Cap maximum discount at 15-20%  
✅ Limit segments to 4-5 for practicality  
✅ Monitor revenue impact  

---

## 📈 **Viewing Results**

### **After Simulation Completes:**

1. **Switch to Bundle View**
   - Click "📊 View Bundles" tab

2. **See Bundle Descriptions**
   - Each bundle shows transport modes
   - Discount amount displayed
   - Duration and price visible

3. **Filter and Sort**
   - Filter by transport mode
   - Sort by price, segments, or discount
   - Click for detailed view

4. **Export Data**
   - Go to Database page
   - Select "Bundles" table
   - Export to Excel/CSV

---

## 🔍 **Troubleshooting**

### **No bundles created?**
✅ Ensure "Enable Multi-Modal Bundles" is checked  
✅ Increase number of providers (5+)  
✅ Run more steps (50+)  
✅ Check database export is enabled  

### **All bundles have same discount?**
✅ Check if hitting maximum discount cap  
✅ Increase max discount percentage  
✅ Verify discount rate is set correctly  

### **Discounts too high/low?**
✅ Adjust "Discount per Segment" rate  
✅ Modify "Maximum Total Discount" cap  
✅ Check discount preview before running  

---

## ✨ **Summary**

Bundle configuration allows you to:

✅ **Enable/Disable** multi-modal bundles  
✅ **Control Complexity** with max segments  
✅ **Set Pricing** with discount rates  
✅ **Cap Discounts** to protect revenue  
✅ **Preview Results** before running  
✅ **Compare Scenarios** with different settings  

**The bundle configuration is now part of the simulation setup!** 🎉

Navigate to http://localhost:3000/bundles, click "Run Scenario", and scroll down to see the bundle configuration section!

---

## 📖 **Next Steps**

1. **Try Default Settings**
   - Run a simulation with default bundle config
   - View generated bundles
   - Check discount amounts

2. **Experiment with Settings**
   - Try different discount rates
   - Adjust max segments
   - Compare results

3. **Analyze Data**
   - Export to Excel
   - Compare scenarios
   - Optimize pricing

**Enjoy your configurable bundle system!** 🚀

