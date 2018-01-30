
# coding: utf-8

from TextAnalisys.docToVecConverter import DocToVecConverter
import numpy as np
from keras.preprocessing.sequence import pad_sequences

class SentimentPredictor:
    # return real value between -1 and 1, where -1 - negative, 1 - positive
    def predict(self, document):
        necessaryNumberOfWordsInDocument = self.__model.input_shape[1]
        docVector = self.__docToVecConverter.convert(document)
        if self.testMode == True:
            print(docVector)
        docVector = np.array([docVector])
        docVector = pad_sequences(docVector, maxlen=necessaryNumberOfWordsInDocument, truncating='post')
        if self.testMode == True:
            print(docVector)
        return self.__model.predict(docVector)[0][0]
        
        
        realNumberOfWordsInDocument = len(docVector)
        difference = necessaryNumberOfWordsInDocument - realNumberOfWordsInDocument
        if difference > 0:
            docVector = np.insert(docVector, [0] * difference, 0, axis=0)
        else:
            difference *= -1
            docVector = np.delete(docVector, [-ind - 1 for ind in range(difference)], axis=0)
        return self.__model.predict(np.array([docVector]))[0][0]
    def setModel(self, model):
        self.__model = model
    def setDocToVecConverter(self, docToVecConverter):
        self.__docToVecConverter = docToVecConverter
    
    __model = None
    __docToVecConverter = None
    
    testMode = False
