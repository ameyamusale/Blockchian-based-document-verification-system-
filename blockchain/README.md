# ModelLedger — blockchain workspace

Hardhat 2 + ethers v6.

| Phase | Contract |
|-------|----------|
| 0–1 (now) | `DocumentRegistry.sol` — legacy baseline, kept so deploy/test works |
| 3 | `ModelLedgerRegistry.sol` replaces it |

```bash
npm install
npm test                 # compiles + runs the contract tests
npm run node             # terminal 1: local chain on :8545
npm run deploy:local     # terminal 2: deploy, prints the address
```

Hardhat downloads the Solidity compiler (0.8.27) on first run, so it needs internet access to `binaries.soliditylang.org`.
