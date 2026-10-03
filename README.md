# ModelLedger — AI Content Provenance & Verification Network

Hackathon problem: *Blockchain PS3 — prove which AI model produced this.*
Status: **Phase 0 + Phase 1 complete** (see `docs/PROGRESS.md`).

ModelLedger records and verifies the origin and transformation history of AI-generated artifacts across
multiple models/applications, using hashes, signatures and a blockchain registry, without exposing private prompts or files.
It never reduces the answer to "real/fake": results are `TRUSTED`, `SELF_ASSERTED`, `UNVERIFIABLE` or `CONFLICT`, each with its evidence.

## Run it (backend + UI)

Requirements: Python 3.10+.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn main:app --reload
```
Open **http://127.0.0.1:8000** (UI) and **http://127.0.0.1:8000/docs** (interactive API).

## Run the tests
```bash
cd backend && python -m pytest -q          # 16 backend tests
cd blockchain && npm install && npm test   # 4 legacy contract tests (needs internet for the solc download)
```

## Try the flow in the UI
1. **Register model** "ModelA" v1.0 and "ModelB" v2.0.
2. **Register artifact**: pick an image + ModelA, no parent → recorded as `GENERATED`.
3. Register a second image: producing model ModelB, parent = the first artifact, action `UPSCALED`.
4. **Verify** the second image → lineage `ART-… → UPSCALED → ART-…`, trust state `SELF_ASSERTED`.
   Signature and blockchain rows say *not checked* (they arrive in Phases 3–4). Verify an unknown or modified image → `UNVERIFIABLE`.

Data is in memory and resets when the server restarts (database = Phase 2).

## Repository layout
See `docs/PHASE1_REFACTOR.md`. Baseline audit: `docs/PHASE0_BASELINE.md`. Original marksheet app: `legacy/` and git tag `baseline-dhruv`.

## Configuration
Environment variables only (see `.env.example`). No secrets or contract addresses are hard-coded.
