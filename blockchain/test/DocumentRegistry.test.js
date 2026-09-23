const { expect } = require("chai");
const { ethers } = require("hardhat");
 
describe("DocumentRegistry", function () {
  let registry;
 
  beforeEach(async function () {
    const DocumentRegistry = await ethers.getContractFactory("DocumentRegistry");
    registry = await DocumentRegistry.deploy();
    await registry.waitForDeployment();
  });
 
  it("registers a document and verifies it correctly", async function () {
    await registry.registerDocument("VT-2026-0001", "hash_original_abc123");
 
    const isValid = await registry.verifyDocument("VT-2026-0001", "hash_original_abc123");
    expect(isValid).to.equal(true);
  });
 
  it("detects a tampered document (hash mismatch)", async function () {
    await registry.registerDocument("VT-2026-0002", "hash_original_abc123");
 
    const isValid = await registry.verifyDocument("VT-2026-0002", "hash_tampered_xyz999");
    expect(isValid).to.equal(false);
  });
 
  it("prevents registering the same document_id twice", async function () {
    await registry.registerDocument("VT-2026-0003", "hash_abc");
    await expect(
      registry.registerDocument("VT-2026-0003", "hash_def")
    ).to.be.revertedWith("Document already registered");
  });
 
  it("reverts when verifying a document that was never registered", async function () {
    await expect(
      registry.verifyDocument("VT-NONEXISTENT", "some_hash")
    ).to.be.revertedWith("Document not found");
  });
});
 