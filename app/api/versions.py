"""
Version API endpoints
Управление версиями блоков и история изменений
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services import version_service
from app.models import BlockVersion, VersionDiff, VersionHistory


router = APIRouter()


class RestoreVersionRequest(BaseModel):
    """Запрос на восстановление версии"""
    version: int
    created_by: Optional[str] = None


class VersionStatsResponse(BaseModel):
    """Статистика по версиям"""
    total_versions: int
    blocks_with_versions: int
    average_versions_per_block: float


@router.get("/{block_id}/history", response_model=VersionHistory)
async def get_version_history(
    block_id: str,
    limit: int = Query(10, ge=1, le=100, description="Максимальное количество версий")
):
    """
    Получить историю версий блока

    Возвращает список всех версий блока в обратном хронологическом порядке
    (самые новые версии первыми).

    Example:
    ```
    GET /api/versions/sgb9_para5/history?limit=10
    ```

    Returns:
    ```json
    {
      "block_id": "sgb9_para5",
      "total_versions": 3,
      "current_version": 3,
      "versions": [
        {
          "version": 3,
          "title": "Updated title",
          "created_at": "2024-01-20T16:45:00",
          "change_summary": "Fixed typo",
          "is_current": true
        },
        ...
      ]
    }
    ```
    """
    try:
        history = await version_service.get_version_history(block_id, limit)
        if history.total_versions == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No version history found for block {block_id}"
            )
        return history
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{block_id}/versions/{version}", response_model=BlockVersion)
async def get_specific_version(block_id: str, version: int):
    """
    Получить конкретную версию блока

    Возвращает snapshot блока для указанной версии.

    Example:
    ```
    GET /api/versions/sgb9_para5/versions/2
    ```

    Returns полный BlockVersion с содержимым блока на момент этой версии.
    """
    try:
        block_version = await version_service.get_version(block_id, version)
        if not block_version:
            raise HTTPException(
                status_code=404,
                detail=f"Version {version} not found for block {block_id}"
            )
        return block_version
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{block_id}/current", response_model=BlockVersion)
async def get_current_version(block_id: str):
    """
    Получить текущую версию блока

    Example:
    ```
    GET /api/versions/sgb9_para5/current
    ```

    Returns текущую (is_current=true) версию блока.
    """
    try:
        current = await version_service.get_current_version(block_id)
        if not current:
            raise HTTPException(
                status_code=404,
                detail=f"No current version found for block {block_id}"
            )
        return current
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{block_id}/compare", response_model=VersionDiff)
async def compare_versions(
    block_id: str,
    old_version: int = Query(..., description="Номер старой версии"),
    new_version: int = Query(..., description="Номер новой версии")
):
    """
    Сравнить две версии блока

    Возвращает различия между двумя версиями блока по основным полям
    (type, title, content, source, level).

    Example:
    ```
    GET /api/versions/sgb9_para5/compare?old_version=1&new_version=2
    ```

    Returns:
    ```json
    {
      "block_id": "sgb9_para5",
      "old_version": 1,
      "new_version": 2,
      "changes": {
        "title": {
          "old": "Old title",
          "new": "New title"
        },
        "content": {
          "old": "Old content...",
          "new": "New content..."
        }
      }
    }
    ```
    """
    try:
        diff = await version_service.compare_versions(
            block_id,
            old_version,
            new_version
        )
        if not diff:
            raise HTTPException(
                status_code=404,
                detail=f"Could not compare versions - one or both versions not found"
            )
        return diff
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{block_id}/restore", status_code=200)
async def restore_version(block_id: str, request: RestoreVersionRequest):
    """
    Восстановить блок к предыдущей версии

    Создаёт новую версию блока на основе указанной старой версии.
    Это НЕ удаляет текущую версию, а создаёт новую с содержимым из старой.

    Example:
    ```json
    POST /api/versions/sgb9_para5/restore
    {
      "version": 2,
      "created_by": "user_123"
    }
    ```

    Returns:
    ```json
    {
      "message": "Block restored to version 2",
      "block_id": "sgb9_para5",
      "old_version": 2,
      "new_version": 4
    }
    ```
    """
    try:
        restored_block = await version_service.restore_version(
            block_id,
            request.version,
            request.created_by
        )

        if not restored_block:
            raise HTTPException(
                status_code=404,
                detail=f"Could not restore - version {request.version} not found for block {block_id}"
            )

        return {
            "message": f"Block restored to version {request.version}",
            "block_id": block_id,
            "old_version": request.version,
            "new_version": restored_block.version
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{block_id}/versions/{version}")
async def delete_version(block_id: str, version: int):
    """
    Удалить версию блока

    Удаляет конкретную версию из истории.
    ВАЖНО: Нельзя удалить текущую версию (is_current=true).

    Example:
    ```
    DELETE /api/versions/sgb9_para5/versions/1
    ```

    Returns:
    ```json
    {
      "message": "Version 1 deleted successfully",
      "block_id": "sgb9_para5"
    }
    ```
    """
    try:
        success = await version_service.delete_version(block_id, version)
        if not success:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete version {version} - it may be current version or not exist"
            )

        return {
            "message": f"Version {version} deleted successfully",
            "block_id": block_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{block_id}/all")
async def delete_all_versions(block_id: str):
    """
    Удалить все версии блока

    Удаляет всю историю версий для блока.
    Используйте с осторожностью!

    Example:
    ```
    DELETE /api/versions/sgb9_para5/all
    ```

    Returns:
    ```json
    {
      "message": "All versions deleted",
      "block_id": "sgb9_para5",
      "deleted_count": 5
    }
    ```
    """
    try:
        deleted_count = await version_service.delete_all_versions(block_id)
        return {
            "message": "All versions deleted",
            "block_id": block_id,
            "deleted_count": deleted_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=VersionStatsResponse)
async def get_version_stats():
    """
    Получить статистику по версиям

    Возвращает общую статистику по системе версионирования:
    - Общее количество версий
    - Количество блоков с версиями
    - Среднее количество версий на блок

    Example:
    ```
    GET /api/versions/stats
    ```

    Returns:
    ```json
    {
      "total_versions": 150,
      "blocks_with_versions": 45,
      "average_versions_per_block": 3.33
    }
    ```
    """
    try:
        stats = await version_service.get_stats()
        return VersionStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
