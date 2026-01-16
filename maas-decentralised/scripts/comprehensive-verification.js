// scripts/comprehensive-verification.js
// Comprehensive verification of all blockchain storage

const { ethers } = require("hardhat");
const fs = require("fs");

async function main() {
  console.log("🔍 COMPREHENSIVE BLOCKCHAIN VERIFICATION");
  console.log("============================================================");

  // Get current block number
  const currentBlock = await ethers.provider.getBlockNumber();
  console.log(`Current block: ${currentBlock}`);
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

  // Check registrations
  console.log("👥 REGISTERED USERS:");
  console.log("============================================================");
  
  console.log("COMMUTERS:");
  for (let i = 0; i < 5; i++) {
    try {
      const commuter = await registry.getCommuter(i);
      if (commuter !== "0x0000000000000000000000000000000000000000") {
        console.log(`✅ Commuter ${i}: ${commuter}`);
      } else {
        console.log(`❌ Commuter ${i}: NOT REGISTERED`);
      }
    } catch (e) {
      console.log(`❌ Commuter ${i}: ERROR - ${e.message}`);
    }
  }

  console.log("\nPROVIDERS:");
  for (let i = 100; i < 103; i++) {
    try {
      const [providerAddr, mode] = await registry.getProvider(i);
      if (providerAddr !== "0x0000000000000000000000000000000000000000") {
        console.log(`✅ Provider ${i}: ${providerAddr} (mode: ${mode})`);
      } else {
        console.log(`❌ Provider ${i}: NOT REGISTERED`);
      }
    } catch (e) {
      console.log(`❌ Provider ${i}: ERROR - ${e.message}`);
    }
  }

  // Check requests
  console.log("\n📝 STORED REQUESTS:");
  console.log("============================================================");
  
  try {
    const lastRequestId = await request.lastRequestId();
    console.log(`Last request ID: ${lastRequestId}`);
    
    for (let i = 1; i <= Math.min(lastRequestId, 10); i++) {
      try {
        const requestHash = await request.getRequestHash(i);
        const status = await request.getStatus(i);
        console.log(`✅ Request ${i}: Hash ${requestHash.slice(0, 10)}..., Status: ${status}`);
      } catch (e) {
        console.log(`❌ Request ${i}: ERROR - ${e.message}`);
      }
    }
  } catch (e) {
    console.log(`❌ Error getting requests: ${e.message}`);
  }

  // Check offers
  console.log("\n💰 STORED OFFERS:");
  console.log("============================================================");
  
  for (let requestId = 1; requestId <= 5; requestId++) {
    try {
      const offers = await auction.getOffers(requestId);
      if (offers.length > 0) {
        console.log(`✅ Request ${requestId} has ${offers.length} offers:`);
        offers.forEach((offer, index) => {
          console.log(`   Offer ${index}: Provider ${offer.providerId}, Hash: ${offer.contentHash.slice(0, 10)}...`);
        });
      } else {
        console.log(`❌ Request ${requestId}: No offers found`);
      }
    } catch (e) {
      console.log(`❌ Request ${requestId}: ERROR - ${e.message}`);
    }
  }

  // Check matches
  console.log("\n🤝 STORED MATCHES:");
  console.log("============================================================");
  
  for (let requestId = 1; requestId <= 5; requestId++) {
    try {
      const match = await auction.getMatch(requestId);
      if (match.exists) {
        console.log(`✅ Request ${requestId}: Matched with offer ${match.offerId}, provider ${match.providerId}, price ${ethers.utils.formatEther(match.priceWei)} ETH`);
      } else {
        console.log(`❌ Request ${requestId}: No match found`);
      }
    } catch (e) {
      console.log(`❌ Request ${requestId}: ERROR - ${e.message}`);
    }
  }

  // Check recent events
  console.log("\n📡 RECENT BLOCKCHAIN EVENTS:");
  console.log("============================================================");
  const fromBlock = Math.max(0, currentBlock - 50);
  
  try {
    const commuterEvents = await registry.queryFilter(
      registry.filters.CommuterRegistered(),
      fromBlock,
      currentBlock
    );
    console.log(`📊 Found ${commuterEvents.length} commuter registration events`);
    
    const providerEvents = await registry.queryFilter(
      registry.filters.ProviderRegistered(),
      fromBlock,
      currentBlock
    );
    console.log(`📊 Found ${providerEvents.length} provider registration events`);
    
    const requestEvents = await request.queryFilter(
      request.filters.RequestCreated(),
      fromBlock,
      currentBlock
    );
    console.log(`📊 Found ${requestEvents.length} request creation events`);
    
    const offerEvents = await auction.queryFilter(
      auction.filters.OfferSubmitted(),
      fromBlock,
      currentBlock
    );
    console.log(`📊 Found ${offerEvents.length} offer submission events`);
    
    const matchEvents = await auction.queryFilter(
      auction.filters.MatchRecorded(),
      fromBlock,
      currentBlock
    );
    console.log(`📊 Found ${matchEvents.length} match recording events`);

  } catch (e) {
    console.log(`❌ Error getting events: ${e.message}`);
  }

  console.log("\n🎯 VERIFICATION COMPLETE!");
  console.log("============================================================");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("Verification failed:", error);
    process.exit(1);
  });
