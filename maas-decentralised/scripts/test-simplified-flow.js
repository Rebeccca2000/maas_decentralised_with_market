// File: scripts/test-simplified-flow.js
// Corrected test script for the simplified MaaS contracts
const { ethers } = require("hardhat");
const fs = require("fs");

// Load deployment info
const deploymentInfo = JSON.parse(fs.readFileSync("deployed/simplified.json", "utf8"));

async function main() {
  console.log("Starting simplified MaaS flow test...");

  // Get the signers
  const [admin, commuter1, provider1] = await ethers.getSigners();
  
  console.log(`Admin: ${admin.address}`);
  console.log(`Commuter 1: ${commuter1.address}`);
  console.log(`Provider 1: ${provider1.address}`);

  // Load the contracts using the correct deployment info
  const registry = await ethers.getContractAt("MaaSRegistry", deploymentInfo.Registry);
  const request = await ethers.getContractAt("MaaSRequest", deploymentInfo.Request);
  const auction = await ethers.getContractAt("MaaSAuction", deploymentInfo.Auction);
  const facade = await ethers.getContractAt("MaaSFacade", deploymentInfo.Facade);

  console.log("Contracts loaded successfully");

  // Step 1: Check facade owner and marketplace API
  console.log("Checking facade access control...");
  const facadeOwner = await facade.owner();
  const marketplaceAPI = await facade.marketplaceAPI();
  console.log(`Facade owner: ${facadeOwner}`);
  console.log(`Marketplace API: ${marketplaceAPI}`);
  console.log(`Admin address: ${admin.address}`);

  // Registration functions use onlyOwner, other functions use onlyAPI
  const ownerSigner = admin.address === facadeOwner ? admin : await ethers.getSigner(facadeOwner);
  const apiSigner = admin.address === marketplaceAPI ? admin : await ethers.getSigner(marketplaceAPI);

  console.log("Registering commuter and provider...");

  // Use timestamp to ensure unique IDs
  const timestamp = Math.floor(Date.now() / 1000);
  const commuterId = timestamp;
  const providerId = timestamp + 1;
  const providerMode = 1; // e.g., rideshare

  await facade.connect(ownerSigner).registerAsCommuter(commuterId, commuter1.address);
  await facade.connect(ownerSigner).registerAsProvider(providerId, provider1.address, providerMode);
  
  console.log("Registration completed");

  // Step 2: Create a request through facade
  console.log("Creating travel request...");
  
  const contentHash = "QmTravelRequestHash123"; // IPFS hash for request details
  
  const tx = await facade.connect(apiSigner).submitRequestHash(commuterId, contentHash);
  const receipt = await tx.wait();
  
  // Extract request ID from events
  console.log("Transaction receipt events:", receipt.events?.length || 0);
  console.log("All events:", receipt.events);

  // The event might be nested in logs, let's try a different approach
  let requestId;
  if (receipt.events && receipt.events.length > 0) {
    // Look for RequestCreated event in all events
    for (const event of receipt.events) {
      console.log("Event:", event.event, event.args);
      if (event.event === 'RequestCreated' && event.args) {
        requestId = event.args.requestId;
        break;
      }
    }
  }

  // If we still don't have requestId, get it from the request contract
  if (!requestId) {
    console.log("Getting request ID from contract...");
    requestId = await request.lastRequestId();
  }
  
  console.log(`Travel request created with ID: ${requestId}`);

  // Step 3: Submit an offer through facade
  console.log("Submitting offer...");
  
  const offerContentHash = "QmOfferHash456"; // IPFS hash for offer details
  
  const offerTx = await facade.connect(apiSigner).submitOfferHash(requestId, providerId, offerContentHash);
  const offerReceipt = await offerTx.wait();
  
  // Extract offer ID from events or use 0 as first offer
  let offerId = 0; // Default to first offer
  if (offerReceipt.events && offerReceipt.events.length > 0) {
    for (const event of offerReceipt.events) {
      console.log("Offer Event:", event.event, event.args);
      if (event.event === 'OfferSubmitted' && event.args) {
        offerId = event.args.offerId;
        break;
      }
    }
  }
  
  console.log(`Offer submitted with ID: ${offerId}`);

  // Step 4: Record match result
  console.log("Recording match result...");
  
  const priceWei = ethers.utils.parseEther("0.1"); // 0.1 ETH
  
  await facade.connect(apiSigner).recordMatch(requestId, offerId, providerId, priceWei);
  
  console.log("Match recorded successfully");

  // Step 5: Confirm completion
  console.log("Confirming service completion...");
  
  await facade.connect(apiSigner).confirmCompletion(requestId);
  
  console.log("Service completion confirmed");

  // Step 6: Verify final state
  console.log("Verifying final state...");
  
  const finalRequest = await request.requests(requestId);
  const matchResult = await auction.getMatchResult(requestId);
  
  console.log(`Final request status: ${finalRequest.status}`);
  console.log(`Match completed: ${matchResult.completed}`);
  console.log(`Match price: ${ethers.utils.formatEther(matchResult.priceWei)} ETH`);

  console.log("Simplified MaaS flow test completed successfully!");
}

// Execute the test
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("Error during test:", error);
    process.exit(1);
  });
