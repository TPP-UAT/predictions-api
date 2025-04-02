from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from app.services.predict import PredictService
from typing import List

router = APIRouter()

@router.post("/predict-test")
async def predict_article(files: List[UploadFile] = File(...)):
    """
    Accepts a PDF file, extracts its text, and returns a prediction.
    """
    # Ensure the uploaded files are a PDF
    for file in files:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="PDF invalido")
    
    try:
        predictions = await PredictService.predict_files(files, is_test=True)
        return predictions

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando el archivo: {e}")

@router.post("/predict")
async def predict_article(files: List[UploadFile] = File(...)):
    """
    Accepts a PDF file, extracts its text, and returns a prediction.
    """
    # Ensure the uploaded files are a PDF
    for file in files:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="PDF invalido")
    
    try:
        predictions, recommendations = await PredictService.predict_files(files, is_test=False)
        return predictions, recommendations

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando el archivo: {e}")
