"""Blockchain adapter (stub until Phase 3).

Design rule ("no silent success"): this adapter NEVER reports a positive result
it did not actually obtain from a chain. Without a configured RPC URL and
contract address it reports mode="stub", committed=False and verified=None.

The old baseline returned {"verified": True} when the chain was missing and used
the placeholder address "0xYourDeployedAddressHere". Both are gone.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

import config


def is_configured() -> bool:
    return bool(config.BLOCKCHAIN_RPC_URL and config.CONTRACT_ADDRESS)


def status() -> Dict[str, Any]:
    if not is_configured():
        return {
            "mode": "stub",
            "connected": False,
            "note": "Blockchain registry is not wired up yet (arrives in Phase 3). "
            "No on-chain evidence is claimed.",
        }
    # Phase 3 will actually connect with web3 and report real state here.
    return {
        "mode": "configured-unimplemented",
        "connected": False,
        "note": "RPC URL and contract address are set, but the ModelLedgerRegistry adapter is a Phase 3 deliverable.",
    }


def register_commitment(kind: str, identifier: str, commitment: str) -> Dict[str, Any]:
    return {"success": False, "committed": False, "tx_hash": None, "reason": status()["note"]}


def has_record(kind: str, identifier: str, commitment: Optional[str] = None) -> Optional[bool]:
    """True/False only when the chain was really queried; None otherwise."""
    return None
