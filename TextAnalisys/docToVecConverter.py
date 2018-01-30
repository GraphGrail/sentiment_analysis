
# coding: utf-8

import os

from .wordListToVecListConverter import WordListToVecListConverter
from .textPreprocessor import TextPreprocessor

class DocToVecConverter:
    def __init__(self):
        self.__wordListToVecListConverter = WordListToVecListConverter()
        self.__textPreprocessor = TextPreprocessor(addPartOfSpeechTagToWords = True)
    def convert(self, doc):
        wordList = self.__textPreprocessor.convertTextToListOfWords(doc)
        return self.__wordListToVecListConverter.convert(wordList)
    def getWordListToVecListConverter(self):
        return self.__wordListToVecListConverter
    def setWordListToVecListConverter(self, wordListToVecListConverter):
        self.__wordListToVecListConverter = wordListToVecListConverter
    def getTextPreprocessor(self):
        return self.__textPreprocessor
    def setTextPreprocessor(self, textPreprocessor):
        self.__textPreprocessor = textPreprocessor
    def save(self, destinationFolder):
        if os.path.isdir(destinationFolder + "/" + "wordListToVecListConverter") == False:
            os.mkdir(destinationFolder + "/" + "wordListToVecListConverter")
        self.__wordListToVecListConverter.save(destinationFolder + "/" + "wordListToVecListConverter")
        if os.path.isdir(destinationFolder + "/" + "textPreprocessor") == False:
            os.mkdir(destinationFolder + "/" + "textPreprocessor")
        self.__textPreprocessor.save(destinationFolder + "/" + "textPreprocessor")
    @staticmethod
    def load(destinationFolder):
        obj = DocToVecConverter()
        obj.__wordListToVecListConverter = WordListToVecListConverter.load(destinationFolder + "/" + "wordListToVecListConverter")
        obj.__textPreprocessor = TextPreprocessor.load(destinationFolder + "/" + "textPreprocessor")
        return obj
    __wordListToVecListConverter = None
    __textPreprocessor = None

