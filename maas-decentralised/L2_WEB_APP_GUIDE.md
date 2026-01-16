# 🌐 Running Web Application on L2 Blockchain Networks

## ✅ What's New

Your web application now supports running simulations on **Layer 2 (L2) blockchain networks**!

### Supported Networks:
- 🏠 **Localhost** - Hardhat local node (default)
- 🌐 **Optimism Sepolia** - L2 testnet (~2s block time)
- 🌐 **Base Sepolia** - L2 testnet (~2s block time)
- 🌐 **Arbitrum Sepolia** - L2 testnet (~0.25s block time)

---

## 🚀 How to Use L2 Networks in Web App

### Step 1: Start the Web Application

**Terminal 1 - Start Hardhat (for localhost only):**
```bash
npx hardhat node
```

**Terminal 2 - Start Backend:**
```bash
python backend/app.py
```

**Terminal 3 - Start Frontend:**
```bash
npm start
```

### Step 2: Open Browser

Navigate to: **http://localhost:3000**

### Step 3: Select Blockchain Network

In the **Simulation Control** page:

1. Scroll down to the **"⛓️ Blockchain Network"** section
2. Select your desired network from the dropdown:
   - **Localhost (Hardhat)** - For local testing
   - **Optimism Sepolia** - For L2 testnet
   - **Base Sepolia** - For L2 testnet
   - **Arbitrum Sepolia** - For L2 testnet

3. (Optional) Enter a custom RPC URL if you have your own endpoint

4. Click **"Start Simulation"**

---

## 📋 Prerequisites for L2 Networks

### 1. Deploy Smart Contracts on L2

Before running on L2, you need to deploy your smart contracts to the selected network.

**Example: Deploy to Optimism Sepolia**

```bash
# Set your private key in .env file
echo "PRIVATE_KEY=your_private_key_here" > .env

# Deploy to Optimism Sepolia
npx hardhat run scripts/deploy.js --network optimism-sepolia
```

**Update `blockchain_config.json` with deployed addresses:**
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

### 2. Get Testnet ETH

You need testnet ETH on the L2 network to pay for gas fees.

**Optimism Sepolia:**
- Faucet: https://app.optimism.io/faucet
- Bridge from Sepolia: https://app.optimism.io/bridge

**Base Sepolia:**
- Faucet: https://www.coinbase.com/faucets/base-ethereum-goerli-faucet
- Bridge from Sepolia: https://bridge.base.org

**Arbitrum Sepolia:**
- Faucet: https://faucet.quicknode.com/arbitrum/sepolia
- Bridge from Sepolia: https://bridge.arbitrum.io

### 3. Configure Hardhat Networks (Optional)

Add L2 networks to your `hardhat.config.js`:

```javascript
module.exports = {
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

---

## 🎯 Quick Start Examples

### Example 1: Run on Localhost (Default)

1. Start Hardhat: `npx hardhat node`
2. Open web app: http://localhost:3000
3. Keep network as **"Localhost (Hardhat)"**
4. Click **"Start Simulation"**

✅ **Fast, instant transactions, no testnet ETH needed**

---

### Example 2: Run on Optimism Sepolia

1. Deploy contracts to Optimism Sepolia (see Prerequisites)
2. Get testnet ETH from faucet
3. Open web app: http://localhost:3000
4. Select **"Optimism Sepolia (L2 Testnet)"** from network dropdown
5. (Optional) Enter custom RPC URL if you have Alchemy/Infura key
6. Click **"Start Simulation"**

✅ **Real L2 blockchain, ~2s block time, requires testnet ETH**

---

### Example 3: Run on Arbitrum Sepolia (Fastest L2)

1. Deploy contracts to Arbitrum Sepolia
2. Get testnet ETH from faucet
3. Open web app: http://localhost:3000
4. Select **"Arbitrum Sepolia (L2 Testnet)"** from network dropdown
5. Click **"Start Simulation"**

✅ **Fastest L2 (~0.25s block time), requires testnet ETH**

---

## 🔧 Custom RPC Endpoints

For better performance and reliability, use your own RPC endpoints:

### Alchemy (Recommended)
1. Sign up at https://www.alchemy.com/
2. Create an app for your desired network
3. Copy the HTTPS endpoint
4. Paste in the "Custom RPC URL" field

**Example:**
```
https://opt-sepolia.g.alchemy.com/v2/YOUR_API_KEY
```

### Infura
1. Sign up at https://infura.io/
2. Create a project
3. Copy the endpoint for your network
4. Paste in the "Custom RPC URL" field

**Example:**
```
https://optimism-sepolia.infura.io/v3/YOUR_PROJECT_ID
```

---

## ⚠️ Important Notes

### Performance Differences

| Network | Block Time | Transaction Speed | Cost |
|---------|-----------|-------------------|------|
| **Localhost** | Instant | ⚡ Instant | Free |
| **Optimism Sepolia** | ~2s | 🐢 Slower | Testnet ETH |
| **Base Sepolia** | ~2s | 🐢 Slower | Testnet ETH |
| **Arbitrum Sepolia** | ~0.25s | 🚀 Fast | Testnet ETH |

### Simulation Duration

- **Localhost**: 50 steps ≈ 1-2 minutes
- **L2 Networks**: 50 steps ≈ 3-5 minutes (due to block confirmation times)

### Recommendations

✅ **Use Localhost for:**
- Development and testing
- Quick iterations
- Large simulations (100+ steps)

✅ **Use L2 Networks for:**
- Production demonstrations
- Research paper validation
- Real blockchain verification
- Multi-party scenarios

---

## 🐛 Troubleshooting

### Issue: "Connection refused" on L2

**Solution:**
- Check your internet connection
- Verify the RPC URL is correct
- Try using a custom RPC endpoint (Alchemy/Infura)

### Issue: "Insufficient funds for gas"

**Solution:**
- Get testnet ETH from faucets (see Prerequisites)
- Ensure you have enough ETH for all transactions
- Reduce simulation size (fewer steps/agents)

### Issue: "Contract not deployed"

**Solution:**
- Deploy contracts to the selected L2 network first
- Update `blockchain_config.json` with correct addresses
- Verify deployment with: `npx hardhat verify --network <network> <address>`

### Issue: Simulation is very slow

**Solution:**
- Use Arbitrum Sepolia (fastest L2)
- Use a custom RPC endpoint (Alchemy/Infura)
- Reduce simulation size
- Switch to localhost for faster testing

---

## 📊 Monitoring L2 Transactions

### Block Explorers

**Optimism Sepolia:**
https://sepolia-optimism.etherscan.io/

**Base Sepolia:**
https://sepolia.basescan.org/

**Arbitrum Sepolia:**
https://sepolia.arbiscan.io/

You can view all your simulation transactions on these explorers!

---

## 🎉 Summary

You can now run your MaaS simulation on real L2 blockchain networks directly from the web interface!

**Steps:**
1. ✅ Start web application (backend + frontend)
2. ✅ Select blockchain network from dropdown
3. ✅ (Optional) Enter custom RPC URL
4. ✅ Click "Start Simulation"
5. ✅ View results and blockchain transactions

**No command-line needed!** Everything is controlled through the web UI.

