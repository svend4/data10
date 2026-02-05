"""
API endpoints для работы с документами
"""

from typing import List
from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import PlainTextResponse, StreamingResponse
from app.models import AssemblyRequest, AssemblyResponse, DocumentResponse
from app.services import assembly_service

router = APIRouter()


@router.post("/assemble", response_model=AssemblyResponse, status_code=201)
async def assemble_document(request: AssemblyRequest):
    """Собрать документ из блоков по шаблону"""
    try:
        result = await assembly_service.assemble_document(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assembly failed: {str(e)}")


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str):
    """Получить документ по ID"""
    document = await assembly_service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0)
):
    """Получить список документов"""
    documents = await assembly_service.list_documents(limit=limit, offset=offset)
    return documents


@router.get("/{document_id}/export/text", response_class=PlainTextResponse)
async def export_document_text(document_id: str):
    """Экспорт документа в текстовый формат"""
    try:
        text = await assembly_service.render_document_text(document_id)
        return Response(content=text, media_type="text/plain")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{document_id}/export/markdown", response_class=PlainTextResponse)
async def export_document_markdown(document_id: str):
    """Экспорт документа в Markdown"""
    try:
        markdown = await assembly_service.export_document_markdown(document_id)
        return Response(content=markdown, media_type="text/markdown")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{document_id}/export/docx")
async def export_document_docx(document_id: str):
    """Экспорт документа в DOCX (Microsoft Word)"""
    try:
        buffer = await assembly_service.export_document_docx(document_id)
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename={document_id}.docx"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
