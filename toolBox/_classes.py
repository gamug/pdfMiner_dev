# Class defined to couple words and search criterion
import re, spacy
import numpy as np

class resultSearched():
    def __init__(self, words, symbol, function='default'):
        self.words = words
        self.symbol = symbol
        if type(function) == str:
            self.function = self.default
        else:
            self.function = function

    def default(self,array):
        '''''
        Function default to search word coincidences
            input:
                array: list type with paragraph words
            output:
                boolean: True if the searched word is in paragraph
                         False if isn't
        '''''
        paragraph = ' '.join(array)
        for word in self.words:
            aux = re.findall(word + r'.*', paragraph, re.IGNORECASE)
            if len(aux) > 0:
                return True
        return False

# This is a class that let us extract engineering and petroleum companies from spacy entities
class entGetter():
    def __init__(self, petroleum, engineer, nlp):
        '''''
        Class generate to proccess company and gpe extraction
        input:
            petroleum: petroleum companies dictionary with structure {'companies':[...],'countries':[...]}
            engineer: enginer companies dictionary with structure {'companies':[...],'countries':[...]}
        Output:
            provide a instantiated object to manage companies and places extraction from text.
        '''''
        self.nlp = nlp
        #         first we create and normalize filters
        self.companies = self.normalizeFilters(petroleum['companies']) \
                         + self.normalizeFilters(engineer['companies'])

    def normalizeFilters(self, data):
        '''''
        function designed to transform word list to an string without spaces
        input:
            data (list): list of strings
            compCollections (string): collections of companies without spaces.
        '''''
        compCollections = []
        for company in data:
            for word in company.split(' '):
                compCollections.append(word)
        compCollections = ''.join(compCollections)
        return compCollections

    def getEntities(self, text):
        '''''
        This function iterate along the text input and return gpe count and entities gotten
        input:
            text: Sentence to analize
        output:
            textCompanies: NumpyArray with all companies found
            gpe: Count of number of places found

        '''''
        self.doc = self.nlp(text)
        self.textCompanies = []
        self.gpe = []
        for ent in self.doc.ents:
            if ent.label_ == 'ORG':
                try:
                    if len(re.findall(ent.text.replace(' ', ''), self.companies)) > 0:
                        self.textCompanies.append(ent.text)
                except:
                    pass
            if ent.label_ == 'GPE':
                self.gpe.append(ent.text)
        self.textCompanies = np.unique(self.textCompanies)
        numgpe = len(self.gpe)
        self.gpe = np.unique(self.gpe)
        return self.textCompanies, self.gpe, numgpe