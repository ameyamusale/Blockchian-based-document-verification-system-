"""Central configuration. All secrets/endpoints come from environment variables.

Nothing in here is a hard-coded account, key or contract address.
"""
from __future__ import annotations

import os
from pathlib import Path

APP_NAME = "ModelLedger"
APP_TAGLINE = "AI Content Provenance & Verification Network"
APP_VERSION = "0.1.0"
IMPLEMENTED_PHASE = 1  # Phase 0 (baseline) + Phase 1 (domain refactor) complete

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"

# --- Uploads (artifacts are hashed in memory; Phase 1 never writes them to disk) ---
MAX_UPLOAD_BYTES = int(os.getenv("MODELLEDGER_MAX_UPLOAD_MB", "10")) * 1024 * 1024
ALLOWED_ARTIFACT_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}

# --- Blockchain (wired up in Phase 3; empty means "not configured") ---
BLOCKCHAIN_RPC_URL = os.getenv("MODELLEDGER_RPC_URL", "").strip()
CONTRACT_ADDRESS = os.getenv("MODELLEDGER_CONTRACT_ADDRESS", "").strip()

# --- CORS ---
CORS_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "MODELLEDGER_CORS_ORIGINS", "http://127.0.0.1:8000,http://localhost:8000"
    ).split(",")
    if o.strip()
]
