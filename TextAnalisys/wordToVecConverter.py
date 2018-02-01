
# coding: utf-8


import numpy as np
import gensim
import os
import json
import enchant
import pymorphy2

# interface for word convertion (word -> vector) class
class WordToVecConverter:
    def convert(self, word):
        pass
    def getWordVectorSize(self):
        pass
    def save(self, destinationFolder):
        pass
    @staticmethod
    def load(destinationFolder):
        realClass = None
        with open(destinationFolder + "/realClassName.txt", "r") as inputFile:
            childClassName = inputFile.readline()
            childClass = eval(childClassName)
        return childClass.load(destinationFolder)
    @staticmethod
    def _saveRealClassName(destinationFolder, realClassName):
        with open(destinationFolder + "/realClassName.txt", "w") as outputFile:
            outputFile.write(realClassName)
    @staticmethod
    def getDtype():
        pass
    
class WordToVecConverterOneHotEncoder(WordToVecConverter):
    def __init__(self):
        self.__wordToId = dict()
        self.__maxBusyIndex = 0
    def getWordVectorSize(self):
        return 1
    def fit(self, sequenceOfWordLists):
        for wordsList in sequenceOfWordLists:
            for word in wordsList:
                if word not in self.__wordToId:
                    self.__maxBusyIndex += 1
                    self.__wordToId[word] = self.__maxBusyIndex
    def convert(self, word):
        if word in self.__wordToId:
            return self.__wordToId[word]
        else:
            return 0
    def getWordToIdDictionary(self):
        return self.__wordToId
    def save(self, destinationFolder):
        WordToVecConverter._saveRealClassName(destinationFolder, "WordToVecConverterOneHotEncoder")
        with open(destinationFolder + "/state.json", "w") as outputFile:
            state = json.dumps([self.__wordToId, self.__maxBusyIndex], separators=(',',':'))
            outputFile.write(state)
            outputFile.close()
    @staticmethod
    def load(destinationFolder):
        obj = WordToVecConverterOneHotEncoder()
        with open(destinationFolder + "/state.json", "r") as inputFile:
            state = json.load(inputFile)
            obj.__wordToId = state[0]
            obj.__maxBusyIndex = state[1]
        return obj
    @staticmethod
    def getDtype():
        return np.int32
    __wordToId = None
    __maxBusyIndex = None # max index that already belong to some word


class WordToVecConverterProximityBased(WordToVecConverter):
    def convert(self, word):
        try:
            res = self.__model[word]
            return res
        except:
            return np.zeros(shape=(self.getWordVectorSize()), dtype=self.getDtype())
    def getWordVectorSize(self):
        return self.__model.vector_size
    def setModel(self, model):
        self.__model = model
    def save(self, destinationFolder):
        WordToVecConverter._saveRealClassName(destinationFolder, "WordToVecConverterProximityBased")
        self.__model.save(destinationFolder + "/model.vec")
    @staticmethod
    def load(destinationFolder):
        obj = WordToVecConverterProximityBased()
        obj.__model = gensim.models.KeyedVectors.load(destinationFolder + "/model.vec")
        return obj
    @staticmethod
    def getDtype():
        return np.float32
    __model = None
    
    
class WordToVecConverterKeyedVectorsBasedUsingSupportModels(WordToVecConverter):
    def convert(self, word):
        try:
            res = self.__model[word]
            return res
        except:
            splitOfWordOnActualWordAndSentencePart = word.split("_")
            actualWord = splitOfWordOnActualWordAndSentencePart[0]
            for model in self.__models:
                similarWords = self._findSimilarWords(actualWord, model)
                for similarWord in similarWords:
                    try:
                        res = self.__model[similarWord]
                        return res
                    except:
                        pass
            if len(similarWords) == 0:
                
            alternatives = self._getAlternativeSpellingVariants(actualWord)
            
            for alternativeWord in alternatives:
                
    def setModel(self, models):
        self.__models = models
    def setSupportingModels(self, models):
        self.__supportingModels = models
    def _getAlternativeSpellingVariants(self, word):
        d = enchant.Dict("ru_RU")
        return d.suggest(word)
    def _findSimilarWords(self, word, model):
        res = []
        mainSentenceParts = ['NOUN', 'ADJF', 'ADJS', 'COMP', 'VERB', 'INFN', 'PRTF', 'PRTS', 'GRND', 'ADVB']
        for sentencePart in mainSentenceParts:
            try:
                similarWords = [w[0] for w in model.similar_by_word(word + sentencePart, topn=3)]
                res = res + similarWords
            except:
                pass
        return res
    def searchAnyVectorForWords(self, words):
        for model in self.__models:
                similarWords = self._findSimilarWords(actualWord, model)
                for similarWord in similarWords:
                    try:
                        res = self.__model[similarWord]
                        return res
                    except:
                        pass
    __model = None
    __supportingModels = None

