from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
from uuid import uuid4
from pathlib import Path
from app.types import GeneralDict

file_router = APIRouter(prefix="/files", tags=["File Management"])

# Define the directory where files will be stored
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# Helper function to get the file path from the ID
def get_file_path(file_id: str) -> Path:
    return UPLOAD_DIR / file_id


# File Upload Route
@file_router.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> GeneralDict:
    # Generate a unique file ID (UUID) for the uploaded file
    file_id = str(uuid4())

    # Define the path to save the file
    file_path = UPLOAD_DIR / file_id

    # Save the uploaded file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # Return the file ID for later reference
    return {"file_id": file_id}


# File Download Route
@file_router.get("/{file_id}/download")
async def download_file(file_id: str) -> FileResponse:
    file_path = get_file_path(file_id)

    # Check if the file exists
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Return the file as a download response
    return FileResponse(file_path)


# File Deletion Route
@file_router.delete("/{file_id}/delete")
async def delete_file(file_id: str) -> GeneralDict:
    file_path = get_file_path(file_id)

    # Check if the file exists
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Delete the file
    os.remove(file_path)

    return {"message": "File deleted successfully"}
