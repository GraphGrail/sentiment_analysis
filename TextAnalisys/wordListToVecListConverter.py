
# coding: utf-8

import numpy as np
import os

from .wordToVecConverter import WordToVecConverter

class WordListToVecListConverter:
    def __init__(self):
        # self.__wordToVecConverter = WordToVecConverterProximityBased()
        self.__wordToVecConverter = None
    def convert(self, wordList):
        numberOfWords = len(wordList)
        wordVectorSize = self.__wordToVecConverter.getWordVectorSize()
        shape = None
        if wordVectorSize == 1:
            shape = (numberOfWords)
        else:
            shape = (numberOfWords, wordVectorSize)
        res = np.zeros(shape=shape, dtype=self.__wordToVecConverter.getDtype())
        i = 0
        while i < numberOfWords:
            res[i] = self.__wordToVecConverter.convert(wordList[i])
            i += 1
        return res
    def getWordToVecConverter(self):
        return self.__wordToVecConverter
    def setWordToVecConverter(self, wordToVecConverter):
        self.__wordToVecConverter = wordToVecConverter
    def save(self, destinationFolder):
        if os.path.isdir(destinationFolder + "/" + "wordToVecConverter") == False:
            os.mkdir(destinationFolder + "/" + "wordToVecConverter")
        self.__wordToVecConverter.save(destinationFolder + "/" + "wordToVecConverter")
    @staticmethod
    def load(destinationFolder):
        obj = WordListToVecListConverter()
        obj.__wordToVecConverter = WordToVecConverter.load(destinationFolder + "/" + "wordToVecConverter")
        return obj
    __wordToVecConverter = None



