# 🚀 How to Run Bundle Simulation and Populate Database

## ❓ Why Database Shows Zero Values?

The database is empty because **no simulation has been run yet** with database export enabled.

---

## ✅ **Step-by-Step Guide to Populate Database**

### **Step 1: Navigate to Bundle Page**
```
Current page: http://localhost:3000/bundles
```

### **Step 2: Switch to Scenario Builder**
1. Click the **"🎯 Run Scenario"** tab at the top
2. You should see the scenario configuration form

### **Step 3: Configure Your Simulation**

#### **Basic Parameters:**
- **Scenario Name**: "My First Bundle Test" (or any name)
- **Simulation Steps**: 50 (recommended for good data)
- **Number of Commuters**: 10 (travelers requesting trips)
- **Number of Providers**: 5 (transport services)

#### **Important Checkboxes:**
- ✅ **Export to Database** - **MUST BE CHECKED!** (This saves data to database)
- ✅ **Skip Plot Generation** - Check for faster execution
- ✅ **Enable Multi-Modal Bundles** - Check to create bundles

#### **Bundle Configuration:**
- **Max Bundle Segments**: 4 (default is fine)
- **Discount per Segment**: 5% (default is fine)
- **Maximum Total Discount**: 15% (default is fine)

### **Step 4: Run the Simulation**
1. Click the **"🚀 Run Scenario"** button
2. Wait for the simulation to complete (progress bar will show)
3. You'll see "Simulation completed successfully!" when done

### **Step 5: View Results**
1. Click **"📊 View Bundles"** tab
2. You should now see bundles with data!
3. Go to **Database** page to see all exported data

---

## 🎯 **Quick Test (Fastest Way)**

### **Use the Quick Test Preset:**

1. Go to **"🎯 Run Scenario"** tab
2. Scroll down to **"📋 Quick Presets"**
3. Click **"⚡ Quick Test"** button
4. **IMPORTANT**: Make sure **"Export to Database"** is checked ✅
5. Click **"🚀 Run Scenario"**
6. Wait ~30 seconds for completion

This will run a fast simulation (20 steps, 3 commuters, 2 providers) and populate the database!

---

## 📊 **What Gets Saved to Database**

When you run a simulation with **"Export to Database"** enabled:

### **Tables Populated:**
1. **runs** - Simulation run metadata
2. **ticks** - Each time step data
3. **commuters** - Traveler agents
4. **providers** - Transport service providers
5. **requests** - Travel requests from commuters
6. **bundles** - Multi-modal journey bundles (with descriptions!)
7. **bundle_segments** - Individual legs of each bundle
8. **reservations** - Confirmed bookings
9. **segment_reservations** - Segment-level reservations

---

## 🔍 **Troubleshooting**

### **Problem: "Export to Database" is not checked**
**Solution:** 
- Go to "Run Scenario" tab
- Find the checkbox labeled "Export to Database"
- Make sure it's checked ✅
- Run simulation again

### **Problem: Simulation runs but no bundles created**
**Solution:**
- Increase number of providers to 5+
- Increase number of commuters to 10+
- Run more steps (50+)
- Make sure "Enable Multi-Modal Bundles" is checked

### **Problem: Database still shows zeros after simulation**
**Solution:**
- Check if simulation completed successfully
- Look for error messages in the simulation output
- Make sure "Export to Database" was checked before running
- Try running again with Quick Test preset

### **Problem: Simulation takes too long**
**Solution:**
- Enable "Skip Plot Generation" checkbox
- Reduce number of steps to 20-30
- Use fewer commuters and providers
- Use "Quick Test" preset

---

## 💡 **Recommended First Run**

### **Configuration:**
```yaml
Scenario Name: "First Bundle Test"
Steps: 50
Commuters: 10
Providers: 5
Export to Database: ✅ CHECKED
Skip Plot Generation: ✅ CHECKED
Enable Multi-Modal Bundles: ✅ CHECKED
Max Bundle Segments: 4
Discount per Segment: 5%
Maximum Total Discount: 15%
```

### **Expected Results:**
- Simulation runs for ~1-2 minutes
- Creates 10+ bundles
- Populates all database tables
- Shows bundle descriptions
- Displays discount information

---

## 📋 **After Simulation Completes**

### **1. View Bundles**
- Click "📊 View Bundles" tab
- See all created bundles with:
  - Bundle descriptions (e.g., "🚲 Bike → 🚆 Train → 🚌 Bus")
  - Pricing and discounts
  - Number of segments
  - Transport modes

### **2. Check Database**
- Go to http://localhost:3000/database
- Click through different tables:
  - **Runs**: See your simulation run
  - **Bundles**: See all bundles with descriptions
  - **Commuters**: See traveler data
  - **Providers**: See transport services
  - **Requests**: See travel requests

### **3. Export Data**
- On Database page, select a table
- Click "Export to Excel" or "Export to CSV"
- Download and analyze the data

---

## 🎨 **Visual Guide**

### **Before Running Simulation:**
```
Database Stats:
├─ Total Bundles: 0
├─ Total Commuters: 0
├─ Total Providers: 0
└─ Total Requests: 0
```

### **After Running Simulation:**
```
Database Stats:
├─ Total Bundles: 15
├─ Total Commuters: 10
├─ Total Providers: 5
└─ Total Requests: 25
```

---

## ⚙️ **Current System Status**

```
✅ Frontend: Running (http://localhost:3000)
✅ Backend: Running (http://localhost:5000)
✅ Hardhat Node: Running (http://localhost:8545)
✅ Database: Ready (maas_bundles.db)
✅ Bundle System: Configured with descriptions
✅ Help System: Available (click ❓ Help button)
```

**Everything is ready! You just need to run a simulation.**

---

## 🚀 **Quick Action Steps**

### **Right Now:**

1. **Click "🎯 Run Scenario" tab** (if not already there)

2. **Verify "Export to Database" is checked** ✅

3. **Click "⚡ Quick Test" preset button**

4. **Click "🚀 Run Scenario"**

5. **Wait for completion** (~30 seconds)

6. **Click "📊 View Bundles"** to see results!

---

## 📖 **Additional Resources**

- **Bundle Configuration Guide**: `BUNDLE_CONFIGURATION_GUIDE.md`
- **Bundle Descriptions**: `BUNDLE_DESCRIPTIONS_ADDED.md`
- **Help System**: `BUNDLE_HELP_SYSTEM_ADDED.md`
- **UI Enhancements**: `UI_ENHANCEMENTS_COMPLETE.md`

---

## ✨ **Summary**

**Why database is empty:**
- No simulation has been run with database export enabled

**How to fix:**
1. Go to "Run Scenario" tab
2. Check "Export to Database" ✅
3. Click "Quick Test" preset
4. Click "Run Scenario"
5. Wait for completion
6. View results in "View Bundles" tab

**That's it!** The database will be populated with all simulation data including bundles with descriptions! 🎉

---

## 🎯 **Next Steps After First Run**

1. **Experiment with different configurations**
   - Try different discount rates
   - Adjust max segments
   - Vary commuter/provider counts

2. **Compare scenarios**
   - Run with bundles enabled vs disabled
   - Test different discount strategies
   - Analyze pricing impact

3. **Export and analyze**
   - Download Excel files
   - Compare bundle adoption rates
   - Study pricing patterns

**Ready to run your first simulation?** Click "Run Scenario" tab and let's go! 🚀

