# 📖 Step-by-Step: Connect to L2 Blockchain

## 🎯 Choose Your Path

### Path A: Localhost (5 minutes - Easiest)
### Path B: L2 Network (30 minutes - Real Blockchain)

---

# 🏠 PATH A: LOCALHOST (RECOMMENDED FOR BEGINNERS)

## ✅ Prerequisites
- Node.js installed
- Hardhat installed (`npm install --save-dev hardhat`)

## 📝 Steps

### Step 1: Start Hardhat Node
Open a terminal and run:
```bash
npx hardhat node
```

**Expected output:**
```
Started HTTP and WebSocket JSON-RPC server at http://127.0.0.1:8545/

Accounts
========
Account #0: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266 (10000 ETH)
...
```

✅ **Keep this terminal open!**

---

### Step 2: Start Backend
Open a **new terminal** and run:
```bash
python backend/app.py
```

**Expected output:**
```
INFO:MarketplaceAPI:Connected to blockchain: True
 * Running on http://127.0.0.1:5000
```

✅ **Keep this terminal open!**

---

### Step 3: Start Frontend
Open a **new terminal** and run:
```bash
npm start
```

**Expected output:**
```
Compiled successfully!

You can now view maas-frontend in the browser.

  Local:            http://localhost:3000
```

✅ **Browser should open automatically**

---

### Step 4: Configure Simulation
In the browser at http://localhost:3000:

1. You'll see the **Simulation Control** page
2. Scroll down to **"⛓️ Blockchain Network"** section
3. **Network should already be set to "Localhost (Hardhat)"** ✅
4. You'll see a green box: "✅ Localhost Mode - Ready to Go!"

---

### Step 5: Start Simulation
1. Configure your simulation parameters (or use defaults)
2. Click **"Start Simulation"** button
3. Watch the progress bar
4. View results when complete!

---

## 🎉 Done!
You're running on localhost blockchain. No testnet ETH needed, instant transactions!

---

# 🌐 PATH B: L2 NETWORK (ADVANCED)

## ✅ Prerequisites
- Node.js installed
- Hardhat installed
- MetaMask or similar wallet
- Basic understanding of blockchain

---

## 📝 Part 1: Get Testnet ETH (10 minutes)

### Option 1: Optimism Sepolia

**Step 1:** Get Sepolia ETH first
- Go to: https://sepoliafaucet.com/
- Enter your wallet address
- Wait for ETH to arrive (~1 minute)

**Step 2:** Bridge to Optimism Sepolia
- Go to: https://app.optimism.io/bridge
- Connect wallet
- Bridge Sepolia ETH to Optimism Sepolia
- Wait for bridge (~5 minutes)

**Alternative:** Direct faucet
- Go to: https://app.optimism.io/faucet
- Connect wallet
- Request testnet ETH

---

### Option 2: Base Sepolia

**Step 1:** Get Sepolia ETH
- Go to: https://sepoliafaucet.com/
- Enter your wallet address

**Step 2:** Bridge to Base Sepolia
- Go to: https://bridge.base.org/
- Connect wallet
- Bridge Sepolia ETH to Base Sepolia

**Alternative:** Direct faucet
- Go to: https://www.coinbase.com/faucets/base-ethereum-goerli-faucet

---

### Option 3: Arbitrum Sepolia (Recommended - Fastest)

**Step 1:** Get Sepolia ETH
- Go to: https://sepoliafaucet.com/

**Step 2:** Bridge to Arbitrum Sepolia
- Go to: https://bridge.arbitrum.io/
- Connect wallet
- Bridge Sepolia ETH to Arbitrum Sepolia

**Alternative:** Direct faucet
- Go to: https://faucet.quicknode.com/arbitrum/sepolia

---

## 📝 Part 2: Configure Hardhat (5 minutes)

### Step 1: Create .env File
In your project root, create a file named `.env`:

```bash
PRIVATE_KEY=your_private_key_without_0x_prefix
```

**How to get your private key:**
1. Open MetaMask
2. Click three dots → Account Details
3. Click "Export Private Key"
4. Enter password
5. Copy the key (without 0x prefix)

⚠️ **NEVER share this key or commit it to Git!**

---

### Step 2: Update hardhat.config.js

Add this to your `hardhat.config.js`:

```javascript
require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

module.exports = {
  solidity: "0.8.20",
  networks: {
    hardhat: {
      chainId: 31337
    },
    "optimism-sepolia": {
      url: "https://sepolia.optimism.io",
      chainId: 11155420,
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : []
    },
    "base-sepolia": {
      url: "https://sepolia.base.org",
      chainId: 84532,
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : []
    },
    "arbitrum-sepolia": {
      url: "https://sepolia-rollup.arbitrum.io/rpc",
      chainId: 421614,
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : []
    }
  }
};
```

---

## 📝 Part 3: Deploy Contracts (10 minutes)

### Step 1: Deploy to Your Chosen Network

