import logging
import numpy as np
from app.core.TermPrediction import TermPrediction
from app.utils.articles_parser import get_text_from_file
from app.utils.summarize_text import summarize_text

logging.basicConfig(filename='logs/predictor.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FilePredictor:
    def __init__(self, initial_term_id, thesaurus, is_test):
        self.thesaurus = thesaurus
        self.input_creators = ['abstract', 'summarize-full_text', 'summarize-summarize']
        # self.input_creators = ['abstract']
        self.initial_term_id = initial_term_id
        self.is_test = is_test
    
        self.predictions = {}
        self.predictions_by_term = {}
        self.repredictions = {}

        # For testing purposes
        self.temporal_predictions = {}
        self.remove_parent_flag = not is_test

        # For logging purposes
        self.log = logging.getLogger('predictor_logger')

    # TODO: Remove function after testing
    '''
    Prints the predictions in the console
    '''
    def print_predictions(self):
        print('----------------------------- Testing Predictions ----------------------------')

        if len(self.predictions) == 0:
            print("There are no predictions")

        else:
            for term_id, prediction in self.temporal_predictions.items():
                print(f"Term: {term_id}, Probability: {prediction}")
                self.log.info(f"Term: {term_id}, Probability: {prediction}")

            print('----------------------- Combined Predictions -------------------------------')

            for term_id, final_prediction in self.predictions_by_term.items():
                print(f"Term: {term_id}, Probability: {final_prediction}")
                self.log.info(f"Term: {term_id}, Probability: {final_prediction}")

    '''
    Predicts the terms for a given input creator
    '''
    def predict_terms(self, input_creator, text, term_id = None):
        term_prediction = TermPrediction(input_creator, self.thesaurus, self.is_test)

        # If the term_id is not provided, we use the initial_term_id
        term_to_use = term_id if term_id is not None else self.initial_term_id
        should_continue = False if term_id is not None else True

        predicted_terms = []
        # The flag remove_parent_flag is for removing the fathers with "condition" based on the probability
        predictions = term_prediction.predict_text(text, term_to_use, predicted_terms, self.remove_parent_flag, should_continue)
        return predictions
    
    def rerun_predictions(self, data_input):
        models_predicted = []
        for _, prediction in self.predictions.items():
            # The condition to rerun is that it has only one prediction and it's a summarize-summarize method
            should_rerun = False

            is_summarize = (len(prediction.get_multipliers_names()) == 1 and 'summarize' in prediction.get_multipliers_names()[0])

            if (is_summarize or len(prediction.get_multipliers_names()) == 2):
                should_rerun = True

            if (should_rerun == False):
                continue

            # Get the parents of the term
            parent_term = prediction.get_parents()[0]

            # Iterate through the input creators
            if (parent_term not in models_predicted):
                for input_creator in self.input_creators:
                    predictions = self.predict_terms(input_creator, data_input[input_creator], parent_term)
                    self.create_and_append_repredictions(predictions)

            # Add parent_term to terms_predicted
            models_predicted.append(parent_term)

    def add_prediction(self, term_id, prediction, predictions):
        # Get term name from thesaurus
        term_name = self.thesaurus.get_by_id(term_id).get_name()
        
        # Find the ponderation of the probability
        final_prediction = 0
        for pred, multiplier in zip(prediction.get_probabilities(), prediction.get_multipliers()):
            final_prediction += pred * multiplier

        predictions[term_id] = { 'probability': f"{round((final_prediction*100), 2)}%", 'name': f"{term_name} ({term_id})" }

        return predictions

    def combine_predictions(self):
        # Generate prediction object with the final probabilities combined

        final_predictions = {}
        # First, we need to add the "repredictions"
        for term_id, prediction in self.repredictions.items():
            print(f"Repredictions: {term_id}, probs: {np.array(prediction.get_probabilities())}, multipliers: {np.array(prediction.get_multipliers())}")
            final_predictions = self.add_prediction(term_id, prediction, final_predictions)

        # Then, we add the predictions
        for term_id, prediction in self.predictions.items():
            # If the prediction is already in the predictions, we skip it
            if term_id in final_predictions:
                continue

            # Get term name from thesaurus
            final_predictions = self.add_prediction(term_id, prediction, final_predictions)

        sorted_predictions = dict(sorted(final_predictions.items(), key=lambda x: x[1]['probability'], reverse=True))

        self.predictions_by_term = sorted_predictions

        # We want the info for the prediction for testing purposes
        for term_id, prediction in self.predictions.items():
            self.temporal_predictions[term_id] = {
                'probabilities': prediction.get_probabilities(),
                'multipliers': prediction.get_multipliers(),
                'multipliersNames': prediction.get_multipliers_names(),
                'parent': prediction.get_parents()
            }

    '''
    Combines the predictions from different input creators and generates the final prediction
    '''
    def create_and_append_predictions(self, predictions):
        # Combine predictions from different input creators if the term is already in the predictions
        for prediction in predictions:
            if prediction.get_term() not in self.predictions:
                self.predictions[prediction.get_term()] = prediction
            else:
                probability = prediction.get_probabilities()[0]
                self.predictions[prediction.get_term()].add_probability(probability)
                self.predictions[prediction.get_term()].add_multiplier(prediction.get_multipliers()[0])
                self.predictions[prediction.get_term()].add_multiplier_name(prediction.get_multipliers_names()[0])
                self.predictions[prediction.get_term()].add_parent(prediction.get_parents()[0])

    def create_and_append_repredictions(self, predictions):
        # Combine predictions from different input creators if the term is already in the predictions
        for prediction in predictions:
            if prediction.get_term() not in self.repredictions:
                self.repredictions[prediction.get_term()] = prediction
            else:
                probability = prediction.get_probabilities()[0]
                self.repredictions[prediction.get_term()].add_probability(probability)
                self.repredictions[prediction.get_term()].add_multiplier(prediction.get_multipliers()[0])
                self.repredictions[prediction.get_term()].add_multiplier_name(prediction.get_multipliers_names()[0])
                self.repredictions[prediction.get_term()].add_parent(prediction.get_parents()[0])

    '''
    Extracts the abstract and full text from a file and predicts the terms
    '''
    async def predict_for_file(self, file):
        abstract, full_text = await get_text_from_file(file)
        summarized_text = summarize_text(full_text, 0.25, max_sentences=100, additional_stopwords={"specific", "unnecessary", "technical"})
        data_input = {"abstract": abstract, "summarize-summarize": summarized_text, "summarize-full_text": full_text}
        # data_input = { "abstract": abstract }

        # Iterate through the input creators
        for input_creator in self.input_creators:
            self.log.info(f"Predicting with input creator: {input_creator}")
            predictions = self.predict_terms(input_creator, data_input[input_creator])
            self.create_and_append_predictions(predictions)

        self.log.info(f"----- Rerunning predictions -----")
        print("----- Rerunning predictions -----")

        self.rerun_predictions(data_input)
        self.combine_predictions()
        self.print_predictions()

        # Return the final predictions (It depends on the is_test flag)
        if self.is_test:
            return self.temporal_predictions
        else:
            return self.predictions_by_term
