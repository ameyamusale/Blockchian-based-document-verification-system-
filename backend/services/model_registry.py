"""Model Registry: identity, version and fingerprint of AI models."""
from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from typing import List

from models.model import ModelRecord, ModelStatus, RegisterModelRequest
from services.errors import DuplicateError, NotFoundError
from services.hashing import canonical_json_hash
from services.store import store


def _creator_id(name: str) -> str:
    # Placeholder identity until the `identities` table / wallets arrive in Phase 2.
    return "CRT-" + hashlib.sha256(name.strip().lower().encode()).hexdigest()[:10]


def register_model(req: RegisterModelRequest) -> ModelRecord:
    creator_id = _creator_id(req.creator_name)
    metadata = {
        "name": req.name.strip(),
        "version": req.version.strip(),
        "model_type": req.model_type.strip(),
        "creator_id": creator_id,
    }
    metadata_hash = canonical_json_hash(metadata)
    with store.lock:
        for existing in store.models.values():
            if existing.metadata_hash == metadata_hash:
                raise DuplicateError(
                    f"Model {req.name} v{req.version} by {req.creator_name} is already registered",
                    existing.model_id,
                )
        record = ModelRecord(
            model_id="MDL-" + uuid.uuid4().hex[:8].upper(),
            name=metadata["name"],
            version=metadata["version"],
            model_type=metadata["model_type"],
            creator_id=creator_id,
            creator_name=req.creator_name.strip(),
            description=req.description,
            # If the creator supplied a weights hash we keep it; otherwise the model
            # commitment is the metadata commitment (honest fallback, see docs).
            model_hash=(req.model_hash or metadata_hash).lower(),
            metadata_hash=metadata_hash,
            status=ModelStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
        )
        store.models[record.model_id] = record
        return record


def get_model(model_id: str) -> ModelRecord:
    record = store.models.get(model_id)
    if record is None:
        raise NotFoundError(f"Model {model_id} not found")
    return record


def list_models() -> List[ModelRecord]:
    return sorted(store.models.values(), key=lambda m: m.created_at, reverse=True)
