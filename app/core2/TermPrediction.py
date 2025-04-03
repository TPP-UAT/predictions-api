import glob
import logging
import spacy
from app.utils.input_creators import get_prediction_multiplier
from app.models.Prediction import Prediction
from app.models.CombinedPrediction import CombinedPrediction

logging.basicConfig(filename='logs/predictor.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TermPredictionv2:
    def __init__(self, data_input, thesaurus):
        self.data_input = data_input
        self.thesaurus = thesaurus

        # self.input_creators = ['abstract', 'summarize-full_text', 'summarize-summarize']
        self.input_creators = ['abstract', 'summarize-full_text', 'summarize-summarize']

        # Threshold for prediction
        self.CHILDREN_THRESHOLD = 0.4
        self.PREDICTION_THRESHOLD = 0.8

        self.nlp = None
        self.log = logging.getLogger('predictor_logger')

        # Array to store the 

        # Array to store the predicted term ids
        self.predicted_term_ids = []

    """
    Retrieve and load the saved spaCy model for a specific term.
    The model should have been previously saved to disk.
    """
    def get_model_for_term(self, term_id, input_creator):
        # Because summarize has two different data inputs, we need to modify the input creator based on the "-"
        input_creator = input_creator.split("-")[0]
        model_path = f"./models/{input_creator}/{term_id}"
        
        try:
            # Check if the model path exists, then load the model
            if not glob.glob(model_path):
                self.log.error(f"Model for term {term_id} not found at path: {model_path}")
                return False
            else:
                # Load the saved spaCy model from disk
                print(f"Loading spaCy model from: {model_path}", flush=True)
                self.nlp = spacy.load(model_path)  # Load the specific model for this term
                return True
        except Exception as e:
            self.log.error(f"Error loading model for term {term_id}: {e}")
            return False

    """
    Perform prediction using a specific spaCy model loaded for the term.
    """
    def predict_text_with_model(self, text, term_id, input_creator):
        predicted_terms = []
        predicted_children = []
        predictions_log = []

        doc = self.nlp(text)  # Process the text with the loaded spaCy model
        for cat, score in doc.cats.items():
            predictions_log.append(f"{cat}: {score:.4f}")
            
            # Check if the term is already predicted 
            # If it's not for testing, we can only have one prediction for the same input creator
            exists = any(item["term"] == cat for item in self.predicted_term_ids)

            # If the term is already predicted, we can skip it
            if exists:
                continue

            # Check if the score is above the threshold
            if score > self.PREDICTION_THRESHOLD:
                prediction_obj = Prediction(cat, round(doc.cats[cat], 5), term_id, get_prediction_multiplier(input_creator), input_creator)
                predicted_terms.append(prediction_obj)
                # self.predicted_term_ids.append({ "term": cat, "parent": term_id })
            if score > self.CHILDREN_THRESHOLD:

                children_obj = Prediction(cat, round(doc.cats[cat], 5), term_id, get_prediction_multiplier(input_creator), input_creator)
                predicted_children.append(children_obj)

        self.log.info(f"Predictions: {', '.join(predictions_log)}")

        return predicted_terms, predicted_children

    '''
        Predicts the terms for a given input creator
    '''
    def predict_text_with_input_creator(self, input_creator, text, term_id):
        # Load the saved spaCy model for the term
        model_has_loaded = self.get_model_for_term(term_id, input_creator)

        if model_has_loaded is not True:
            print(f"Model for term {term_id} not found", flush=True)
            return [], []  # Skip if the model for the term is not found
        
        # Use the loaded model to predict the terms
        selected_terms, selected_children_terms = self.predict_text_with_model(text, term_id, input_creator)
        return selected_terms, selected_children_terms
    
    '''
        Combines the predictions from different input creators and generates the final prediction
    '''
    def combine_predictions(self, new_predictions, current_predictions):
        # Combine the predictions from different input creators
        for prediction in new_predictions:
            term = prediction.get_term()
            probability = prediction.get_probability()
            parent = prediction.get_parent()
            multiplierName = prediction.get_multiplier_name()
            multiplier = prediction.get_multiplier()

            if term not in current_predictions:
                current_predictions[term] = CombinedPrediction(term, probability, multiplier, multiplierName, parent)
            else:
                current_predictions[term].add_probability(probability)
                current_predictions[term].add_multiplier(multiplier)
                current_predictions[term].add_multiplier_name(multiplierName)
                current_predictions[term].add_parent(parent)

        return current_predictions

    '''
    Recursive function to predict the terms (Initially predicted terms are empty)
    '''
    def predict_text(self, predicted_terms, term_id):
        # Initialize local arrays for combining the predictions
        current_predictions = {}
        current_children = {}
        selected_children_ids = []

        self.log.info(f"--------Started predicting for term: {term_id}--------")
        print(f"--------Started predicting for term: {term_id}--------", flush=True)

        # For each term, we need to ensamble the three different input creators
        # Iterate over the input creators 
        for input_creator in self.input_creators:
            self.log.info(f"*Predicting with input creator: {input_creator}*")
            print(f"*Predicting with input creator: {input_creator}*", flush=True)
            selected_terms, selected_children_terms = self.predict_text_with_input_creator(input_creator, self.data_input[input_creator], term_id)

            # Combine the predictions from different input creators
            current_predictions = self.combine_predictions(selected_terms, current_predictions)
            current_children = self.combine_predictions(selected_children_terms, current_children)

        # Generate probability for term using ensamble, append predictions only if the term is not already predicted and the probability is above the threshold
        for term, prediction in current_predictions.items():
            prediction.generate_probability()

            if prediction.get_combined_probability() > self.PREDICTION_THRESHOLD and term not in self.predicted_term_ids:
                predicted_terms.append(prediction)
                self.predicted_term_ids.append({ "term": term, "parent": prediction.get_parents()[0] })

                # For each predicted term, check if the term has a father term already predicted. If that's the case, remove the father from predicted_terms
                self.filter_predicted_terms_by_child(predicted_terms, current_predictions)

        for term, prediction in current_children.items():
            prediction.generate_probability()

            if prediction.get_combined_probability() > self.CHILDREN_THRESHOLD:
                selected_children_ids.append(term)

        # If the prediction returns children, recursively predict for them
        if len(selected_children_ids):
            for selected_children_id in selected_children_ids:
                self.predict_text(predicted_terms, selected_children_id)

        return predicted_terms


    '''
        Iterates over the current_predictions (new predictions) and removes the father term from the predicted terms (all predictions) if it is already predicted
    '''
    def filter_predicted_terms_by_child(self, predicted_terms, current_predictions):
        for selected_term in current_predictions.values():
            term_predictions = selected_term.get_probabilities()
            term_parents = selected_term.get_parents()

            for term_prediction, term_parent in zip(term_predictions, term_parents):
                self.remove_father_from_predictions(predicted_terms, term_prediction, term_parent)
    
    '''
        Removes the father term from the predicted terms if it is already predicted
    '''
    def remove_father_from_predictions(self, predicted_terms, term_prediction, term_parent):
        father_prediction = next((prediction for prediction in predicted_terms if prediction.get_term() == term_parent), None)
        if father_prediction != None:
            self.delete_prediction(predicted_terms, father_prediction, term_prediction)

    '''
        Iterates over the predicted terms and removes the branch of the term recursively
    '''
    def delete_branch(self, predicted_terms, term_parents):
        for parent in term_parents:
            father_prediction = next((prediction for prediction in predicted_terms if prediction.get_term() == parent), None)
            if father_prediction != None:
                print(f"Removing {father_prediction.get_term()} from predicted terms as branch", flush=True)
                self.log.info(f"Removing {father_prediction.get_term()} from predicted terms as branch")
                self.delete_prediction(predicted_terms, father_prediction)
                self.delete_branch(predicted_terms, father_prediction.get_parents())

    '''
        Deletes the term from the predicted terms
    '''
    def delete_prediction(self, predicted_terms, term, probability=None):
        if probability is not None:
            print(f"Removing {term.get_term()} from predicted terms with prob {probability}", flush=True)
            self.log.info(f"Removing {term.get_term()} from predicted terms")
        predicted_terms.remove(term)


