// scripts/fund-api-account.js
// Fund the API account with ETH for gas fees

const { ethers } = require("hardhat");

async function main() {
  console.log("Funding API account with ETH for gas fees...");

  // Get signers
  const [deployer] = await ethers.getSigners();
  
  // API account address (same as used in Python)
  const apiAccountAddress = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266";
  
  console.log(`Deployer: ${deployer.address}`);
  console.log(`API Account: ${apiAccountAddress}`);
  
  // Check if they're the same (they should be in Hardhat)
  if (deployer.address.toLowerCase() === apiAccountAddress.toLowerCase()) {
    console.log("✅ API account is the same as deployer - already funded!");
    
    // Check balance
    const balance = await ethers.provider.getBalance(apiAccountAddress);
    console.log(`API account balance: ${ethers.utils.formatEther(balance)} ETH`);
    
    if (balance.gt(ethers.utils.parseEther("1"))) {
      console.log("✅ API account has sufficient ETH for gas fees");
    } else {
      console.log("⚠️  API account has low ETH balance");
    }
  } else {
    // Fund the API account
    const fundAmount = ethers.utils.parseEther("10"); // 10 ETH
    
    console.log(`Sending ${ethers.utils.formatEther(fundAmount)} ETH to API account...`);
    
    const tx = await deployer.sendTransaction({
      to: apiAccountAddress,
      value: fundAmount
    });
    
    await tx.wait();
    
    console.log(`✅ Funded API account: ${tx.hash}`);
    
    // Check new balance
    const balance = await ethers.provider.getBalance(apiAccountAddress);
    console.log(`API account balance: ${ethers.utils.formatEther(balance)} ETH`);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("Error funding API account:", error);
    process.exit(1);
  });
