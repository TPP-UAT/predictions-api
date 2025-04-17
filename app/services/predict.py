import os
from typing import List
from fastapi import File, UploadFile
from app.core.FilePredictor import FilePredictor

class PredictService:  
    @staticmethod
    async def predict_files(files: List[UploadFile] = File(...)):
        predictions = []

        for file in files:
            print("Predicting for file: ", file.filename)
            predictor = FilePredictor()
            accuracy, file_predictions = await predictor.predict_for_file(file)

            filename = file.filename.removesuffix(".pdf")

            # Create an object with the filename, accuracy, and the array of predictions
            file_predictions = {
                "filename": filename,
                "accuracy": accuracy,
                "predictions": file_predictions
            }
            predictions.append(file_predictions)

        return predictions
        