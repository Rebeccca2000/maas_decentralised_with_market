// scripts/check-transaction-details.js
// Check the details of specific transactions to see what happened

const { ethers } = require("hardhat");

async function main() {
  console.log("🔍 CHECKING TRANSACTION DETAILS");
  console.log("============================================================");

  // Transaction hashes from the simulation logs
  const txHashes = [
    "0xa183a71e57cfcac7d110b83d871384b635154ca0ea2316715c7771ffd6d09ae07", // registerAsCommuter
    "0x4f4d2070f81f54e5a422785927db70542291aeff174c7155afeef5e4bdb7a36f5", // registerAsCommuter
    "0x1c7b6b849de6761c72abf78a0ba766ea3483f347f00b50db55ccd2a8173d60d64", // registerAsCommuter
    "0x54b8aa31b8d096a32d2603587b4ad52bb6c1884b5710cb3ee9dd4bbcfc2fcbae0", // registerAsCommuter
    "0x843ba493737273079f6e7b6c712502b45cfce365e4a417183fbbaba930ba2e4a", // registerAsCommuter
    "0x54d02aa410789fc7efc363d8955e422ed65f361e5c09eb799cee5f1eb678da02f", // registerAsProvider
    "0x549e9c83feac37eeec42e918b83e4480f1ed2fce9bd237d6eecc8b525ac23c07e", // registerAsProvider
    "0xcc27fa6cca14d81c0ac98b471687cdf080f71ae3ee06f2ea75ccbacbfcd70e1b2", // registerAsProvider
    "0x319c3ba11fac80d4fbe6e78ec7404a8b9d55cf187f18788dbdaae87a8f2802359", // createRequestWithHash
    "0x67e0e342dd1002011246b8e4cd9f815f81ce349bdc188c29c0ffc5c3e3fc9beb2"  // recordMatchResult
  ];

  for (let i = 0; i < txHashes.length; i++) {
    const txHash = txHashes[i];
    console.log(`\n📋 Transaction ${i + 1}: ${txHash}`);
    console.log("------------------------------------------------------------");
    
    try {
      // Get transaction receipt
      const receipt = await ethers.provider.getTransactionReceipt(txHash);
      
      if (!receipt) {
        console.log("❌ Transaction not found");
        continue;
      }
      
      console.log(`✅ Status: ${receipt.status === 1 ? 'SUCCESS' : 'FAILED'}`);
      console.log(`📍 Block: ${receipt.blockNumber}`);
      console.log(`⛽ Gas Used: ${receipt.gasUsed.toString()}`);
      console.log(`📧 To: ${receipt.to}`);
      console.log(`📤 From: ${receipt.from}`);
      
      // Get transaction details
      const tx = await ethers.provider.getTransaction(txHash);
      console.log(`💰 Value: ${ethers.utils.formatEther(tx.value)} ETH`);
      console.log(`📊 Gas Limit: ${tx.gasLimit.toString()}`);
      console.log(`🔢 Nonce: ${tx.nonce}`);
      
      // Decode transaction data if possible
      if (tx.data && tx.data !== "0x") {
        console.log(`📝 Data Length: ${tx.data.length} characters`);
        console.log(`📝 Data (first 100 chars): ${tx.data.substring(0, 100)}...`);
      }
      
      // Check for events in the receipt
      if (receipt.logs && receipt.logs.length > 0) {
        console.log(`📡 Events: ${receipt.logs.length} logs found`);
        for (let j = 0; j < receipt.logs.length; j++) {
          const log = receipt.logs[j];
          console.log(`   Log ${j + 1}: Address ${log.address}, Topics: ${log.topics.length}`);
        }
      } else {
        console.log(`📡 Events: No logs found`);
      }
      
    } catch (error) {
      console.log(`❌ Error checking transaction: ${error.message}`);
    }
  }
  
  console.log("\n🎯 TRANSACTION ANALYSIS COMPLETE!");
  console.log("============================================================");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("Analysis failed:", error);
    process.exit(1);
  });
