import os
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.gvs import UPLOADS_DIR
from app.types import GeneralDict

file_router = APIRouter(prefix="/files", tags=["File Management"])

# Define the directory where files will be stored
UPLOAD_DIR = Path(UPLOADS_DIR)


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
@file_router.get("/download/{file_id}")
async def download_file(file_id: str) -> FileResponse:
    file_path = get_file_path(file_id)

    # Check if the file exists
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Return the file as a download response
    return FileResponse(file_path)


# File Deletion Route
@file_router.delete("/delete/{file_id}")
async def delete_file(file_id: str) -> GeneralDict:
    file_path = get_file_path(file_id)

    # Check if the file exists
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Delete the file
    os.remove(file_path)

    return {"message": "File deleted successfully"}
