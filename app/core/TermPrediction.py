import glob
import logging
import spacy
from app.utils.input_creators import get_prediction_multiplier
from app.models.Prediction import Prediction

logging.basicConfig(filename='logs/predictor.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CHILDREN_THRESHOLD = 0.4
PREDICTION_THRESHOLD = 0.8

class TermPrediction:
    def __init__(self, input_creator, thesaurus):
        self.input_creator = input_creator
        self.thesaurus = thesaurus
        self.nlp = None
        self.log = logging.getLogger('predictor_logger')
        # Array to store the predicted term ids and parents
        self.predicted_term_ids = []

    """
    Retrieve and load the saved spaCy model for a specific term.
    The model should have been previously saved to disk.
    """
    def get_model_for_term(self, term_id):
        model_path = f"./models/{self.input_creator}/{term_id}"
        
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
    def predict_text_with_model(self, text, term_id):
        predicted_terms = []
        predicted_children_ids = []
        predictions_log = []

        doc = self.nlp(text)  # Process the text with the loaded spaCy model
        for cat, score in doc.cats.items():
            predictions_log.append(f"{cat}: {score:.4f}")
            # TODO: Remove this condition. We have to check only if the term is already predicted (the parents dont matter)
            # Change this condition to check if the "cat" is already predicted in predicted_term_ids
            exists = any(item["term"] == cat and item["parent"] == term_id for item in self.predicted_term_ids)
            if score > PREDICTION_THRESHOLD and not exists:
                prediction_obj = Prediction(cat, round(doc.cats[cat], 5), get_prediction_multiplier(self.input_creator), self.input_creator, term_id)
                predicted_terms.append(prediction_obj)
                self.predicted_term_ids.append({ "term": cat, "parent": term_id })
            if score > CHILDREN_THRESHOLD:
                predicted_children_ids.append(cat)

        self.log.info(f"Predictions: {', '.join(predictions_log)}")

        return predicted_terms, predicted_children_ids

        # Score supera PREDICTION -> guardar como un predicted term
        #            prediction_obj = Prediction(term, doc.cats[term], get_prediction_multiplier(self.input_creator))
        #             predicted_terms.append(prediction_obj)
        # Score supera CHILDREN PREDICTION -> guardar como un id y apendearlo a un predicted_children_terms (son ids)

    '''
    Recursive function to predict the terms (Initially predicted terms are empty)
    '''
    def predict_text(self, text, term_id, predicted_terms, remove_fathers=False, delete_by_probability=False):
        self.log.info(f"Started predicting for term: {term_id}")
        print(f"Started predicting for term: {term_id}", flush=True)

        # Load the saved spaCy model for the term
        model_has_loaded = self.get_model_for_term(term_id)
        if model_has_loaded is not True:
            print(f"Model for term {term_id} not found", flush=True)
            return predicted_terms  # Skip if the model for the term is not found

        # Use the loaded model to predict the terms
        selected_terms, selected_children_ids = self.predict_text_with_model(text, term_id)

        if selected_terms:
            predicted_terms.extend(selected_terms)

            # For each predicted term, check if the term has a father term already predicted. If that's the case, remove the father from predicted_terms
            if remove_fathers:
                self.filter_predicted_terms_by_child(predicted_terms, delete_by_probability, selected_terms)

        # If the prediction returns children, recursively predict for them
        if len(selected_children_ids):
            for selected_children_id in selected_children_ids:
                self.predict_text(text, selected_children_id, predicted_terms, remove_fathers, delete_by_probability)

        return predicted_terms

    '''
        Iterates over the selected terms (new predictions) and removes the father term from the predicted terms (all predictions) if it is already predicted
    '''
    def filter_predicted_terms_by_child(self, predicted_terms, delete_by_probability, selected_terms):
        for selected_term in selected_terms:
            term_predictions = selected_term.get_probabilities()
            term_parents = selected_term.get_parents()
            term_multipliers = selected_term.get_multipliers_names()

            for term_prediction, term_parent, term_input_creator in zip(term_predictions, term_parents, term_multipliers):
                self.remove_father_from_predictions(predicted_terms, term_prediction, term_parent, term_input_creator, delete_by_probability)
    
    '''
        Removes the father term from the predicted terms if it is already predicted
    '''
    def remove_father_from_predictions(self, predicted_terms, term_prediction, term_parent, term_input_creator, delete_by_probability):
        father_prediction = next((prediction for prediction in predicted_terms if prediction.get_term() == term_parent), None)
        if father_prediction != None and term_input_creator == self.input_creator:
            if delete_by_probability:
                        
                # Get first index of current input creator from father prediction
                father_index = father_prediction.get_multipliers_names().index(self.input_creator)
                father_probability = father_prediction.get_probabilities()[father_index]

                # If the father probability is less than the term prediction + 0.05, remove the father from the predicted terms
                if (father_probability < (term_prediction + 0.05)):
                    self.delete_prediction(predicted_terms, father_prediction, father_probability)
                    self.delete_branch(predicted_terms, father_prediction.get_parents())
            else:
                self.delete_prediction(predicted_terms, father_prediction)

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


