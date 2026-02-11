from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException, status
from app.api.deps import AuthDependency
from app.schemas.document import DocumentUploadResponse, DocumentInfo
from app.services.document_processor import document_processor

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse, summary="Upload and ingest a document")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    category: str = Form(default="general"),
    api_key: str = AuthDependency,
):
    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )

    metadata = {"category": category, "source": file.filename}

    # Process ingestion
    response = document_processor.process_file_content(
        filename=file.filename,
        content_bytes=content,
        metadata=metadata,
    )
    return response


@router.get("", response_model=List[DocumentInfo], summary="List all ingested documents")
async def list_documents(api_key: str = AuthDependency):
    return document_processor.list_documents()


@router.delete("/{document_id}", summary="Delete an ingested document")
async def delete_document(document_id: str, api_key: str = AuthDependency):
    success = document_processor.delete_document(document_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    return {"status": "success", "message": f"Document {document_id} removed"}
