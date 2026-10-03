"""Transformation Engine (Phase 5/6).

Phase 1 only owns the vocabulary. Deep checks ("does this RESIZE really relate
parent and child?") need the robust fingerprint from Phase 4.
"""
from __future__ import annotations

from typing import Optional

from models.provenance import ProvenanceAction, ProvenanceEvent

# Actions that legitimately change the bytes but keep the content recognisable.
CONTENT_PRESERVING = {
    ProvenanceAction.UPSCALED,
    ProvenanceAction.RESIZED,
    ProvenanceAction.CROPPED,
    ProvenanceAction.RE_ENCODED,
    ProvenanceAction.FILTERED,
    ProvenanceAction.EDITED,
}


def check_transformation(event: ProvenanceEvent) -> Optional[bool]:
    """None = not checked. Never returns True before a real check exists."""
    return None
