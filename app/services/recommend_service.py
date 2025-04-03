import os
from typing import List
from fastapi import File, HTTPException, UploadFile
from app.services.predict import PredictService
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

class RecommendService:
    @staticmethod
    async def recommend_files(files: List[UploadFile] = File(...)):
        
        try:
            predictions = await PredictService.predict_files(files, is_test=False)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error procesando el archivo: {e}")
        
        recommendations = {}

        for filename in predictions:
            print("Recommending for file: ", filename)
            recommender = FileRecommender(database)
            recommended_docs = recommender.recommend_documents(predictions[filename])
            recommendations[filename] = {"recommended_documents": recommended_docs}
            
        return recommendations
        