// scripts/check-permissions.js
// Check contract permissions and ownership

const { ethers } = require("hardhat");
const fs = require("fs");

async function main() {
  console.log("🔍 CHECKING CONTRACT PERMISSIONS");
  console.log("============================================================");

  // Load deployment info
  const deploymentInfo = JSON.parse(fs.readFileSync("deployed/simplified.json", "utf8"));
  
  // Get contract instances
  const registry = await ethers.getContractAt("MaaSRegistry", deploymentInfo.Registry);
  const facade = await ethers.getContractAt("MaaSFacade", deploymentInfo.Facade);

  console.log("📋 Contract Addresses:");
  console.log(`Registry: ${registry.address}`);
  console.log(`Facade: ${facade.address}`);
  console.log(`API Account: ${deploymentInfo.marketplaceAPI}`);
  console.log("");

  // Check ownership
  console.log("👑 OWNERSHIP:");
  console.log("============================================================");
  
  try {
    const registryOwner = await registry.owner();
    const facadeOwner = await facade.owner();
    
    console.log(`Registry Owner: ${registryOwner}`);
    console.log(`Facade Owner: ${facadeOwner}`);
    console.log(`API Account: ${deploymentInfo.marketplaceAPI}`);
    console.log("");
    
    console.log("✅ Registry owned by facade:", registryOwner.toLowerCase() === facade.address.toLowerCase());
    console.log("✅ Facade owned by API:", facadeOwner.toLowerCase() === deploymentInfo.marketplaceAPI.toLowerCase());
    
  } catch (e) {
    console.log(`Error checking ownership: ${e.message}`);
  }

  console.log("");

  // Test a registration call
  console.log("🧪 TESTING REGISTRATION CALL:");
  console.log("============================================================");
  
  try {
    const [signer] = await ethers.getSigners();
    console.log(`Test signer: ${signer.address}`);
    console.log(`API account: ${deploymentInfo.marketplaceAPI}`);
    console.log(`Same account: ${signer.address.toLowerCase() === deploymentInfo.marketplaceAPI.toLowerCase()}`);
    
    // Try to call registerAsCommuter
    console.log("\nTesting registerAsCommuter call...");
    
    // Estimate gas first
    const gasEstimate = await facade.estimateGas.registerAsCommuter(999, "0x1234567890123456789012345678901234567890");
    console.log(`Gas estimate: ${gasEstimate.toString()}`);
    
    // Try the actual call (dry run)
    await facade.callStatic.registerAsCommuter(999, "0x1234567890123456789012345678901234567890");
    console.log("✅ Call would succeed");
    
  } catch (e) {
    console.log(`❌ Call would fail: ${e.message}`);
    
    // Check if it's a permission issue
    if (e.message.includes("Not owner") || e.message.includes("Ownable")) {
      console.log("🔒 This is a permission issue - API account is not the owner");
    }
  }

  console.log("");
  console.log("🎯 PERMISSION CHECK COMPLETE!");
  console.log("============================================================");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("Permission check failed:", error);
    process.exit(1);
  });
