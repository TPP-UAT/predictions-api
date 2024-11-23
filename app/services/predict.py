import os
import fitz
from fastapi import File, UploadFile
from app.utils.UATMapper import UATMapper
from app.core.FilePredictor import FilePredictor

class PredictService:
    @staticmethod
    async def predict_file(file: UploadFile = File(...)):
        mapper = UATMapper(os.path.abspath("app/data/UAT-filtered.json"))
        thesaurus = mapper.map_to_thesaurus()
        # Get the root element from the thesaurus
        root_term = thesaurus.get_by_id("1")
        predictions = {}

        predictor = FilePredictor(root_term.get_id(), thesaurus)
        # In the future, we could iterate over more than one file
        file_predictions = await predictor.predict_for_file(file)

        filename = file.filename.removesuffix(".pdf")
        predictions[filename] = file_predictions
        return predictions
        