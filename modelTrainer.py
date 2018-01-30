
# coding: utf-8

import contextlib

class ModelTrainer:
    def __init__(self, numberOfStepsBeforeTesting, filenameToStoreBestModel = None):
        self.__totalNumberOfStepsMade = 0
        self.__numberOfStepsBeforeTesting = numberOfStepsBeforeTesting
        self.__filenameToStoreBestModel = filenameToStoreBestModel
    def setGenerators(self, trainGen, testGen):
        self.__trainGenerator = trainGen
        self.__testGenerator = testGen
    def setTrainFiniteGeneratorForTestModel(self, trainFiniteGeneratorForTestModel):
        self.__trainFiniteGeneratorForTestModel = trainFiniteGeneratorForTestModel
    def getModel(self):
        return self.__model
    def setModel(self, model):
        self.__model = model
    def storeModel(self):
        if self.__filenameToStoreBestModel != None:
            self.__model.save(self.__filenameToStoreBestModel)
    def train(self, showModelOutputDuringTrainingSteps=False):
        self.__continueTraining = True
        self.__totalNumberOfStepsMade = 0
        minimumLoss = None
        print("Number of steps before testing step: " +  str(self.__numberOfStepsBeforeTesting))
        while self.__continueTraining == True:
            i = 0
            if showModelOutputDuringTrainingSteps == False:
                with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
                    while i < self.__numberOfStepsBeforeTesting:
                        if self.__continueTraining == False:
                            break
                        self.__model.fit_generator(self.__trainGenerator, steps_per_epoch=1, epochs=1, use_multiprocessing=True)
                        i += 1
            else:
                while i < self.__numberOfStepsBeforeTesting:
                    if self.__continueTraining == False:
                        break
                    self.__model.fit_generator(self.__trainGenerator, steps_per_epoch=1, epochs=1, use_multiprocessing=True)
                    i += 1
            self.__totalNumberOfStepsMade += self.__numberOfStepsBeforeTesting
            print("Number of steps made: " + str(self.__totalNumberOfStepsMade))
            if self.__trainFiniteGeneratorForTestModel != None: # test model. Can it predict correctly at least on train data
                loss = self.__model.evaluate_generator(self.__trainFiniteGeneratorForTestModel, use_multiprocessing=True)
                print("Current loss on train data: " + str(loss))
            loss = self.__model.evaluate_generator(self.__testGenerator, use_multiprocessing=True)
            print("Current loss: " + str(loss))
            if minimumLoss == None or loss < minimumLoss:
                self.storeModel()
                minimumLoss = loss
    def stopTraining(self):
        self.__continueTraining = False
    __model = None
    __trainGenerator = None
    __testGenerator = None # child of keras.utils.Sequence
    __totalNumberOfStepsMade = None
    
    __numberOfStepsBeforeTesting = None
    
    __continueTraining = None
    __filenameToStoreBestModel = None
    
    __trainFiniteGeneratorForTestModel = None
