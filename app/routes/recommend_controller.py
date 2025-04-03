from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from app.services.recommend_service import RecommendService
from typing import List

router = APIRouter()

@router.post("/recommend")
async def recommend_articles(files: List[UploadFile] = File(...)):
    """
    Accepts a PDF file, extracts its text, and returns a prediction.
    """
    # Ensure the uploaded files are a PDF
    for file in files:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="PDF invalido")
    
    try:
        recommendations = await RecommendService.recommend_files(files)
        return recommendations

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando el archivo: {e}")
