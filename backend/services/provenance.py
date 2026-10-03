"""Provenance event system and lineage reconstruction."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List

from models.provenance import (
    CreateEventRequest,
    Lineage,
    LineageStep,
    ProvenanceAction,
    ProvenanceEvent,
)
from services.artifact_registry import get_artifact
from services.errors import DuplicateError, ValidationFailure
from services.hashing import canonical_json_hash
from services.model_registry import get_model
from services.store import store


def add_event(req: CreateEventRequest) -> ProvenanceEvent:
    with store.lock:
        child = get_artifact(req.child_artifact_id)

        if req.action == ProvenanceAction.GENERATED:
            if req.parent_artifact_id:
                raise ValidationFailure("A GENERATED event has no parent artifact")
            if not req.model_id:
                raise ValidationFailure("A GENERATED event needs the originating model_id")
        else:
            if not req.parent_artifact_id:
                raise ValidationFailure(f"A {req.action.value} event needs a parent_artifact_id")
            if req.parent_artifact_id == req.child_artifact_id:
                raise ValidationFailure("An artifact cannot be its own parent")
            get_artifact(req.parent_artifact_id)
            if not (req.model_id or req.application_id):
                raise ValidationFailure("Name the model_id or application_id that performed the action")

        if req.model_id:
            get_model(req.model_id)

        existing = store.events_for_child(child.artifact_id)
        if existing:
            raise DuplicateError(
                f"{child.artifact_id} already has a creating event ({existing[0].event_id}). "
                "Competing claims are handled by the Conflict Detector in Phase 7.",
                existing[0].event_id,
            )

        event = ProvenanceEvent(
            event_id="EVT-" + uuid.uuid4().hex[:8].upper(),
            parent_artifact_id=req.parent_artifact_id,
            child_artifact_id=req.child_artifact_id,
            action=req.action,
            model_id=req.model_id,
            application_id=req.application_id,
            metadata_hash=canonical_json_hash(req.metadata),  # private details are NOT stored
            created_at=datetime.now(timezone.utc),
        )
        store.events[event.event_id] = event
        return event


def events_for_artifact(artifact_id: str) -> List[ProvenanceEvent]:
    get_artifact(artifact_id)
    return sorted(store.events_for_artifact(artifact_id), key=lambda e: e.created_at)


def list_events() -> List[ProvenanceEvent]:
    return sorted(store.events.values(), key=lambda e: e.created_at, reverse=True)


def build_lineage(artifact_id: str) -> Lineage:
    """Walk parent links back to the root. Returns steps ordered root -> artifact."""
    get_artifact(artifact_id)
    steps: List[LineageStep] = []
    issues: List[str] = []
    seen = set()
    current = artifact_id
    root_reached = False

    while current:
        if current in seen:
            issues.append(f"Cycle detected at {current}")
            break
        seen.add(current)
        events = store.events_for_child(current)
        if not events:
            steps.append(LineageStep(artifact_id=current, event=None))
            issues.append(f"{current} has no recorded provenance event")
            break
        event = events[0]
        steps.append(LineageStep(artifact_id=current, event=event))
        if event.parent_artifact_id is None:
            root_reached = event.action == ProvenanceAction.GENERATED
            break
        if event.parent_artifact_id not in store.artifacts:
            issues.append(f"Parent {event.parent_artifact_id} of {current} does not exist")
            break
        current = event.parent_artifact_id

    steps.reverse()
    return Lineage(
        artifact_id=artifact_id,
        steps=steps,
        depth=max(len(steps) - 1, 0),
        root_reached=root_reached,
        issues=issues,
    )
