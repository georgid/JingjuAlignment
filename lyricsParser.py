# -*- coding: utf-8 -*-
'''
Created on Mar 5, 2015
collection of metods for parsing textGrid and lyrics

@author: joro
'''

import sys
import os
import json



parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 

pathUtils = os.path.join(parentDir, 'utilsLyrics')
if pathUtils not in sys.path:
    sys.path.append(pathUtils)
from Utilz import writeListToTextFile


pathEvaluation = os.path.join(parentDir, 'AlignmentEvaluation')
if pathEvaluation not in sys.path:
    sys.path.append(pathEvaluation)

from WordLevelEvaluator import readNonEmptyTokensTextGrid, TextGrid2WordList

pathHMMDuration = os.path.join(parentDir, 'AlignmentDuration')
if pathHMMDuration not in sys.path:
    sys.path.append(pathHMMDuration)


from Phonetizer import Phonetizer

from SyllableJingju import SyllableJingju
from SymbTrParser import createWord

from Lyrics import Lyrics
    

    
            
def createSyllables(annotationURI, fromSyllable, toSyllable):
    '''
    @param refSyllableDuration: its value does not matter. important is that all syllables are assigned same relative duration.
    
    create Syllables, assign their durations in refSyllableDuration
    
    @return: lyrics - created lyrics oboject
    '''
    listSyllables = []
    
    annotationTokenList, annotationTokenListNoPauses =  readNonEmptyTokensTextGrid(annotationURI, 3, fromSyllable, toSyllable)
    
    
    for tsAndSyll in annotationTokenListNoPauses:
        currSyllable = SyllableJingju(tsAndSyll[2], -1)
        currSyllable.setDurationInMinUnit(1)
        listSyllables.append(currSyllable)
    
    
    
    
    return listSyllables


def divideIntoSentencesFromAnno(annotationURI):
    '''
    infer section/line timestamps from annotation-textgrid, 
    parse divison into sentences from Tier 'lines' and load its syllables corresponding by timestamps 
    '''
    
    whichLevel = 5 # read lines (sentences) tier
    annotationTokenList, annotationLinesListNoPauses =  readNonEmptyTokensTextGrid(annotationURI, whichLevel, 0, -1)
    
    whichLevel = 3 # read syllables as pinyin 
    syllablesList = TextGrid2WordList(annotationURI, whichLevel)
    annotationTokenList, syllablesList =  readNonEmptyTokensTextGrid(annotationURI, whichLevel, 0, -1)

    syllablePointer = 0
    
    listSentences = []
    for currSentence in annotationLinesListNoPauses:
        currSectionSyllables = []
        currSentenceBegin = currSentence[0] 
        currSentenceEnd = currSentence[1]
         
        while syllablesList[syllablePointer][0] < currSentenceBegin: # search for beginning
             syllablePointer += 1
        if not syllablesList[syllablePointer][0] == currSentenceBegin: # start has to be aligned 
            sys.exit("no syllable starting at sentence start at {}  ".format(currSentenceBegin) )
        
        fromSyllableIdx = syllablesList[syllablePointer][3]
        while syllablePointer < len(syllablesList) and float(syllablesList[syllablePointer][1]) <= currSentenceEnd: # syllables in currSentence
            isEndOfSentence, syllableTxt = stripPunctuationSings(syllablesList[syllablePointer][2])
            currSyllable = SyllableJingju(syllableTxt, -1)
            currSyllable.setDurationInMinUnit(1)
            currSectionSyllables.append(currSyllable)
            syllablePointer += 1
        if not syllablesList[syllablePointer-1][1] == currSentenceEnd: # end has to be aligned 
            sys.exit("no syllable ending at sentence end at {}  ".format(currSentenceEnd) )
        toSyllableIdx = syllablesList[syllablePointer-1][3]
        
        listSentences.append(( currSentenceBegin, currSentenceEnd, fromSyllableIdx, toSyllableIdx, currSectionSyllables))

     
    return listSentences


def divideIntoSentencesFromAnnoOld(annotationURI):
        '''
        infer section/line timestamps from annotation-textgrid, 
        use punctuation as marker for sentence ends
        @deprecated
        '''
