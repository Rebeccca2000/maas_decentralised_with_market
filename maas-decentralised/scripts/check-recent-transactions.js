// scripts/check-recent-transactions.js
// Check recent transactions and events on the blockchain

const { ethers } = require("hardhat");
const fs = require("fs");

async function main() {
  console.log("🔍 CHECKING RECENT BLOCKCHAIN ACTIVITY");
  console.log("============================================================");

  // Get current block number
  const currentBlock = await ethers.provider.getBlockNumber();
  console.log(`Current block: ${currentBlock}`);

  // Check recent blocks for transactions
  const blocksToCheck = Math.min(10, currentBlock);
  console.log(`Checking last ${blocksToCheck} blocks...`);
  console.log("");

  let totalTransactions = 0;
  
  for (let i = currentBlock; i > currentBlock - blocksToCheck; i--) {
    try {
      const block = await ethers.provider.getBlock(i, true);
      if (block && block.transactions.length > 0) {
        console.log(`📦 Block ${i}: ${block.transactions.length} transactions`);
        
        for (let j = 0; j < Math.min(3, block.transactions.length); j++) {
          const tx = block.transactions[j];
          console.log(`  📄 TX ${j+1}: ${tx.hash}`);
          console.log(`     From: ${tx.from}`);
          console.log(`     To: ${tx.to}`);
          console.log(`     Nonce: ${tx.nonce}`);
          
          // Get transaction receipt to see if it was successful
          try {
            const receipt = await ethers.provider.getTransactionReceipt(tx.hash);
            console.log(`     Status: ${receipt.status === 1 ? '✅ SUCCESS' : '❌ FAILED'}`);
            console.log(`     Gas Used: ${receipt.gasUsed.toString()}`);
            
            if (receipt.logs.length > 0) {
              console.log(`     Events: ${receipt.logs.length} logs emitted`);
            }
          } catch (e) {
            console.log(`     Status: ❓ UNKNOWN`);
          }
          console.log("");
        }
        
        totalTransactions += block.transactions.length;
      }
    } catch (e) {
      console.log(`❌ Error checking block ${i}: ${e.message}`);
    }
  }

  console.log(`📊 Total transactions found: ${totalTransactions}`);
  console.log("");

  // Load deployment info and check contract addresses
  try {
    const deploymentInfo = JSON.parse(fs.readFileSync("deployed/simplified.json", "utf8"));
    console.log("📋 Contract Addresses from deployment:");
    console.log(`Registry: ${deploymentInfo.Registry}`);
    console.log(`Request: ${deploymentInfo.Request}`);
    console.log(`Auction: ${deploymentInfo.Auction}`);
    console.log(`Facade: ${deploymentInfo.Facade}`);
    console.log("");

    // Check if any transactions were sent to these contracts
    console.log("🎯 Checking transactions to our contracts:");
    
    const contractAddresses = [
      deploymentInfo.Registry,
      deploymentInfo.Request,
      deploymentInfo.Auction,
      deploymentInfo.Facade
    ];

    for (let i = currentBlock; i > currentBlock - blocksToCheck; i--) {
      try {
        const block = await ethers.provider.getBlock(i, true);
        if (block && block.transactions.length > 0) {
          for (const tx of block.transactions) {
            if (contractAddresses.includes(tx.to)) {
              console.log(`✅ Found transaction to our contract!`);
              console.log(`   Block: ${i}`);
              console.log(`   TX: ${tx.hash}`);
              console.log(`   To: ${tx.to}`);
              console.log(`   From: ${tx.from}`);
              
              const receipt = await ethers.provider.getTransactionReceipt(tx.hash);
              console.log(`   Status: ${receipt.status === 1 ? '✅ SUCCESS' : '❌ FAILED'}`);
              console.log(`   Events: ${receipt.logs.length} logs`);
              console.log("");
            }
          }
        }
      } catch (e) {
        // Skip errors
      }
    }

  } catch (e) {
    console.log(`❌ Error loading deployment info: ${e.message}`);
  }

  console.log("🎯 ANALYSIS COMPLETE!");
  console.log("============================================================");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("Analysis failed:", error);
    process.exit(1);
  });