**For Optimism Sepolia:**
```bash
npx hardhat run scripts/deploy.js --network optimism-sepolia
```

**For Base Sepolia:**
```bash
npx hardhat run scripts/deploy.js --network base-sepolia
```

**For Arbitrum Sepolia:**
```bash
npx hardhat run scripts/deploy.js --network arbitrum-sepolia
```

**Expected output:**
```
Deploying contracts...
MaaSRegistry deployed to: 0x1234...
MaaSRequest deployed to: 0x5678...
MaaSAuction deployed to: 0x9abc...
MaaSFacade deployed to: 0xdef0...
```

✅ **Copy these addresses!**

---

### Step 2: Update blockchain_config.json

Edit `blockchain_config.json` with your deployed addresses:

**For Optimism Sepolia:**
```json
{
  "rpc_url": "https://sepolia.optimism.io",
  "chain_id": 11155420,
  "contracts": {
    "registry": "0xYourRegistryAddress",
    "request": "0xYourRequestAddress",
    "auction": "0xYourAuctionAddress",
    "facade": "0xYourFacadeAddress"
  }
}
```

**For Base Sepolia:**
```json
{
  "rpc_url": "https://sepolia.base.org",
  "chain_id": 84532,
  "contracts": {
    "registry": "0xYourRegistryAddress",
    "request": "0xYourRequestAddress",
    "auction": "0xYourAuctionAddress",
    "facade": "0xYourFacadeAddress"
  }
}
```

**For Arbitrum Sepolia:**
```json
{
  "rpc_url": "https://sepolia-rollup.arbitrum.io/rpc",
  "chain_id": 421614,
  "contracts": {
    "registry": "0xYourRegistryAddress",
    "request": "0xYourRequestAddress",
    "auction": "0xYourAuctionAddress",
    "facade": "0xYourFacadeAddress"
  }
}
```

---

## 📝 Part 4: Get Custom RPC (Optional - 5 minutes)

### Option 1: Alchemy (Recommended)

**Step 1:** Sign up
- Go to: https://www.alchemy.com/
- Create free account

**Step 2:** Create app
- Click "Create App"
- Choose your network (Optimism Sepolia, Base Sepolia, or Arbitrum Sepolia)
- Name it (e.g., "MaaS Simulation")

**Step 3:** Get endpoint
- Click on your app
- Click "View Key"
- Copy the HTTPS endpoint

**Example:**
```
https://opt-sepolia.g.alchemy.com/v2/abc123def456
```

---

### Option 2: Infura

**Step 1:** Sign up
- Go to: https://infura.io/
- Create free account

**Step 2:** Create project
- Click "Create New Project"
- Choose "Web3 API"
- Name it

**Step 3:** Get endpoint
- Select your network from dropdown
- Copy the HTTPS endpoint

---

## 📝 Part 5: Run Simulation on L2

### Step 1: Start Backend
```bash
python backend/app.py
```

### Step 2: Start Frontend
```bash
npm start
```

### Step 3: Configure in Browser
1. Go to: http://localhost:3000
2. Click **"❓ Show Help"** button to see instructions
3. Scroll to **"⛓️ Blockchain Network"** section
4. Select your network from dropdown:
   - Optimism Sepolia
   - Base Sepolia
   - Arbitrum Sepolia

### Step 4: Add Custom RPC (Optional)
- Paste your Alchemy/Infura endpoint in "Custom RPC URL" field
- This improves performance and reliability

### Step 5: Start Simulation
- Click **"Start Simulation"**
- Wait for completion (~3-5 minutes for 50 steps)
- View results!

---

## 🎉 Success!

You're now running on a real L2 blockchain! 

### Verify Your Transactions

**Optimism Sepolia:**
https://sepolia-optimism.etherscan.io/

**Base Sepolia:**
https://sepolia.basescan.org/

**Arbitrum Sepolia:**
https://sepolia.arbiscan.io/

Search for your wallet address to see all transactions!

---

## 🐛 Troubleshooting

### "Insufficient funds for gas"
- Get more testnet ETH from faucets
- Check you're on the correct network in MetaMask

### "Contract not deployed"
- Verify deployment was successful
- Check blockchain_config.json has correct addresses
- Verify on block explorer

### "Connection refused"
- Check internet connection
- Verify RPC URL is correct
- Try using custom RPC (Alchemy/Infura)

### Simulation very slow
- Use Arbitrum Sepolia (fastest)
- Add custom RPC endpoint
- Reduce simulation size (fewer steps)

---

## 📚 Additional Resources

- **Full Guide:** `L2_WEB_APP_GUIDE.md`
- **Quick Reference:** `QUICK_START_L2_WEB.md`
- **Hardhat Docs:** https://hardhat.org/docs
- **Optimism Docs:** https://docs.optimism.io/
- **Base Docs:** https://docs.base.org/
- **Arbitrum Docs:** https://docs.arbitrum.io/

