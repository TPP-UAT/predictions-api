from app.database.Keyword import Keyword
import logging

logging.basicConfig(filename='logs/recommender.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FileRecommender:
    def __init__(self, db):
        self.files_db = db
        self.log = logging.getLogger('recommender_logger')


    def recommend_documents(self, predictions_by_term):
      print('----------------------------- Testing Recommendations ----------------------------')

      if len(predictions_by_term.items()) == 0:
        print("No term_id predicted for the file, therefore no documents to recommend")
        return {}

      predicted_keywords = predictions_by_term.keys()
      term_files_ocurencies = self.top_keywords_files_ocurrences(predicted_keywords, 10)

      print(f"Predicted Keywords: {predicted_keywords}")
      print(f"Term Files Ocurrencies: {term_files_ocurencies}")

      recommended_file_ids = [term_file_ocurrencies[0] for term_file_ocurrencies in term_files_ocurencies]

      return recommended_file_ids
    
    def top_keywords_files_ocurrences(self, keywords, limit):
      keyword_table_db = Keyword(self.files_db)

      return keyword_table_db.get_keywords_files_ocurrences(keywords, limit)