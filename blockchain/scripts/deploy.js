const hre = require("hardhat");

// Phase 0/1: deploys the legacy DocumentRegistry baseline.
// Phase 3 will switch this to ModelLedgerRegistry.
const CONTRACT_NAME = "DocumentRegistry";

async function main() {
  const Factory = await hre.ethers.getContractFactory(CONTRACT_NAME);
  const registry = await Factory.deploy();
  await registry.waitForDeployment();
  const address = await registry.getAddress();

  console.log(`${CONTRACT_NAME} deployed to: ${address}`);
  console.log("\nTo point the backend at it later (Phase 3):");
  console.log(`  export MODELLEDGER_RPC_URL=http://127.0.0.1:8545`);
  console.log(`  export MODELLEDGER_CONTRACT_ADDRESS=${address}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
