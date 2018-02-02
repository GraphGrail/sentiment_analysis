
# coding: utf-8

# In[ ]:

from nltk.corpus import stopwords
import numpy as np
import pymorphy2
import re
import pandas as pd
import json
import enchant
import copy
#import polyglot

def pymorphy_POS_tags_to_universal_tags(tagList):
    res = [""] * len(tagList)
        i = 0
        while i < len(tagList):
            if tagList[i] in ["ADJF", "ADJS"]:
                res[i] = "ADJ"
                i += 1
                continue
            if tagList[i] in ["COMP", "ADVB"]:
                res[i] = "ADV"
                i += 1
                continue
            if tagList[i] in ["INFN", 'PRTF', 'PRTS', 'GRND']:
                res[i] = "VERB"
                i += 1
                continue
            if tagList[i] in ["NPRO"]:
                res[i] = "NOUN"
                i += 1
                continue
            res[i] = tagList[i]
            i += 1
        return res


class TextPreprocessorFixMisspellingsMultipleModels:
    def __init__(self, add_POS_tag_to_words = False):
        self.__significant_POS = ['NOUN', 'ADJF', 'ADJS', 'COMP', 'VERB', 'INFN', 'PRTF', 'PRTS', 'GRND', 'ADVB']
        self.__model_POS_tags = ["ADJ", "ADV", "INTJ", "NOUN", "PROPN", "VERB"]
        
        self.__stoplist = set.union(self.__stoplist, set(stopwords.words('english')))
        self.__stoplist = set.union(self.__stoplist, set(stopwords.words('russian')))
        
        self.__add_POS_tag_to_words = add_POS_tag_to_words
        
        self.__morph = pymorphy2.MorphAnalyzer()
        
        self.__pymorphy_POS_tags_converter = pymorphy_POS_tags_to_universal_tags
        
        self.__dictRu = enchant.Dict("ru_RU")
    # convert text to list of words, removing named entities, not significant sentence parts and stopwords
    def convertTextToListOfWords(self, text):
        if pd.isnull(text):
            return []
        wordList = self.splitStringInList(text)
        if self.testMode == True:
            print("After splitting:")
            print(wordList)
        namedEntitiesSet = self.getSetOfEntitiesInList(wordList)
        self.removeSpecificWordsFromList(wordList, namedEntitiesSet)
        self.removeNotInformativeWordsFromList(wordList)
        i = 0
        res = []
        while i < len(wordList):
            res = res + tryToHandleWord(wordList[i])
        if self.testMode == True:
            print("After all changes:")
            print(res)
        return res
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
    def tryToHandleWord(self, word):
        correct = self.__dictRu.check(word)
        wordAndItsAlternatives = [word]
        if correct == False:
            wordAndItsAlternatives = wordAndItsAlternatives + self.__dictRu.suggest(word)
        i = 0
        res = []
        while i < len(wordAndItsAlternatives):
            splittedWords = wordAndItsAlternatives[i].split(" ")
            for splittedWord in splittedWords:
                searchResult = self.searchForWordInModels(splittedWord)
                if searchResult != None:
                    res.append(searchResult)
            if res != []:
                return res
            i += 1
        return res
    def searchForWordInModels(self, word):
        probablePOS = self.__pymorphy_POS_tags_converter(str(self.__morph.parse(word.lower())[0].tag.POS))
        copiedTags = copy.deepcopy(self.__model_POS_tags)
        word = self.__morph.parse(word.lower())[0].normal_form
        i = 0
        while i < len(copiedTags):
            if probablePOS == copiedTags[i]:
                del copiedTags[i]
                copiedTags.insert(0, probablePOS)
                break
            i += 1
        res = self._searchForWordInBaseModel(word, copiedTags)
        if res != None:
            return res
        res = self._searchForSimilarWordInSupportingModels(word, copiedTags)
        return res
    def _searchForWordInBaseModel(self, , word, copiedTags):
        for POS in copiedTags:
            try:
                wordWithPOS = word + "_" + POS
                res = self.__baseModel[wordWithPOS]
                return wordWithPOS
            except:
                pass
        return None
    def _searchForSimilarWordInSupportingModels(self, word, copiedTags):
        for POS in copiedTags:
            for supportModel in self.__supportingModels:
                wordWithPOS = word + "_" + POS
                try:
                    res = self.supportModel[wordWithPOS]
                    similarWords = supportModel.similar_by_word(wordWithPOS, topn=3)
                    for similarWord in similarWords:
                        try:
                            res = self.__baseModel[similarWord[0]]
                            return similarWord[0]
                        except:
                            pass
                except:
                    pass
        return None
    # get list of words from text using regular expressions
    def splitStringInList(self, text):
        #prog = re.compile(r'[А-Яа-яA-Za-z-]{1,}')
        prog = re.compile(r'[А-Яа-я]{1,}-{0,1}[А-Яа-я]{1,}|[A-Za-z]{1,}-{0,1}[A-Za-z]{1,}')
        wordsIterator = prog.finditer(text)
        resultList = []
        for word in wordsIterator:
            resultList.append(word.group(0))
        return resultList
    # return set of words which are named entities in list l
    def getSetOfEntitiesInList(self, l): # TODO
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
    def removeSpecificWordsFromList(self, l, words_set):
        for word in words_set:
            word = word.lower()
            i = len(l) - 1
            while i >= 0:
                if l[i].lower() == word:
                    del l[i]
                i -= 1
    def removeNotInformativeWordsFromList(self, l):
        i = len(l) - 1
        while i >= 0:
            if self.__dictRu.check(l[i]) and self.__morph.parse(l[i])[0].tag.POS not in self.__significant_POS:
                del l[i]
            i -= 1
    def getSignificantSentenceParts(self):
        return self.__significant_POS
    def setSignificantSentenceParts(self, significant_POS):
        self.__significant_POS = significant_POS
    def getStopList(self):
        return self.__stoplist
    def setStopList(self, stopList):
        self.__stoplist = stoplist
    def save(self, destinationFolder):
        with open(destinationFolder + "/state.json", "w") as outputFile:
            state = json.dumps([self.__significant_POS, 
                                list(self.__stoplist), 
                                self.__add_POS_tag_to_words], 
                               separators=(',',':'))
            outputFile.write(state)
            outputFile.close()
    @staticmethod
    def load(destinationFolder):
        obj = TextPreprocessor()
        with open(destinationFolder + "/state.json", "r") as inputFile:
            state = json.load(inputFile)
            obj.__significant_POS = state[0]
            obj.__stoplist = set(state[1])
            obj.__add_POS_tag_to_words = state[2]
            obj.__morph = pymorphy2.MorphAnalyzer()
            obj.__pymorphy_POS_tags_converter = pymorphy_POS_tags_to_universal_tags
        return obj
    __significant_POS = None
    __stoplist = None
    __add_POS_tag_to_words = None
    __morph = None
    
    __pymorphy_POS_tags_converter = None
    __model_POS_tags = None
    
    __baseModel = None
    __supportingModels = None
    
    __dictRu = None
    
    testMode = False


