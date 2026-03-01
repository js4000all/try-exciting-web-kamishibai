from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException

from .models import SaveDataV0, SaveWriteResponse
from .projects import PROJECTS

router = APIRouter(prefix="/api/v0/projects/{project_id}/saves", tags=["saves"])

SAVES: dict[tuple[str, str], tuple[SaveDataV0, datetime]] = {}


@router.put("/{slot}", response_model=SaveWriteResponse)
def put_save(project_id: str, slot: str, payload: SaveDataV0) -> SaveWriteResponse:
    if project_id not in PROJECTS:
        raise HTTPException(status_code=404, detail="Project not found")

    saved_at = datetime.now(tz=UTC)
    SAVES[(project_id, slot)] = (payload, saved_at)
    return SaveWriteResponse(project_id=project_id, slot=slot, saved_at=saved_at)


@router.get("/{slot}", response_model=SaveDataV0)
def get_save(project_id: str, slot: str) -> SaveDataV0:
    if project_id not in PROJECTS:
        raise HTTPException(status_code=404, detail="Project not found")

    save_item = SAVES.get((project_id, slot))
    if save_item is None:
        raise HTTPException(status_code=404, detail="Save not found")

    return save_item[0]
