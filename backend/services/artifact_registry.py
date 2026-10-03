"""Artifact Registry: exact hash + (later) robust fingerprint per artifact."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from models.artifact import ArtifactRecord, ArtifactStatus, ArtifactType
from services.errors import DuplicateError, NotFoundError
from services.fingerprint import compute_robust_fingerprint
from services.hashing import sha256_bytes
from services.model_registry import get_model
from services.store import store


def register_artifact(
    data: bytes,
    artifact_type: ArtifactType = ArtifactType.IMAGE,
    model_id: Optional[str] = None,
) -> ArtifactRecord:
    if model_id:
        get_model(model_id)  # raises NotFoundError if the claimed model is unknown
    exact_hash = sha256_bytes(data)
    with store.lock:
        existing = store.find_artifact_by_hash(exact_hash)
        if existing:
            raise DuplicateError(
                f"These exact bytes are already registered as {existing.artifact_id}",
                existing.artifact_id,
            )
        record = ArtifactRecord(
            artifact_id="ART-" + uuid.uuid4().hex[:8].upper(),
            artifact_type=artifact_type,
            exact_hash=exact_hash,
            robust_fingerprint=compute_robust_fingerprint(data, artifact_type),
            size_bytes=len(data),
            model_id=model_id,
            status=ArtifactStatus.REGISTERED,
            created_at=datetime.now(timezone.utc),
        )
        store.artifacts[record.artifact_id] = record
        store.artifact_by_hash[exact_hash] = record.artifact_id
        return record


def get_artifact(artifact_id: str) -> ArtifactRecord:
    record = store.artifacts.get(artifact_id)
    if record is None:
        raise NotFoundError(f"Artifact {artifact_id} not found")
    return record


def list_artifacts() -> List[ArtifactRecord]:
    return sorted(store.artifacts.values(), key=lambda a: a.created_at, reverse=True)


def find_by_hash(exact_hash: str) -> Optional[ArtifactRecord]:
    return store.find_artifact_by_hash(exact_hash)
