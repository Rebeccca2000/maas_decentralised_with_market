// scripts/simple-blockchain-check.js
// Simple check of blockchain state

const { ethers } = require("hardhat");
const fs = require("fs");

async function main() {
  console.log("🔍 SIMPLE BLOCKCHAIN CHECK");
  console.log("============================================================");

  // Get current block number
  const currentBlock = await ethers.provider.getBlockNumber();
  console.log(`Current block: ${currentBlock}`);

  // Get account balances
  const accounts = await ethers.getSigners();
  console.log(`API Account: ${accounts[0].address}`);
  const balance = await ethers.provider.getBalance(accounts[0].address);
  console.log(`API Balance: ${ethers.utils.formatEther(balance)} ETH`);
  console.log("");

  // Load deployment info
  const deploymentInfo = JSON.parse(fs.readFileSync("deployed/simplified.json", "utf8"));
  
  // Get contract instances
  const facade = await ethers.getContractAt("MaaSFacade", deploymentInfo.Facade);
  const registry = await ethers.getContractAt("MaaSRegistry", deploymentInfo.Registry);
  const request = await ethers.getContractAt("MaaSRequest", deploymentInfo.Request);
  const auction = await ethers.getContractAt("MaaSAuction", deploymentInfo.Auction);

  console.log("📋 Contract Addresses:");
  console.log(`Facade: ${facade.address}`);
  console.log(`Registry: ${registry.address}`);
  console.log(`Request: ${request.address}`);
  console.log(`Auction: ${auction.address}`);
  console.log("");

  // Check if contracts are deployed properly
  try {
    const code = await ethers.provider.getCode(facade.address);
    console.log(`Facade contract code length: ${code.length} characters`);
    
    if (code === "0x") {
      console.log("❌ Facade contract not deployed!");
      return;
    } else {
      console.log("✅ Facade contract is deployed");
    }
  } catch (e) {
    console.log(`❌ Error checking facade: ${e.message}`);
    return;
  }

  // Try to call a simple read function
  try {
    // Check if we can call the registry through facade
    console.log("\n🔍 Testing contract calls:");
    
    // Try to get commuter 0
    try {
      const commuter0 = await registry.getCommuter(0);
      console.log(`Commuter 0 address: ${commuter0}`);
      if (commuter0 !== "0x0000000000000000000000000000000000000000") {
        console.log("✅ Found registered commuter 0!");
      } else {
        console.log("❌ Commuter 0 not registered");
      }
    } catch (e) {
      console.log(`❌ Error getting commuter 0: ${e.message}`);
    }

    // Try to get provider 100
    try {
      const [providerAddr, mode] = await registry.getProvider(100);
      console.log(`Provider 100 address: ${providerAddr}, mode: ${mode}`);
      if (providerAddr !== "0x0000000000000000000000000000000000000000") {
        console.log("✅ Found registered provider 100!");
      } else {
        console.log("❌ Provider 100 not registered");
      }
    } catch (e) {
      console.log(`❌ Error getting provider 100: ${e.message}`);
    }

    // Check recent events
    console.log("\n📡 Checking recent events:");
    const fromBlock = Math.max(0, currentBlock - 50);
    
    try {
      const commuterEvents = await registry.queryFilter(
        registry.filters.CommuterRegistered(),
        fromBlock,
        currentBlock
      );
      console.log(`Found ${commuterEvents.length} commuter registration events`);
      
      if (commuterEvents.length > 0) {
        console.log("Recent commuter registrations:");
        commuterEvents.slice(-3).forEach((event, i) => {
          console.log(`  ${i+1}. Commuter ${event.args.commuterId} -> ${event.args.commuter}`);
        });
      }
    } catch (e) {
      console.log(`❌ Error getting commuter events: ${e.message}`);
    }

    try {
      const providerEvents = await registry.queryFilter(
        registry.filters.ProviderRegistered(),
        fromBlock,
        currentBlock
      );
      console.log(`Found ${providerEvents.length} provider registration events`);
      
      if (providerEvents.length > 0) {
        console.log("Recent provider registrations:");
        providerEvents.slice(-3).forEach((event, i) => {
          console.log(`  ${i+1}. Provider ${event.args.providerId} -> ${event.args.provider} (mode: ${event.args.mode})`);
        });
      }
    } catch (e) {
      console.log(`❌ Error getting provider events: ${e.message}`);
    }

    try {
      const requestEvents = await request.queryFilter(
        request.filters.RequestCreated(),
        fromBlock,
        currentBlock
      );
      console.log(`Found ${requestEvents.length} request creation events`);
      
      if (requestEvents.length > 0) {
        console.log("Recent requests:");
        requestEvents.slice(-3).forEach((event, i) => {
          console.log(`  ${i+1}. Request ${event.args.requestId} by commuter ${event.args.commuter}`);
        });
      }
    } catch (e) {
      console.log(`❌ Error getting request events: ${e.message}`);
    }

  } catch (e) {
    console.log(`❌ Error testing contracts: ${e.message}`);
  }

  console.log("\n🎯 CHECK COMPLETE!");
  console.log("============================================================");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("Check failed:", error);
    process.exit(1);
  });
