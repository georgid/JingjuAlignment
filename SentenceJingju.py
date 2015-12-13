'''
Created on Dec 9, 2015

@author: joro
'''
from PhonetizerDict import createDictSyll2XSAMPA

from Phonetizer import Phonetizer
from Lyrics import Lyrics
from SymbTrParser import createWord
import numpy


class SentenceJingju(Lyrics):
    '''
    classdocs
    '''


    def __init__(self, listSyllables,  beginTs, endTs, fromSyllableIdx, toSyllableIdx, banshiType):
        '''
        '''
        
                
        listWords = []
        for syllable in listSyllables:
            # word of only one syllable
            word, dummy = createWord([], syllable)
            listWords.append(word)
            
        Phonetizer.initLookupTable(True,  'XSAMPA2METUphonemeLookupTableSYNTH')

        # load phonetic dict 
#         Phonetizer.initPhoneticDict('syl2phn46.txt')
        Phonetizer.phoneticDict = createDictSyll2XSAMPA() 

        Lyrics.__init__(self, listWords)
        
        
        
        self.banshiType = banshiType
        self.beginTs = beginTs
        self.endTs = endTs
        self.fromSyllableIdx = fromSyllableIdx
        self.toSyllableIdx = toSyllableIdx
    
    def assignReferenceDurations(self):
    
        ####### set durations according rules
    
        lenSyllables = len(self.listWords) # each word has one syllable
        
        durations = self._computeReferenceDurations(lenSyllables)
        
        for idx, word in enumerate(self.listWords):
                word.syllables[0].setDurationInMinUnit(durations[idx])
                
                
                
    def _computeReferenceDurations(self, lenSyllables):
        '''
        use musicological rules depending on number of syllables
        '''
    
        durations = [0 for x in range(lenSyllables)]
        durations[-1] = 1 / 3.0
        
        if lenSyllables >=6:
            if lenSyllables <= 8:
                firstPhraseEndIndex = 1
                secondPhraseEndIndex = 3
            elif lenSyllables >= 9:
                firstPhraseEndIndex = 2
                secondPhraseEndIndex = 5
            durations[firstPhraseEndIndex] = 1 / 4.0
            durations[secondPhraseEndIndex] = 1 / 5.0
        
        
        arr = numpy.array(durations)
        lenSyllablesDiffThan0 = len(numpy.where(arr != 0)[0])
        
    # the rest of sylable durations are equal
        totalAssignedDurations = sum(durations)
        durRest = 0
        if lenSyllables - lenSyllablesDiffThan0:
            durRest = (1 - totalAssignedDurations) / float(lenSyllables - lenSyllablesDiffThan0)
        for i in range(len(durations)):
            if durations[i] == 0: durations[i] = durRest
        
        return durations
       