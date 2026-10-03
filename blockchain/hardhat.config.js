require("@nomicfoundation/hardhat-toolbox");

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.27",
  networks: {
    // `npx hardhat node` listens here; used by `npm run deploy:local`
    localhost: { url: process.env.MODELLEDGER_RPC_URL || "http://127.0.0.1:8545" },
  },
};
