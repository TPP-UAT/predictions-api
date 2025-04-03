class Prediction:
    def __init__(self, term, probability, parent, multiplier=None, multiplierName=None):
        self.term = term

        self.probability = probability
        self.parent = parent
        self.multiplier = multiplier
        self.multiplierName = multiplierName

    def add_probability(self, probability):
        self.probability = probability

    def add_multiplier(self, multiplier):
        self.multiplier = multiplier

    def add_multiplier_name(self, multiplierName):
        self.multiplierName = multiplierName

    def add_parent(self, parent):
        self.parent = parent

    def get_term(self):
        return self.term

    def get_probability(self):
        return self.probability

    def get_multiplier(self):
        return self.multiplier
    
    def get_multiplier_name(self):
        return self.multiplierName

    def get_parent(self):
        return self.parent
