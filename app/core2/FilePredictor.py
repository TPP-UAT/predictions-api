import os
import logging
from app.utils.UATMapper import UATMapper
from app.core2.TermPrediction import TermPredictionv2
from app.utils.articles_parser import get_text_from_file
from app.utils.summarize_text import summarize_text
from app.utils.accuracy import evaluate_hierarchical_metrics

logging.basicConfig(filename='logs/predictor.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FilePredictorv2:
    def __init__(self):
        # Initialize the thesaurus
        mapper = UATMapper(os.path.abspath("app/data/UAT-filtered.json"))
        self.thesaurus = mapper.map_to_thesaurus()

        # For logging purposes
        self.log = logging.getLogger('predictor_logger')

    # TODO: Remove function after testing
    '''
    Prints the predictions in the console
    '''
    def print_predictions(self, predictions):
        if len(predictions) == 0:
            print("There are no predictions")

        else:
            for prediction in predictions:
                print(f"Term: {prediction.get_term()}, Probability: {prediction.get_combined_probability()}, probabilites: {prediction.get_probabilities()}, multipliersNames: {prediction.get_multipliers_names()}, parent: {prediction.get_parents()}")

    def find_paths(self, term_ids, best_paths, terms_in_path, overwrite_existing=False, fill_missing=False):
        eleven_children = ["104", "1145", "1476", "1529", "1583", "343", "486", "563", "739", "804", "847"]
        distances = {}

        for term_id in term_ids:
            for original_child in eleven_children:
                # Find the shortest path between predicted and original
                shortest_path = self.thesaurus.find_shortest_path(original_child, term_id)

                if shortest_path:
                    distances[(term_id, original_child)] = (len(shortest_path) - 1, shortest_path)
                else:
                    # If no path is found, return None for that pair
                    distances[(term_id, original_child)] = (None, "No path found")

        for term_id in term_ids:
            best_path_for_term = None
            best_length = float("inf")

            for original_child in eleven_children:
                key = (term_id, original_child)
                dist, path = distances.get(key, (None, None))
                if not isinstance(path, list):
                    continue

                if any(t in path and t != term_id for t in terms_in_path):
                    if len(path) < best_length:
                        best_path_for_term = path
                        best_length = len(path)

                    # Check if the path contains any of the terms in the path
                    # and if so, update the best_paths dictionary
                    for t in terms_in_path:
                        if t in path and t != term_id:
                            # solo sobreescribir si no existe o el nuevo camino es más corto
                            if t not in best_paths or len(path) < len(best_paths[t]):
                                best_paths[t] = path

            if best_path_for_term:
                if (
                    term_id not in best_paths or
                    overwrite_existing and len(best_path_for_term) < len(best_paths[term_id])
                ):
                    best_paths[term_id] = best_path_for_term         

            elif fill_missing and term_id not in best_paths:
                # Try to at least fill *some* path if none match the filter
                for original_child in eleven_children:
                    key = (term_id, original_child)
                    dist, path = distances.get(key, (None, None))
                    if isinstance(path, list):
                        best_paths[term_id] = path
                        break

        return best_paths

    '''
    Calculate the accuracy for the file
    '''
    def calculate_accuracy(self, predictions, keywords_ids):
        # Get the ids of the predicted terms
        predicted_ids = [prediction.get_term() for prediction in predictions]
        print("Predicted IDs: ", predicted_ids)
        print("Keywords IDs: ", keywords_ids)

        best_paths = {}

        best_paths = self.find_paths(keywords_ids, best_paths, predicted_ids)
        best_paths = self.find_paths(predicted_ids, best_paths, keywords_ids, overwrite_existing=True, fill_missing=True)

        # Filter best_paths to only include those that contain a predicted_id
        best_paths = {pid: path for pid, path in best_paths.items() if pid in predicted_ids}

        # If there's a prediction the same as a keyword, set the path to None
        for kid in keywords_ids:
            if kid in best_paths:
                best_paths[kid] = None

        print("----------- Best Paths Including a Keyword ID -----------")
        for pid, path in best_paths.items():
            print(f"{pid}: {path}")

        # Calculate the accuracy
        accuracy = evaluate_hierarchical_metrics(keywords_ids, best_paths)
        print("----> Accuracy: ", accuracy)
        return accuracy
        
    '''
    Predicts the terms for a given file
    '''
    def predict_terms(self, data_input):
        term_prediction = TermPredictionv2(data_input, self.thesaurus)

        # Initial term ID
        root_term = self.thesaurus.get_by_id("1")
        level = 0

        predicted_terms = []
        predictions = term_prediction.predict_text(predicted_terms, root_term.get_id(), level)

        if (len(predictions) < 3):
            term_prediction.reduce_threshold()
            predictions = term_prediction.predict_text(predicted_terms, root_term.get_id(), level)
        return predictions

    '''
    Extracts the abstract and full text from a file and predicts the terms
    '''
    async def predict_for_file(self, file):
        self.log.info("\n\n")
        self.log.info(f"****** Starting prediction for file: {file.filename} ********")
        # Get the text from the file
        abstract, full_text, keywords = await get_text_from_file(file)
        summarized_text = summarize_text(full_text, 0.25, max_sentences=100, additional_stopwords={"specific", "unnecessary", "technical"})
        # If we can't extract the abstract, we use the summarized text
        abstract_text = abstract if abstract else summarized_text
        data_input = {"abstract": abstract_text, "summarize-summarize": summarized_text, "summarize-full_text": full_text}
        print("Keywords: ", keywords)

        predictions = self.predict_terms(data_input)

        print("----------------------------- Predictions ----------------------------")
        self.print_predictions(predictions)

        accuracy = 0
        if (keywords):
            accuracy = self.calculate_accuracy(predictions, keywords)

        return accuracy, predictions
