"""In-memory persistence stub.

Phase 1 intentionally keeps data in process memory (it resets on restart).
Phase 2 replaces this module with a real database behind the same methods.
"""
from __future__ import annotations

import threading
from typing import Dict, List, Optional

from models.artifact import ArtifactRecord
from models.model import ModelRecord
from models.provenance import ProvenanceEvent


class InMemoryStore:
    def __init__(self) -> None:
        self.lock = threading.RLock()
        self.reset()

    def reset(self) -> None:
        with self.lock:
            self.models: Dict[str, ModelRecord] = {}
            self.artifacts: Dict[str, ArtifactRecord] = {}
            self.events: Dict[str, ProvenanceEvent] = {}
            self.artifact_by_hash: Dict[str, str] = {}

    def events_for_child(self, artifact_id: str) -> List[ProvenanceEvent]:
        return [e for e in self.events.values() if e.child_artifact_id == artifact_id]

    def events_for_artifact(self, artifact_id: str) -> List[ProvenanceEvent]:
        return [
            e for e in self.events.values()
            if e.child_artifact_id == artifact_id or e.parent_artifact_id == artifact_id
        ]

    def find_artifact_by_hash(self, exact_hash: str) -> Optional[ArtifactRecord]:
        artifact_id = self.artifact_by_hash.get(exact_hash.lower())
        return self.artifacts.get(artifact_id) if artifact_id else None


store = InMemoryStore()
