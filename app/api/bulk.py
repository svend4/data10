"""
Bulk Operations API endpoints
Массовые операции с блоками, документами и шаблонами
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
import json

from app.services import block_service, search_service
from app.models import BlockCreate, BlockUpdate, Block


router = APIRouter()


class BulkCreateRequest(BaseModel):
    """Запрос на массовое создание блоков"""
    blocks: List[BlockCreate] = Field(..., description="Список блоков для создания")
    created_by: Optional[str] = Field(None, description="Автор создания")
    create_versions: bool = Field(True, description="Создавать версии")


class BulkCreateResponse(BaseModel):
    """Ответ на массовое создание"""
    total: int = Field(..., description="Всего блоков в запросе")
    created: int = Field(..., description="Успешно создано")
    failed: int = Field(..., description="Не удалось создать")
    created_ids: List[str] = Field(default_factory=list, description="ID созданных блоков")
    errors: List[dict] = Field(default_factory=list, description="Ошибки")


class BulkUpdateRequest(BaseModel):
    """Запрос на массовое обновление"""
    updates: List[dict] = Field(..., description="Список обновлений: [{block_id, update_data}]")
    change_summary: Optional[str] = Field(None, description="Описание изменений")
    created_by: Optional[str] = Field(None, description="Автор изменений")
    create_versions: bool = Field(True, description="Создавать версии")


class BulkUpdateResponse(BaseModel):
    """Ответ на массовое обновление"""
    total: int = Field(..., description="Всего блоков в запросе")
    updated: int = Field(..., description="Успешно обновлено")
    failed: int = Field(..., description="Не удалось обновить")
    updated_ids: List[str] = Field(default_factory=list, description="ID обновлённых блоков")
    errors: List[dict] = Field(default_factory=list, description="Ошибки")


class BulkDeleteRequest(BaseModel):
    """Запрос на массовое удаление"""
    block_ids: List[str] = Field(..., description="ID блоков для удаления")
    delete_versions: bool = Field(True, description="Удалить историю версий")


class BulkDeleteResponse(BaseModel):
    """Ответ на массовое удаление"""
    total: int = Field(..., description="Всего блоков в запросе")
    deleted: int = Field(..., description="Успешно удалено")
    failed: int = Field(..., description="Не удалось удалить")
    deleted_ids: List[str] = Field(default_factory=list, description="ID удалённых блоков")
    errors: List[dict] = Field(default_factory=list, description="Ошибки")


class BulkExportResponse(BaseModel):
    """Ответ на массовый экспорт"""
    total: int = Field(..., description="Всего блоков")
    exported: int = Field(..., description="Экспортировано")
    blocks: List[dict] = Field(default_factory=list, description="Экспортированные блоки")


@router.post("/create", response_model=BulkCreateResponse)
async def bulk_create_blocks(request: BulkCreateRequest):
    """
    Массовое создание блоков

    Создаёт несколько блоков за один запрос. Каждый блок создаётся независимо,
    ошибка создания одного блока не останавливает создание остальных.

    Example:
    ```json
    POST /api/bulk/create
    {
      "blocks": [
        {
          "id": "block1",
          "type": "paragraph",
          "title": "Title 1",
          "content": "Content 1",
          "source": "Custom"
        },
        {
          "id": "block2",
          "type": "section",
          "title": "Title 2",
          "content": "Content 2",
          "source": "Custom"
        }
      ],
      "created_by": "user_123",
      "create_versions": true
    }
    ```

    Returns:
    ```json
    {
      "total": 2,
      "created": 2,
      "failed": 0,
      "created_ids": ["block1", "block2"],
      "errors": []
    }
    ```
    """
    total = len(request.blocks)
    created = 0
    failed = 0
    created_ids = []
    errors = []

    for block_data in request.blocks:
        try:
            result = await block_service.create_block(
                block_data,
                created_by=request.created_by,
                create_version=request.create_versions
            )
            if result:
                created += 1
                created_ids.append(result.id)
            else:
                failed += 1
                errors.append({
                    "block_id": block_data.id,
                    "error": "Failed to create block"
                })
        except Exception as e:
            failed += 1
            errors.append({
                "block_id": block_data.id,
                "error": str(e)
            })

    return BulkCreateResponse(
        total=total,
        created=created,
        failed=failed,
        created_ids=created_ids,
        errors=errors
    )


@router.post("/update", response_model=BulkUpdateResponse)
async def bulk_update_blocks(request: BulkUpdateRequest):
    """
    Массовое обновление блоков

    Обновляет несколько блоков за один запрос.

    Example:
    ```json
    POST /api/bulk/update
    {
      "updates": [
        {
          "block_id": "block1",
          "update_data": {
            "title": "Updated Title 1",
            "content": "Updated Content 1"
          }
        },
        {
          "block_id": "block2",
          "update_data": {
            "title": "Updated Title 2"
          }
        }
      ],
      "change_summary": "Bulk update via API",
      "created_by": "user_123",
      "create_versions": true
    }
    ```

    Returns:
    ```json
    {
      "total": 2,
      "updated": 2,
      "failed": 0,
      "updated_ids": ["block1", "block2"],
      "errors": []
    }
    ```
    """
    total = len(request.updates)
    updated = 0
    failed = 0
    updated_ids = []
    errors = []

    for update_item in request.updates:
        block_id = update_item.get("block_id")
        update_data = update_item.get("update_data")

        if not block_id or not update_data:
            failed += 1
            errors.append({
                "block_id": block_id or "unknown",
                "error": "Missing block_id or update_data"
            })
            continue

        try:
            # Создать BlockUpdate из словаря
            from app.models import BlockUpdate
            block_update = BlockUpdate(**update_data)

            result = await block_service.update_block(
                block_id,
                block_update,
                change_summary=request.change_summary,
                created_by=request.created_by,
                create_version=request.create_versions
            )

            if result:
                updated += 1
                updated_ids.append(block_id)
            else:
                failed += 1
                errors.append({
                    "block_id": block_id,
                    "error": "Block not found"
                })
        except Exception as e:
            failed += 1
            errors.append({
                "block_id": block_id,
                "error": str(e)
            })

    return BulkUpdateResponse(
        total=total,
        updated=updated,
        failed=failed,
        updated_ids=updated_ids,
        errors=errors
    )


@router.post("/delete", response_model=BulkDeleteResponse)
async def bulk_delete_blocks(request: BulkDeleteRequest):
    """
    Массовое удаление блоков

    Удаляет несколько блоков за один запрос.

    Example:
    ```json
    POST /api/bulk/delete
    {
      "block_ids": ["block1", "block2", "block3"],
      "delete_versions": true
    }
    ```

    Returns:
    ```json
    {
      "total": 3,
      "deleted": 3,
      "failed": 0,
      "deleted_ids": ["block1", "block2", "block3"],
      "errors": []
    }
    ```
    """
    total = len(request.block_ids)
    deleted = 0
    failed = 0
    deleted_ids = []
    errors = []

    for block_id in request.block_ids:
        try:
            # Удалить блок
            success = await block_service.delete_block(block_id)

            if success:
                # Удалить версии если требуется
                if request.delete_versions:
                    try:
                        from app.services.version_service import version_service
                        await version_service.delete_all_versions(block_id)
                    except Exception as e:
                        print(f"⚠️  Failed to delete versions for {block_id}: {e}")

                # Удалить из поискового индекса
                try:
                    await search_service.delete_from_index(block_id)
                except Exception as e:
                    print(f"⚠️  Failed to delete from search index {block_id}: {e}")

                deleted += 1
                deleted_ids.append(block_id)
            else:
                failed += 1
                errors.append({
                    "block_id": block_id,
                    "error": "Block not found or deletion failed"
                })
        except Exception as e:
            failed += 1
            errors.append({
                "block_id": block_id,
                "error": str(e)
            })

    return BulkDeleteResponse(
        total=total,
        deleted=deleted,
        failed=failed,
        deleted_ids=deleted_ids,
        errors=errors
    )


@router.post("/export", response_model=BulkExportResponse)
async def bulk_export_blocks(block_ids: List[str]):
    """
    Массовый экспорт блоков

    Экспортирует несколько блоков в JSON формате.

    Example:
    ```json
    POST /api/bulk/export
    ["block1", "block2", "block3"]
    ```

    Returns:
    ```json
    {
      "total": 3,
      "exported": 3,
      "blocks": [
        {
          "id": "block1",
          "type": "paragraph",
          "title": "Title 1",
          ...
        },
        ...
      ]
    }
    ```

    Можно сохранить результат как JSON файл:
    ```bash
    curl -X POST http://localhost:8000/api/bulk/export \
      -H "Content-Type: application/json" \
      -d '["block1", "block2"]' \
      > blocks_export.json
    ```
    """
    total = len(block_ids)
    exported = 0
    blocks_data = []

    for block_id in block_ids:
        try:
            block = await block_service.get_block(block_id)
            if block:
                # Конвертировать в dict для JSON сериализации
                blocks_data.append(block.dict())
                exported += 1
        except Exception as e:
            print(f"⚠️  Failed to export block {block_id}: {e}")

    return BulkExportResponse(
        total=total,
        exported=exported,
        blocks=blocks_data
    )


@router.post("/import")
async def bulk_import_blocks(file: UploadFile = File(...)):
    """
    Массовый импорт блоков из JSON файла

    Импортирует блоки из загруженного JSON файла.

    File format (JSON array):
    ```json
    [
      {
        "id": "block1",
        "type": "paragraph",
        "title": "Title 1",
        "content": "Content 1",
        "source": "Custom",
        ...
      },
      ...
    ]
    ```

    Example:
    ```bash
    curl -X POST http://localhost:8000/api/bulk/import \
      -F "file=@blocks_export.json"
    ```

    Returns:
    ```json
    {
      "message": "Bulk import completed",
      "total": 10,
      "imported": 9,
      "failed": 1,
      "imported_ids": ["block1", "block2", ...],
      "errors": [...]
    }
    ```
    """
    try:
        # Читаем содержимое файла
        content = await file.read()
        blocks_data = json.loads(content)

        if not isinstance(blocks_data, list):
            raise HTTPException(
                status_code=400,
                detail="File must contain a JSON array of blocks"
            )

        # Создаём запрос на bulk создание
        blocks_create = []
        for block_dict in blocks_data:
            try:
                # Удаляем системные поля если есть
                block_dict.pop("created_at", None)
                block_dict.pop("updated_at", None)
                block_dict.pop("version", None)

                block_create = BlockCreate(**block_dict)
                blocks_create.append(block_create)
            except Exception as e:
                print(f"⚠️  Failed to parse block: {e}")

        # Выполняем bulk создание
        request = BulkCreateRequest(
            blocks=blocks_create,
            created_by="import",
            create_versions=True
        )

        result = await bulk_create_blocks(request)

        return {
            "message": "Bulk import completed",
            "total": result.total,
            "imported": result.created,
            "failed": result.failed,
            "imported_ids": result.created_ids,
            "errors": result.errors
        }

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON file"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Import failed: {str(e)}"
        )


@router.post("/reindex")
async def bulk_reindex():
    """
    Переиндексация всех блоков в Elasticsearch

    Перестраивает поисковый индекс для всех блоков.
    Полезно после массового импорта или изменений в структуре индекса.

    Example:
    ```
    POST /api/bulk/reindex
    ```

    Returns:
    ```json
    {
      "message": "Reindexing completed",
      "total": 150,
      "indexed": 148,
      "failed": 2
    }
    ```
    """
    try:
        stats = await search_service.index_all_blocks()

        return {
            "message": "Reindexing completed",
            **stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Reindexing failed: {str(e)}"
        )
