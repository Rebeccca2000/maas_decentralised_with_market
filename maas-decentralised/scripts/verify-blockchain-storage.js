// scripts/verify-blockchain-storage.js
// Verify what data is actually stored on the blockchain

const { ethers } = require("hardhat");
const fs = require("fs");

async function main() {
  console.log("🔍 VERIFYING BLOCKCHAIN STORAGE");
  console.log("============================================================");

  // Load deployment info
  const deploymentInfo = JSON.parse(fs.readFileSync("deployed/simplified.json", "utf8"));
  
  // Get contract instances
  const registry = await ethers.getContractAt("MaaSRegistry", deploymentInfo.Registry);
  const request = await ethers.getContractAt("MaaSRequest", deploymentInfo.Request);
  const auction = await ethers.getContractAt("MaaSAuction", deploymentInfo.Auction);
  const facade = await ethers.getContractAt("MaaSFacade", deploymentInfo.Facade);

  console.log("📋 Contract Addresses:");
  console.log(`Registry: ${registry.address}`);
  console.log(`Request: ${request.address}`);
  console.log(`Auction: ${auction.address}`);
  console.log(`Facade: ${facade.address}`);
  console.log("");

  // Check registered users
  console.log("👥 REGISTERED USERS:");
  console.log("============================================================");
  
  try {
    // Check registered users by ID (from simulation logs)
    const commuterIds = [0, 1, 2, 3, 4];
    const providerIds = [100, 101, 102];

    console.log("COMMUTERS:");
    for (let id of commuterIds) {
      try {
        const address = await registry.getCommuter(id);
        if (address !== "0x0000000000000000000000000000000000000000") {
          console.log(`✅ Commuter ${id}: ${address}`);
        } else {
          console.log(`❌ Commuter ${id}: NOT REGISTERED`);
        }
      } catch (e) {
        console.log(`❌ Commuter ${id}: ERROR - ${e.message}`);
      }
    }

    console.log("\nPROVIDERS:");
    for (let id of providerIds) {
      try {
        const [address, mode] = await registry.getProvider(id);
        if (address !== "0x0000000000000000000000000000000000000000") {
          const modeNames = {1: "Car", 2: "Bike", 3: "Bus", 4: "Train"};
          console.log(`✅ Provider ${id}: ${address} (Mode: ${modeNames[mode] || mode})`);
        } else {
          console.log(`❌ Provider ${id}: NOT REGISTERED`);
        }
      } catch (e) {
        console.log(`❌ Provider ${id}: ERROR - ${e.message}`);
      }
    }
  } catch (e) {
    console.log(`Error checking registrations: ${e.message}`);
  }

  console.log("");

  // Check requests
  console.log("📝 STORED REQUESTS:");
  console.log("============================================================");
  
  try {
    // Try to get some requests by ID (from recent simulation logs)
    const requestIds = [
      "11313806944927182985",
      "10266071066932708074",
      "11017542509161025393",
      "11916770516963040642",
      "12978888641822073856",
      "13344665538219912331",
      "9562363673188137687",
      "10102680209072222665"
    ];

    for (let requestId of requestIds) {
      try {
        const requestData = await request.getRequest(requestId);
        console.log(`✅ Request ${requestId}:`);
        console.log(`   Commuter: ${requestData.commuter}`);
        console.log(`   Content Hash: ${requestData.contentHash}`);
        console.log(`   Timestamp: ${new Date(requestData.timestamp * 1000).toISOString()}`);
        console.log(`   Status: ${requestData.status}`);
        console.log("");
      } catch (e) {
        console.log(`❌ Request ${requestId} - NOT FOUND or ERROR`);
      }
    }
  } catch (e) {
    console.log(`Error checking requests: ${e.message}`);
  }

  // Check matches
  console.log("🤝 STORED MATCHES:");
  console.log("============================================================");
  
  try {
    // Check for matches using the same request IDs
    const requestIds = [
      "11313806944927182985",
      "10266071066932708074",
      "11017542509161025393",
      "11916770516963040642",
      "12978888641822073856",
      "13344665538219912331",
      "9562363673188137687",
      "10102680209072222665"
    ];

    for (let requestId of requestIds) {
      try {
        const matchData = await auction.getMatch(requestId);
        console.log(`✅ Match for Request ${requestId}:`);
        console.log(`   Winner Offer ID: ${matchData.winnerOfferId}`);
        console.log(`   Provider: ${matchData.provider}`);
        console.log(`   Price: ${ethers.utils.formatEther(matchData.priceWei)} ETH`);
        console.log(`   Timestamp: ${new Date(matchData.timestamp * 1000).toISOString()}`);
        console.log("");
      } catch (e) {
        console.log(`❌ Match for Request ${requestId} - NOT FOUND`);
      }
    }
  } catch (e) {
    console.log(`Error checking matches: ${e.message}`);
  }

  // Get recent events
  console.log("📡 RECENT BLOCKCHAIN EVENTS:");
  console.log("============================================================");
  
  try {
    const currentBlock = await ethers.provider.getBlockNumber();
    const fromBlock = Math.max(0, currentBlock - 100); // Last 100 blocks
    
    // Get registration events
    const commuterEvents = await registry.queryFilter(
      registry.filters.CommuterRegistered(),
      fromBlock,
      currentBlock
    );
    
    const providerEvents = await registry.queryFilter(
      registry.filters.ProviderRegistered(),
      fromBlock,
      currentBlock
    );

    console.log(`📊 Found ${commuterEvents.length} commuter registrations`);
    console.log(`📊 Found ${providerEvents.length} provider registrations`);

    // Get request events
    const requestEvents = await request.queryFilter(
      request.filters.RequestCreated(),
      fromBlock,
      currentBlock
    );
    
    console.log(`📊 Found ${requestEvents.length} requests created`);

    // Get match events  
    const matchEvents = await auction.queryFilter(
      auction.filters.MatchRecorded(),
      fromBlock,
      currentBlock
    );
    
    console.log(`📊 Found ${matchEvents.length} matches recorded`);

  } catch (e) {
    console.log(`Error getting events: ${e.message}`);
  }

  console.log("");
  console.log("🎯 VERIFICATION COMPLETE!");
  console.log("============================================================");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("Verification failed:", error);
    process.exit(1);
  });
