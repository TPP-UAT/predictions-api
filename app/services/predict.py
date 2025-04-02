import os
from typing import List
from fastapi import File, UploadFile
from app.utils.UATMapper import UATMapper
from app.core.FilePredictor import FilePredictor
from app.core.FileRecommender import FileRecommender
from app.database.Database import Database

# Initialize the database
# db_url = os.getenv('DB_URL')
db_url = "postgresql://user:password@localhost:5432/UAT_IA"
print("DB URL:", db_url)
database = Database(db_url)
engine = database.get_engine()
connection = engine.connect()
database.init_db()

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
            recommender = FileRecommender(database)
            file_predictions = await predictor.predict_for_file(file)
            recommender_docs = recommender.recommend_documents(file_predictions)
            filename = file.filename.removesuffix(".pdf")
            predictions[filename] = file_predictions

        return predictions, recommender_docs
        