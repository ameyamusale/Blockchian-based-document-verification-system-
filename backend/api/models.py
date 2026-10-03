from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException

from api.deps import to_http
from models.model import ModelRecord, RegisterModelRequest
from services import model_registry
from services.errors import ModelLedgerError

router = APIRouter(prefix="/api/models", tags=["models"])


@router.post("", response_model=ModelRecord, status_code=201)
def register_model(req: RegisterModelRequest):
    """Register an AI model. Only metadata and a hash are stored, never weights."""
    try:
        return model_registry.register_model(req)
    except ModelLedgerError as exc:
        raise to_http(exc)


@router.get("", response_model=List[ModelRecord])
def list_models():
    return model_registry.list_models()


@router.get("/{model_id}", response_model=ModelRecord)
def get_model(model_id: str):
    try:
        return model_registry.get_model(model_id)
    except ModelLedgerError as exc:
        raise to_http(exc)
