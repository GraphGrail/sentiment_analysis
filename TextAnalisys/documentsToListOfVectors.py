
# coding: utf-8

import numpy as np
from tensorflow.contrib import learn
import gensim
import os
from .textPreprocessor import TextPreprocessor
from .wordToVecConverter import WordToVecConverterOneHotEncoder
from .wordToVecConverter import WordToVecConverterProximityBased
from ast import literal_eval


class DocumentsToListOfVectors:
    def __init__(self):
        self.__textPreprocessor = TextPreprocessor(addPartOfSpeechTagToWords = True)
        #self.__wordToVecConverter = WordToVecConverterProximityBased()
        self.__wordToVecConverter = WordToVecConverterOneHotEncoder()
    def convertDocuments(self, documentsList):
        documentsRepresentationAsWordLists = self.__textPreprocessor.convertListOfDocumentsTo2dListOfWords(documentsList)
        return self.convertWordLists(self, documentsRepresentationAsWordLists)
    # convert already splited by words documents to list of 3d vectors
    def convertWordLists(self, wordLists):
        i = 0
        listOfWordVectors = []
        for wordList in wordLists:
            if i % 200 == 0:
                print("Vectorization of " + str(i) + " document")
            wordVectors = []
            for word in wordList:
                wordVectors.append(self.__wordToVecConverter.convert(word))
            listOfWordVectors.append(wordVectors)
            i += 1
        return listOfWordVectors
    # instead of function convertWordLists(self, wordLists) result of convertion is numpy array of const size
    def convertWordListsWithFixedLength(self, wordLists, wordAmountPerDocument):
        documnetsNumber = len(wordLists)
        listOfWordVectors = np.zeros(shape=(documnetsNumber, wordAmountPerDocument, self.__wordToVecConverter.getWordVectorSize()), dtype=np.float32)
        i = 0
        while i < documnetsNumber:
            numberOfWordsInDocument = len(wordLists[i])
            startPosition = wordAmountPerDocument - numberOfWordsInDocument
            if startPosition < 0:
                startPosition = 0
            g = 0
            while g < wordAmountPerDocument - startPosition:
                listOfWordVectors[i][g + startPosition] = self.__wordToVecConverter.convert(wordLists[i][g])
                g += 1
            i += 1
        return listOfWordVectors
    def convertDocumentToListOfWordVectors(self, document):
        wordVectors = []
        wordList = self.__textPreprocessor.convertTextToListOfWords(document)
        for word in wordList:
            wordVectors.append(self.__wordToVecConverter.convert(word))
        return wordVectors
    def convertDocumentToWordVectorsListOfFixedLength(self, document, wordAmountPerDocument):
        wordVectors = np.zeros(shape=(wordAmountPerDocument, self.__wordToVecConverter.getWordVectorSize()), dtype=np.float32)
        wordList = self.__textPreprocessor.convertTextToListOfWords(document)
        numberOfWordsInDocument = len(wordList)
        startPosition = wordAmountPerDocument - numberOfWordsInDocument
        if startPosition < 0:
            startPosition = 0
        g = 0
        while g < wordAmountPerDocument - startPosition:
            wordVectors[g + startPosition] = self.__wordToVecConverter.convert(wordList[g])
            g += 1
        return wordVectors
    __textPreprocessor = None
    __wordToVecConverter = None

