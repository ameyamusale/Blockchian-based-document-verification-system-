from fastapi import FastAPI, UploadFile, File
import shutil
import os
from app.services.blockchain_routes import router as blockchain_router


app = FastAPI()
app.include_router(blockchain_router)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def home():
    return {"message": "VeriTrust AI Backend Running"}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "Document uploaded successfully",
        "filename": file.filename
    }