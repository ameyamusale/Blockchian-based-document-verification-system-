"""Verification Engine: collect evidence for an uploaded artifact, then ask the trust engine."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import List, Optional

from models.claims import EvidenceCheck, VerificationEvidence, VerificationReport
from models.model import ModelStatus
from services import blockchain, conflict_detector, signature, transformation
from services.artifact_registry import find_by_hash
from services.hashing import sha256_bytes
from services.provenance import build_lineage
from services.store import store
from services.trust_engine import evaluate

log = logging.getLogger("modelledger.verification")


def _check(key: str, label: str, value: Optional[bool], pass_msg: str, fail_msg: str) -> EvidenceCheck:
    if value is None:
        return EvidenceCheck(key=key, label=label, state="not_checked", detail="Not checked in this phase / not available")
    return EvidenceCheck(key=key, label=label, state="pass" if value else "fail", detail=pass_msg if value else fail_msg)


def verify_bytes(data: bytes) -> VerificationReport:
    exact_hash = sha256_bytes(data)
    artifact = find_by_hash(exact_hash)
    chain_status = blockchain.status()
    now = datetime.now(timezone.utc)

    if artifact is None:
        evidence = VerificationEvidence(artifact_match=False)
        decision = evaluate(evidence)
        report = VerificationReport(
            exact_hash=exact_hash,
            evidence=evidence,
            checks=[_check("artifact_match", "Exact hash is registered", False, "", "No registered artifact has this SHA-256")],
            decision=decision,
            blockchain=chain_status,
            verified_at=now,
        )
        log.info("verify hash=%s status=%s", exact_hash[:12], decision.status.value)
        return report

    model = store.models.get(artifact.model_id) if artifact.model_id else None
    lineage = build_lineage(artifact.artifact_id)
    own_events = [s.event for s in lineage.steps if s.event is not None]

    # parent_exists: only meaningful when this artifact claims a parent.
    own_event = lineage.steps[-1].event if lineage.steps else None
    parent_exists: Optional[bool] = None
    if own_event is not None and own_event.parent_artifact_id:
        parent_exists = own_event.parent_artifact_id in store.artifacts

    if own_event is None:
        lineage_ok: Optional[bool] = None  # no provenance event recorded at all
    elif any("does not exist" in i or "Cycle" in i for i in lineage.issues):
        lineage_ok = False
    else:
        lineage_ok = True if lineage.root_reached else None

    sig_results = [signature.verify_event_signature(e) for e in own_events]
    tx_results = [transformation.check_transformation(e) for e in own_events if e.parent_artifact_id]
    signature_valid = None if (not sig_results or any(r is None for r in sig_results)) else all(sig_results)
    transformation_valid = None if (not tx_results or any(r is None for r in tx_results)) else all(tx_results)

    evidence = VerificationEvidence(
        artifact_match=True,
        model_registered=(model is not None) if artifact.model_id else False,
        signature_valid=signature_valid,
        parent_exists=parent_exists,
        transformation_valid=transformation_valid,
        blockchain_record=blockchain.has_record("artifact", artifact.artifact_id, artifact.exact_hash),
        revoked=(model.status == ModelStatus.REVOKED) if model else None,
    )
    conflicts = conflict_detector.detect_conflicts(artifact.artifact_id)
    decision = evaluate(evidence, conflicts)
    if lineage.issues and not lineage.root_reached:
        decision.reasons.extend(lineage.issues)

    checks: List[EvidenceCheck] = [
        _check("artifact_match", "Exact hash is registered", True, f"Matches {artifact.artifact_id}", ""),
        _check("model_registered", "Claimed model is registered", evidence.model_registered,
               f"{model.name} v{model.version}" if model else "", "No registered model is linked to this artifact"),
        _check("parent_exists", "Lineage links are intact", lineage_ok,
               f"Chain of {lineage.depth + 1} artifact(s) reaches its GENERATED origin", "A parent artifact is missing or the chain loops"),
        _check("transformation_valid", "Transformation claims verified", evidence.transformation_valid, "Transformations verified", "Transformation mismatch"),
        _check("signature_valid", "Provenance signature valid", evidence.signature_valid, "Signature verified", "Signature invalid"),
        _check("blockchain_record", "On-chain record exists", evidence.blockchain_record, "Record found on chain", "No on-chain record"),
        _check("revoked", "Not revoked", None if evidence.revoked is None else (not evidence.revoked), "Not revoked", "Revoked"),
    ]
    report = VerificationReport(
        exact_hash=exact_hash,
        artifact=artifact,
        model=model,
        lineage=lineage,
        evidence=evidence,
        checks=checks,
        decision=decision,
        blockchain=chain_status,
        verified_at=now,
    )
    log.info("verify artifact=%s status=%s", artifact.artifact_id, decision.status.value)
    return report
