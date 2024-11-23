class Prediction:
    def __init__(self, term, probability, multiplier, multiplierName, parent):
        self.term = term

        # These are arrays because we can have multiple predictions for the same term
        self.probabilities = [probability]
        self.multipliers = [multiplier]
        self.multipliersNames = [multiplierName]
        self.parents = [parent]

    def add_probability(self, probability):
        self.probabilities.append(probability)

    def add_multiplier(self, multiplier):
        self.multipliers.append(multiplier)

    def add_multiplier_name(self, multiplierName):
        self.multipliersNames.append(multiplierName)

    def add_parent(self, parent):
        self.parents.append(parent)

    def get_term(self):
        return self.term

    def get_probabilities(self):
        return self.probabilities

    def get_multipliers(self):
        return self.multipliers
    
    def get_multipliers_names(self):
        return self.multipliersNames

    def get_parents(self):
        return self.parents
