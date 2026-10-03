"""Signed provenance claims (Phase 4).

Rule: the *private key* signs. Biometrics (Phase 8) only authorise use of the key.
Until Phase 4 every verification reports signature_valid = None ("not checked").
"""
from __future__ import annotations

from typing import Optional

from models.provenance import ProvenanceEvent

IMPLEMENTED = False


def verify_event_signature(event: ProvenanceEvent) -> Optional[bool]:
    return None