#         whichLevel = 5 # line
        whichLevel = 3 # pinyin
        annotationTokenList, annotationTokenListNoPauses =  readNonEmptyTokensTextGrid(annotationURI, whichLevel, 0, -1)

        
        currSectionSyllables =  []
        listSentences = []
        
        i = 0
        currSectionStartTime = annotationTokenListNoPauses[i][0]
        fromSyllable = annotationTokenListNoPauses[i][3]
        
        for i in range(len(annotationTokenListNoPauses)):
            
            token = annotationTokenListNoPauses[i]
            isEndOfSentence, token[2] = stripPunctuationSings(token[2])
            if isEndOfSentence:
                currSyllable = SyllableJingju(token[2], -1)
                currSyllable.setDurationInMinUnit(1)
                currSectionSyllables.append(currSyllable)
                
                currSectionEndTime = token[1]
                toSyllable = token[3]
                listSentences.append(( currSectionStartTime, currSectionEndTime, fromSyllable, toSyllable, currSectionSyllables))
                
                # start next section
                currSectionSyllables =  []
                if i != len(annotationTokenListNoPauses)-1:
                    currSectionStartTime = annotationTokenListNoPauses[i+1][0]
                    fromSyllable = annotationTokenListNoPauses[i+1][3]
                
            else: # syllable not at end of sentence
                currSyllable = SyllableJingju(token[2], -1)
                currSyllable.setDurationInMinUnit(1)
                currSectionSyllables.append(currSyllable)
        return listSentences
    
    
def loadLyricsFromTextGridSentence(currSentence):
    Phonetizer.initLookupTable(True,  'phonemeMandarin2METUphonemeLookupTableSYNTH')
    syllables = currSentence[4]
    lyrics = syllables2Lyrics(syllables)

    return lyrics


def syllables2Lyrics(syllables):
        
        listWords = []
        for syllable in syllables:
            # word of only one syllable
            word, dummy = createWord([], syllable)
            listWords.append(word)
    

        Phonetizer.initLookupTable(True,  'phonemeMandarin2METUphonemeLookupTableSYNTH')

        # load phonetic dict 
        Phonetizer.initPhoneticDict('syl2phn46.txt')                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
    
        ## 3) create lyrics
        # here is called Syllable.expandToPhonemes.
        lyrics = Lyrics(listWords)
        return lyrics
    
  
def stripPunctuationSings(string_):
    isEndOfSentence = False
    if string_.endswith(u'\u3002') or string_.endswith(u'\uff0c') \
             or string_.endswith('？') or string_.endswith('！') or string_.endswith('：') \
             or string_.endswith(':') or string_.endswith(',') : # syllable at end of line/section
                string_  = string_.replace(u'\u3002', '') # comma 
                string_  = string_.replace(',','')
                string_  = string_.replace(u'\uff0c', '') # point
                string_  = string_.replace('？', '')
                string_  = string_.replace('！', '')
                string_  = string_.replace('：', '')
                string_  = string_.replace(':', '')
                isEndOfSentence = True
    return isEndOfSentence, string_

def serializeLyrics(lyrics, outputFileNoExt):
    '''
    @deprecated
    '''
    writeListToTextFile(lyrics.phonemesNetwork, None,  outputFileNoExt + '.phn')
    
    listDurations = []  
    for phoneme_ in lyrics.phonemesNetwork :
        listDurations.append(phoneme_.duration)
    writeListToTextFile(listDurations, None, outputFileNoExt + '.dur')
    
    
#     lyrics.printSyllables()
    lyrics.printPhonemeNetwork()

     
if __name__ == '__main__':
    rootURI = '/Users/joro/Documents/Phd/UPF/arias/'
    listSentences = divideIntoSentencesFromAnnoOld(rootURI + 'laosheng-erhuang_04.TextGrid')
#     for section in listSentences:
#         print section[0],  section[1], section[2], section[3]
#         for syll in section[4]:
#             print syll.text
        
        
    
#     serializeLyrics(lyrics, rootURI + 'laosheng-erhuang_04')

