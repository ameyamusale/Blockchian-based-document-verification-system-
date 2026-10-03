"""Conflict Detector (Phase 7).

Phase 1 allows a single creating event per artifact, so contradictory origin
claims cannot be stored yet. Phase 7 relaxes that and fills this in.
"""
from __future__ import annotations

from typing import List


def detect_conflicts(artifact_id: str) -> List[str]:
    return []
