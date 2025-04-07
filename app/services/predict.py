import os
from typing import List
from fastapi import File, UploadFile
from app.utils.UATMapper import UATMapper
from app.core.FilePredictor import FilePredictor
from app.core2.FilePredictor import FilePredictorv2

class PredictService:
    @staticmethod
    async def predict_files(files: List[UploadFile] = File(...), is_test: bool = False):
        mapper = UATMapper(os.path.abspath("app/data/UAT-filtered.json"))
        thesaurus = mapper.map_to_thesaurus()
        # Get the root element from the thesaurus
        root_term = thesaurus.get_by_id("1")
        predictions = {}

        for file in files:
            print("Predicting for file: ", file.filename)
            predictor = FilePredictor(root_term.get_id(), thesaurus, is_test)
            file_predictions = await predictor.predict_for_file(file)
            filename = file.filename.removesuffix(".pdf")
            predictions[filename] = file_predictions

        return predictions
    
    @staticmethod
    async def predict_filesv2(files: List[UploadFile] = File(...)):
        predictions = []

        for file in files:
            print("Predicting for file: ", file.filename)
            predictor = FilePredictorv2()
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
        