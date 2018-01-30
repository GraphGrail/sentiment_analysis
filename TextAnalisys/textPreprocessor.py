
# coding: utf-8

from nltk.corpus import stopwords
#from polyglot.text import Text
import numpy as np
import pymorphy2
import re
import pandas as pd
import json

class TextPreprocessor:
    def __init__(self, addPartOfSpeechTagToWords = False):
        self.significantSentenceParts_ = ['NOUN', 'ADJF', 'ADJS', 'COMP', 'VERB', 'INFN', 'PRTF', 'PRTS', 'GRND', 'ADVB']
        
        self.stoplist_ = set(['помочь', 'мочь'])
        self.stoplist_ = set.union(self.stoplist_, set(stopwords.words('english')))
        self.stoplist_ = set.union(self.stoplist_, set(stopwords.words('russian')))
        
        self.addPartOfSpeechTagToWords_ = addPartOfSpeechTagToWords
        
        self.morph_ = pymorphy2.MorphAnalyzer()
    # convert text to list of words, removing named entities, not significant sentence parts and stopwords
    def convertTextToListOfWords(self, text):
        if pd.isnull(text):
            return []
        wordList = self.splitStringInList(text)
        namedEntitiesSet = self.getSetOfEntitiesInList(wordList)
        self.removeSpecificWordsFromList(wordList, namedEntitiesSet)
        self.removeNotInformativeWordsFromList(wordList)
        self.normalizeWordsInList(wordList)
        if self.addPartOfSpeechTagToWords_ == True:
            self.addPartOfSpeechTagToWordsInList(wordList)
        return wordList
    def convertListOfDocumentsTo2dListOfWords(self, documentList):
        i = 0
        res = []
        for doc in documentList:
            if i % 200 == 0:
                print("Converting " + str(i) + " document")
            res.append(self.convertTextToListOfWords(doc))
            i += 1
        return res
    def convertListOfDocumentsToListOfStrings(self, documentList):
        res = []
        for doc in documentList:
            res.append(" ".join(self.convertTextToListOfWords(doc)))
        return res
    def normalizeWordsInList(self, l):
        i = 0
        listSize = len(l)
        while i < listSize:
            l[i] = self.morph_.parse(l[i].lower())[0].normal_form
            i += 1
    def addPartOfSpeechTagToWordsInList(self, l):
        i = 0
        listSize = len(l)
        while i < listSize:
            speechPart = self.morph_.parse(l[i])[0].tag.POS
            if speechPart is None:
                i += 1
                continue
            l[i] = l[i] + "_" + self.morph_.parse(l[i])[0].tag.POS
            i += 1
    # get list of words from text using regular expressions
    def splitStringInList(self, text):
        prog = re.compile(r'[А-Яа-яA-Za-z-]{1,}')
        wordsIterator = prog.finditer(text)
        resultList = []
        for word in wordsIterator:
            resultList.append(word.group(0))
        return resultList
    # return set of words which are named entities in list l
    def getSetOfEntitiesInList(self, l):
        stringFromList = " ".join(l)
        res = set()
        '''errorNumber = 0
        try:
            polyglotText = Text(stringFromList)
            for entitie in polyglotText.entities:
                for entitiePart in entitie:
                    res.add(entitiePart.lower())
        except:
            errorNumber += 1'''
        return res
    # removes wordsSet from list of words l
    def removeSpecificWordsFromList(self, l, wordsSet):
        for word in wordsSet:
            word = word.lower()
            i = len(l) - 1
            while i >= 0:
                if l[i].lower() == word:
                    del l[i]
                i -= 1
    def removeNotInformativeWordsFromList(self, l):
        i = len(l) - 1
        while i >= 0:
            if self.morph_.parse(l[i])[0].tag.POS not in self.significantSentenceParts_:
                del l[i]
            i -= 1
    def getSignificantSentenceParts(self):
        return self.significantSentenceParts_
    def setSignificantSentenceParts(self, significantSentenceParts):
        self.significantSentenceParts_ = significantSentenceParts
    def getStopList(self):
        return self.stoplist_
    def setStopList(self, stopList):
        self.stoplist_ = stoplist
    def save(self, destinationFolder):
        with open(destinationFolder + "/state.json", "w") as outputFile:
            state = json.dumps([self.significantSentenceParts_, 
                                list(self.stoplist_), 
                                self.addPartOfSpeechTagToWords_], 
                               separators=(',',':'))
            outputFile.write(state)
            outputFile.close()
    @staticmethod
    def load(destinationFolder):
        obj = TextPreprocessor()
        with open(destinationFolder + "/state.json", "r") as inputFile:
            state = json.load(inputFile)
            obj.significantSentenceParts_ = state[0]
            obj.stoplist_ = set(state[1])
            obj.addPartOfSpeechTagToWords_ = state[2]
            obj.morph_ = pymorphy2.MorphAnalyzer()
        return obj
    significantSentenceParts_ = None
    stoplist_ = None
    addPartOfSpeechTagToWords_ = None
    morph_ = None

