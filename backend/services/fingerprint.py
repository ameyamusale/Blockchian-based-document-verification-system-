"""Robust / content fingerprint (Phase 4).

Phase 1 only defines the interface so the rest of the code can depend on it.
The exact hash answers "are these the same bytes?"; the robust fingerprint will
answer "is this the same content after an allowed transformation?" and is
supporting evidence only, never proof.
"""
from __future__ import annotations

from typing import Optional

from models.artifact import ArtifactType

IMPLEMENTED = False


def compute_robust_fingerprint(data: bytes, artifact_type: ArtifactType = ArtifactType.IMAGE) -> Optional[str]:
    """Returns None until Phase 4 (None means "not computed", never "no match")."""
    return None
