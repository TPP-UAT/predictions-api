from app.database.Keyword import Keyword
import os
from app.utils.UATMapper import UATMapper
import logging

logging.basicConfig(filename='logs/recommender.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FileRecommender:
    def __init__(self, db):
        self.files_db = db
        self.log = logging.getLogger('recommender_logger')

        # Initialize the thesaurus
        mapper = UATMapper(os.path.abspath("app/data/UAT-filtered.json"))
        self.thesaurus = mapper.map_to_thesaurus()

    def recommend_documents(self, predictions_by_term):
        print('----------------------------- Testing Recommendations ----------------------------')
        results = []

        if len(predictions_by_term) == 0:
            print("No term_id predicted for the file, therefore no documents to recommend")
            return {}
        
        # Get the ids from the predicted terms
        term_ids = [prediction.get_term() for prediction in predictions_by_term]
        term_files_ocurencies = self.top_keywords_files_ocurrences(term_ids, 5)

        print(f"Predicted Keywords: {term_ids}")
        print(f"Term Files Ocurrencies: {term_files_ocurencies}")

        recommended_file_ids = [term_file_ocurrencies[0] for term_file_ocurrencies in term_files_ocurencies]

        # Get original keywords for each file
        for doc in recommended_file_ids:
            keywords = self.get_keywords_by_file_id(doc)
            keyword_ids = [kw.keyword_id for kw in keywords]

            # Convert to int the term ids
            term_ids = [int(k) for k in term_ids]

            # Check which keywords are the same and which are different
            same = [kid for kid in keyword_ids if kid in term_ids]
            other = [kid for kid in keyword_ids if kid not in term_ids]

            for same_term in same:
                # Get the name of the term
                term = self.thesaurus.get_by_id(str(same_term))
                if term:
                    name = term.get_name() + "(" + str(same_term) + ")"
                    same[same.index(same_term)] = name

            for other_term in other:
                # Get the name of the term
                term = self.thesaurus.get_by_id(str(other_term))
                if term:
                    name = term.get_name() + "(" + str(other_term) + ")"
                    other[other.index(other_term)] = name

            results.append({
                "id": doc,
                "same_keywords": same,
                "other_keywords": other
            })

        print("results: ", results)
        return results
    
    def top_keywords_files_ocurrences(self, keywords, limit):
        keyword_table_db = Keyword(self.files_db)

        return keyword_table_db.get_keywords_files_ocurrences(keywords, limit)
    
    def get_keywords_by_file_id(self, file_id):
        keyword_table_db = Keyword(self.files_db)

        return keyword_table_db.get_by_file_id(file_id)
    