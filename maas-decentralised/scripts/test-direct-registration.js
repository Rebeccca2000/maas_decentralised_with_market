// scripts/test-direct-registration.js
// Test direct registration to see if it works

const { ethers } = require("hardhat");
const fs = require("fs");

async function main() {
  console.log("🧪 TESTING DIRECT REGISTRATION");
  console.log("============================================================");

  // Load deployment info
  const deploymentInfo = JSON.parse(fs.readFileSync("deployed/simplified.json", "utf8"));
  
  // Get contract instances
  const registry = await ethers.getContractAt("MaaSRegistry", deploymentInfo.Registry);
  const facade = await ethers.getContractAt("MaaSFacade", deploymentInfo.Facade);

  const [signer] = await ethers.getSigners();
  
  console.log("📋 Setup:");
  console.log(`Facade: ${facade.address}`);
  console.log(`Registry: ${registry.address}`);
  console.log(`Signer: ${signer.address}`);
  console.log("");

  // Test 1: Register a commuter
  console.log("👤 TEST 1: Register Commuter");
  console.log("------------------------------------------------------------");
  
  try {
    const testCommuterId = 999;
    const testAddress = "0x1234567890123456789012345678901234567890";
    
    console.log(`Registering commuter ${testCommuterId} at ${testAddress}...`);
    
    const tx = await facade.registerAsCommuter(testCommuterId, testAddress);
    console.log(`Transaction sent: ${tx.hash}`);
    
    const receipt = await tx.wait();
    console.log(`✅ Transaction confirmed in block ${receipt.blockNumber}`);
    console.log(`Gas used: ${receipt.gasUsed.toString()}`);
    console.log(`Events: ${receipt.events ? receipt.events.length : 0}`);
    
    // Check if it was stored
    const storedAddress = await registry.getCommuter(testCommuterId);
    console.log(`Stored address: ${storedAddress}`);
    console.log(`✅ Registration successful: ${storedAddress.toLowerCase() === testAddress.toLowerCase()}`);
    
  } catch (e) {
    console.log(`❌ Registration failed: ${e.message}`);
  }

  console.log("");

  // Test 2: Register a provider
  console.log("🚗 TEST 2: Register Provider");
  console.log("------------------------------------------------------------");
  
  try {
    const testProviderId = 888;
    const testAddress = "0x9876543210987654321098765432109876543210";
    const testMode = 1; // Car
    
    console.log(`Registering provider ${testProviderId} at ${testAddress} with mode ${testMode}...`);
    
    const tx = await facade.registerAsProvider(testProviderId, testAddress, testMode);
    console.log(`Transaction sent: ${tx.hash}`);
    
    const receipt = await tx.wait();
    console.log(`✅ Transaction confirmed in block ${receipt.blockNumber}`);
    console.log(`Gas used: ${receipt.gasUsed.toString()}`);
    console.log(`Events: ${receipt.events ? receipt.events.length : 0}`);
    
    // Check if it was stored
    const [storedAddress, storedMode] = await registry.getProvider(testProviderId);
    console.log(`Stored address: ${storedAddress}`);
    console.log(`Stored mode: ${storedMode}`);
    console.log(`✅ Registration successful: ${storedAddress.toLowerCase() === testAddress.toLowerCase() && storedMode === testMode}`);
    
  } catch (e) {
    console.log(`❌ Registration failed: ${e.message}`);
  }

  console.log("");

  // Test 3: Check all registrations
  console.log("📊 TEST 3: Check All Registrations");
  console.log("------------------------------------------------------------");
  
  try {
    // Check our test registrations
    const commuter999 = await registry.getCommuter(999);
    const [provider888Address, provider888Mode] = await registry.getProvider(888);
    
    console.log(`Commuter 999: ${commuter999}`);
    console.log(`Provider 888: ${provider888Address} (mode: ${provider888Mode})`);
    
    // Check the simulation IDs
    console.log("\nChecking simulation IDs:");
    for (let i = 0; i <= 4; i++) {
      const address = await registry.getCommuter(i);
      console.log(`Commuter ${i}: ${address}`);
    }
    
    for (let i = 100; i <= 102; i++) {
      const [address, mode] = await registry.getProvider(i);
      console.log(`Provider ${i}: ${address} (mode: ${mode})`);
    }
    
  } catch (e) {
    console.log(`❌ Check failed: ${e.message}`);
  }

  console.log("");
  console.log("🎯 DIRECT REGISTRATION TEST COMPLETE!");
  console.log("============================================================");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("Test failed:", error);
    process.exit(1);
  });
