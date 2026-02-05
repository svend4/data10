"""
API endpoints для работы с блоками
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.models import BlockCreate, BlockUpdate, BlockResponse
from app.services import block_service

router = APIRouter()


@router.post("/", response_model=BlockResponse, status_code=201)
async def create_block(block: BlockCreate):
    """Создать новый блок"""
    result = await block_service.create_block(block)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create block")
    return result


@router.get("/{block_id}", response_model=BlockResponse)
async def get_block(block_id: str):
    """Получить блок по ID"""
    block = await block_service.get_block(block_id)
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    return block


@router.put("/{block_id}", response_model=BlockResponse)
async def update_block(block_id: str, update: BlockUpdate):
    """Обновить блок"""
    block = await block_service.update_block(block_id, update)
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    return block


@router.delete("/{block_id}", status_code=204)
async def delete_block(block_id: str):
    """Удалить блок"""
    success = await block_service.delete_block(block_id)
    if not success:
        raise HTTPException(status_code=404, detail="Block not found")


@router.get("/", response_model=List[BlockResponse])
async def list_blocks(
    source: Optional[str] = Query(None, description="Фильтр по источнику"),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0)
):
    """Получить список блоков"""
    blocks = await block_service.list_blocks(source=source, limit=limit, offset=offset)
    return blocks


@router.get("/{block_id}/related", response_model=List[BlockResponse])
async def get_related_blocks(
    block_id: str,
    max_depth: int = Query(2, ge=1, le=5)
):
    """Получить связанные блоки через граф"""
    blocks = await block_service.get_related_blocks(block_id, max_depth)
    return blocks
