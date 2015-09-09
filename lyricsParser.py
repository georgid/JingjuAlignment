# -*- coding: utf-8 -*-
'''
Created on Mar 5, 2015

@author: joro
'''

import sys
import os
import json



parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 

pathUtils = os.path.join(parentDir, 'utilsLyrics')
if pathUtils not in sys.path:
    sys.path.append(pathUtils)
from Utilz import writeListToTextFile


pathEvaluation = os.path.join(parentDir, 'AlignmentEvaluation')
if pathEvaluation not in sys.path:
    sys.path.append(pathEvaluation)

pathAlignmentDuration = os.path.join(parentDir, 'AlignmentDuration')
if pathAlignmentDuration not in sys.path:
    sys.path.append(pathAlignmentDuration)


from Phonetizer import Phonetizer

from SyllableJingju import SyllableJingju
from SymbTrParser import createWord

from Lyrics import Lyrics
    
from WordLevelEvaluator import readNonEmptyTokensTextGrid

    
            
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


def divideIntoSectionsFromAnno(annotationURI):
        '''
        infer section/line timestamps from annotation-textgrid
        '''        
        annotationTokenList, annotationTokenListNoPauses =  readNonEmptyTokensTextGrid(annotationURI, 3, 0,-1)

        
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
                listSentences.append(( currSectionStartTime,currSectionEndTime, fromSyllable, toSyllable, currSectionSyllables))
                
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
    listSentences = divideIntoSectionsFromAnno(rootURI + 'laosheng-erhuang_04.TextGrid')
#     for section in listSentences:
#         print section[0],  section[1], section[2], section[3]
#         for syll in section[4]:
#             print syll.text
        
        
    
#     serializeLyrics(lyrics, rootURI + 'laosheng-erhuang_04')

