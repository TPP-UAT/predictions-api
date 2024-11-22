from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.predict import PredictService

router = APIRouter()

@router.post("/predict")
async def predict_article(file: UploadFile = File(...)):
    """
    Accepts a PDF file, extracts its text, and returns a prediction.
    """
    # Ensure the uploaded file is a PDF
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="PDF invalido")
    
    try:
        # call predict service
        await PredictService.predict_file(file)

        # Here you can pass the extracted text to your prediction model
        # For demonstration, we'll return the extracted text
        return {"message": "success"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando el archivo: {e}")
