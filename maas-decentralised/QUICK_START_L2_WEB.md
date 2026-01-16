# 🚀 Quick Start: L2 Blockchain in Web App

## ✅ What You Need to Do

### Option 1: Run on Localhost (Easiest - No Setup)

**Step 1:** Start services
```bash
# Terminal 1
npx hardhat node

# Terminal 2
python backend/app.py

# Terminal 3
npm start
```

**Step 2:** Open browser
- Go to: http://localhost:3000

**Step 3:** Start simulation
- Keep network as **"Localhost (Hardhat)"**
- Click **"Start Simulation"**

✅ **Done!** No blockchain setup needed.

---

### Option 2: Run on L2 Network (Optimism/Base/Arbitrum)

**Step 1:** Get testnet ETH
- Optimism Sepolia: https://app.optimism.io/faucet
- Base Sepolia: https://www.coinbase.com/faucets/base-ethereum-goerli-faucet
- Arbitrum Sepolia: https://faucet.quicknode.com/arbitrum/sepolia

**Step 2:** Deploy contracts to L2
```bash
# Add your private key to .env
echo "PRIVATE_KEY=your_private_key_here" > .env

# Deploy to Optimism Sepolia (example)
npx hardhat run scripts/deploy.js --network optimism-sepolia

# Update blockchain_config.json with deployed addresses
```

**Step 3:** Start web app
```bash
# Terminal 1 - Backend
python backend/app.py

# Terminal 2 - Frontend
npm start
```

**Step 4:** Open browser and select network
- Go to: http://localhost:3000
- Scroll to **"⛓️ Blockchain Network"** section
- Select **"Optimism Sepolia"** (or Base/Arbitrum)
- (Optional) Enter custom RPC URL
- Click **"Start Simulation"**

✅ **Done!** Simulation runs on real L2 blockchain.

---

## 🎯 What You'll See in the Web App

### New UI Section: "⛓️ Blockchain Network"

Located in the **Simulation Control** page, you'll see:

```
⛓️ Blockchain Network
┌─────────────────────────────────────────┐
│ Network: [Dropdown Menu ▼]             │
│   • Localhost (Hardhat)                 │
│   • Optimism Sepolia (L2 Testnet)      │
│   • Base Sepolia (L2 Testnet)          │
│   • Arbitrum Sepolia (L2 Testnet)      │
└─────────────────────────────────────────┘

Custom RPC URL (optional):
┌─────────────────────────────────────────┐
│ https://opt-sepolia.g.alchemy.com/...  │
└─────────────────────────────────────────┘

⚠️ L2 Network Requirements:
• Ensure you have testnet ETH on the selected L2
• Transactions will be slower than localhost
• Smart contracts must be deployed on the network
```

---

## 📊 Network Comparison

| Feature | Localhost | Optimism | Base | Arbitrum |
|---------|-----------|----------|------|----------|
| **Setup** | ✅ None | 🔧 Deploy + ETH | 🔧 Deploy + ETH | 🔧 Deploy + ETH |
| **Speed** | ⚡ Instant | 🐢 ~2s | 🐢 ~2s | 🚀 ~0.25s |
| **Cost** | 💚 Free | 💛 Testnet ETH | 💛 Testnet ETH | 💛 Testnet ETH |
| **Real Blockchain** | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes |
| **Best For** | Testing | Demos | Demos | Production |

---

## 🔧 Prerequisites for L2 (One-Time Setup)

### 1. Configure Hardhat Networks

Add to `hardhat.config.js`:

```javascript
require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

module.exports = {
  solidity: "0.8.20",
  networks: {
    "optimism-sepolia": {
      url: "https://sepolia.optimism.io",
      chainId: 11155420,
      accounts: [process.env.PRIVATE_KEY]
    },
    "base-sepolia": {
      url: "https://sepolia.base.org",
      chainId: 84532,
      accounts: [process.env.PRIVATE_KEY]
    },
    "arbitrum-sepolia": {
      url: "https://sepolia-rollup.arbitrum.io/rpc",
      chainId: 421614,
      accounts: [process.env.PRIVATE_KEY]
    }
  }
};
```

### 2. Create .env File

```bash
PRIVATE_KEY=your_private_key_without_0x_prefix
```

### 3. Deploy Contracts

```bash
# Deploy to Optimism Sepolia
npx hardhat run scripts/deploy.js --network optimism-sepolia

# Deploy to Base Sepolia
npx hardhat run scripts/deploy.js --network base-sepolia

# Deploy to Arbitrum Sepolia
npx hardhat run scripts/deploy.js --network arbitrum-sepolia
```

### 4. Update blockchain_config.json

After deployment, update with contract addresses:

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

---

## 💡 Pro Tips

### Use Custom RPC for Better Performance

Instead of public endpoints, use:

**Alchemy (Recommended):**
1. Sign up: https://www.alchemy.com/
2. Create app for your network
3. Copy HTTPS endpoint
4. Paste in web app's "Custom RPC URL" field

**Example:**
```
https://opt-sepolia.g.alchemy.com/v2/YOUR_API_KEY
```

### Monitor Transactions

View your transactions on block explorers:
- **Optimism Sepolia:** https://sepolia-optimism.etherscan.io/
- **Base Sepolia:** https://sepolia.basescan.org/
- **Arbitrum Sepolia:** https://sepolia.arbiscan.io/

### Reduce Simulation Time on L2

For faster L2 simulations:
- Use fewer steps (20-30 instead of 50-100)
- Use fewer agents (5 commuters, 3 providers)
- Use Arbitrum Sepolia (fastest L2)
- Use custom RPC endpoint (Alchemy/Infura)

---

## 🐛 Common Issues

### "Connection refused"
- Check internet connection
- Verify RPC URL is correct
- Try custom RPC endpoint

### "Insufficient funds"
- Get testnet ETH from faucets
- Check you're on the right network
- Verify wallet has ETH

### "Contract not deployed"
- Deploy contracts to L2 first
- Update blockchain_config.json
- Verify addresses are correct

### Simulation very slow
- Use Arbitrum (fastest L2)
- Reduce simulation size
- Use custom RPC endpoint
- Switch to localhost for testing

---

## 📖 Full Documentation

For complete details, see: **L2_WEB_APP_GUIDE.md**

---

## 🎉 Summary

**You can now run simulations on L2 blockchains directly from the web interface!**

**No command-line needed** - just:
1. ✅ Refresh browser
2. ✅ Select network from dropdown
3. ✅ Click "Start Simulation"

**That's it!** 🚀

