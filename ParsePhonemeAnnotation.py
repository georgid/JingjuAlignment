'''
Created on Oct 6, 2015

@author: joro
'''

from lyricsParser import _findBeginEndIndices, stripPunctuationSigns,\
    divideIntoSentencesFromAnnoWithSil, \
    mergeDuplicateSyllablePhonemes
from lyricsParser import logger
import os
import sys
from collections import deque
from PhonetizerDict import loadXSAMPAPhonetizers, toXSAMPAPhonemes,\
    createDictSyll2XSAMPA, tokenizePhonemes
import logging

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 

pathEvaluation = os.path.join(parentDir, 'AlignmentEvaluation')
if pathEvaluation not in sys.path:
    sys.path.append(pathEvaluation)

from WordLevelEvaluator import readNonEmptyTokensTextGrid, TextGrid2WordList, tierAliases


parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 

pathHMMDuration = os.path.join(parentDir, 'AlignmentDuration')
if pathHMMDuration not in sys.path:
    sys.path.append(pathHMMDuration)


import Phonetizer
from Phoneme import Phoneme


def validatePhonemesWholeAria(lyricsTextGrid):
    '''
    validates if annotated phonemes are corresponmding to automatically expanded from dict
    '''
    listSentences = divideIntoSentencesFromAnnoWithSil(lyricsTextGrid) #uses TextGrid annotation to derive structure. 
    dictSyll2XSAMPA = createDictSyll2XSAMPA()
    
    for whichSentence, currSentence in  enumerate(listSentences):
#         if whichSentence <3: continue
        
        
        for i, syllableIdx in enumerate(range(currSentence.fromSyllableIdx, currSentence.toSyllableIdx)):
             
            validatePhonemesOneSyll(lyricsTextGrid, syllableIdx, dictSyll2XSAMPA, currSentence.listWords[i].syllables[0])






def parsePhonemes(lyricsTextGrid, syllableIdx):
    '''
    parse phonemes for given syllable
    '''
    highLevel = tierAliases.pinyin # read syllable in pinyin
    syllable, dummy = readNonEmptyTokensTextGrid(lyricsTextGrid, highLevel, syllableIdx, syllableIdx)

    
    lowLevel = tierAliases.xsampadetails # read phonemesAnno
    phonemesAnnoList, phonemesAnnoListNoPauses = readNonEmptyTokensTextGrid(lyricsTextGrid, lowLevel, 0, -1)
    
    beginSyllableTs = syllable[0][0]
    endSyllableTs = syllable[0][1]
    syllablePinYinRaw = syllable[0][2].strip()
    isEndOfSentence, syllableText = stripPunctuationSigns(syllablePinYinRaw)
    
#     if syllableText == '': # skip this syllable with no lyrics 
#         return phonemesAnnoList, -1, -1, syllableText 
    
    phonemesPointer = 0
    
    fromPhonemeIdx, toPhonemeIdx, dummy, dummy = _findBeginEndIndices(phonemesAnnoList, phonemesPointer, beginSyllableTs, endSyllableTs, highLevel)
    
    return phonemesAnnoList, fromPhonemeIdx, toPhonemeIdx, syllableText, phonemesAnnoListNoPauses



def removeDuplicatePhonemes(phonemesListNoPauses, fromPhonemeIdx, toPhonemeIdx):
    '''
    
    input in tier details : x x x o o u -> 
    output: x o u (with corresponding timestamps at begining and end) 
    '''
    ################### find index where a new phoneme appears
    indicesStateStarts = [] # indices of change of phoneme text
    
    currPhoneme = ''
    for i, phoneme in enumerate(phonemesListNoPauses[fromPhonemeIdx:toPhonemeIdx + 1]):
        if phoneme[2] == '?':   continue # ? are not new phonemes
        
        if not phoneme[2] == currPhoneme: # new phoneme
            indicesStateStarts.append(i + fromPhonemeIdx)
            currPhoneme = phoneme[2]
    
    ################## get only unique phonemes from indices
    phonemesAnno = [] #  output: list of phonemesAnno read
    for i in range(len(indicesStateStarts) - 1):
        idx = indicesStateStarts[i]
        idxLast = indicesStateStarts[i + 1] - 1
        
        currPhn = Phoneme(phonemesListNoPauses[idx][2])  
        
        currPhn.setBeginTs(phonemesListNoPauses[idx][0])
        currPhn.setEndTs(phonemesListNoPauses[idxLast][1])
       
        phonemesAnno.append(currPhn)
    
    # add last phoneme
    lastTokenIdx = indicesStateStarts[-1]
    
    lastPhn = Phoneme(phonemesListNoPauses[lastTokenIdx][2]) 
    
    lastPhn.setBeginTs(phonemesListNoPauses[lastTokenIdx][0])
    lastPhn.setEndTs(phonemesListNoPauses[toPhonemeIdx][1])
    
    phonemesAnno.append(lastPhn)
    
    return phonemesAnno


def hasDuplicatedSyllables(phonemesAnno, phonemesDictSAMPA):
    
    '''
    x o x o -> x o
    '''
    phonemesAnnoStr = ''        
    for phoneme in phonemesAnno:
        phonemesAnnoStr += phoneme.ID
        
    phonemesDictSAMPAString = ''.join(phonemesDictSAMPA)
    phonemesDictSAMPAString += phonemesDictSAMPAString # concatenate twice string
    
    isDuplicated = 0
    if phonemesAnnoStr == phonemesDictSAMPAString:
        isDuplicated = 1
    return  isDuplicated




def loadPhonemesAnnoOneSyll(lyricsTextGrid, syllableIdx, syllable):
    '''
    load phonemes in XSAMPA from TextGrid. aggregate them if repeated 
    '''
    phonemesAnno,  syllableText = loadPhonemesFromAnno(lyricsTextGrid, syllableIdx)
#     if syllableText == '': #  empty syll
#          return phonemesAnno
     
        
    # duplicate phoneme sequences, hack: take first repetition only
    # split 2 phonemes from annotaion into equally sized. TODO: use rules. TODO: for 2 phonemes

    phonemesAnno = mergeDuplicateSyllablePhonemes(phonemesAnno, syllable.phonemes)
   
  
    return phonemesAnno, syllableText
    
    





def validatePhonemesOneSyll(lyricsTextGrid, syllableIdx, dictSyll2XSAMPA, syllable):
   
    phonemesDictSAMPAQueue, phonemesDictSAMPA = text2Phonemes(dictSyll2XSAMPA, syllable.text)
    
    phonemesAnno, syllableText = loadPhonemesAnnoOneSyll(lyricsTextGrid, syllableIdx, syllable)
    

    
    if syllableText == '': # nothing to validate. empty syll
        return
    
    
    ### CHECK if phonemes from annotation correspond to dictionary:
    
      #check phoneme identities
    phonemesAnnoStr = "".join(map(str,phonemesAnno))
    phonemesDictSAMPAQueueStr = "".join(phonemesDictSAMPAQueue)
    if phonemesAnnoStr != phonemesDictSAMPAQueueStr:
            logger.info("At  syllable {}. Phonemes in annotaion are {} and they shoud be {}".format(syllableText, phonemesAnno, phonemesDictSAMPAQueue))

    
#     if len(phonemesAnno) > len(phonemesDictSAMPAQueue):
#         if hasDuplicatedSyllables(phonemesAnno, phonemesDictSAMPA):
#             logger.debug(" syllables in annotaion  {} is duplicated".format(phonemesAnno, phonemesDictSAMPAQueue))
#         else:
#             logger.info(" More phonemes annotated for syllable {}. Phonemes in annotaion are {} and they shoud be {}".format(syllableText, phonemesAnno, phonemesDictSAMPAQueue))
#           
#         
#                 
#     else: 
#         if len(phonemesAnno) < len(phonemesDictSAMPAQueue):
# #         logger.warning(" Less phonemes annotated")
# #          syllables in annotaion are {} and they shoud be {}".format(phonemesAnno, phonemesDictSAMPAQueue))
# 
#         
#             for currPhoneme in phonemesAnno:
#                 dictPhoneme = phonemesDictSAMPAQueue.popleft()
#                 
#                 if not currPhoneme.ID == dictPhoneme:
#                     # divide into two
#                     logger.info("in annotation says {} but expected {} from dict".format(currPhoneme.ID, dictPhoneme)) # todo: put the two new back in queue
#     #                 pass
#                   
#             # missing phoneme
#             while not len(phonemesDictSAMPAQueue) == 0:
#                 phoneme = phonemesDictSAMPAQueue.popleft()
#                 logger.info( "in annotation phoneme {} is missing".format(phoneme))
#         
#       

def text2Phonemes(dictSyll2XSAMPA, syllableText):
    '''
    load list of phonemes from annotation TextGrid, sieve out duplicate  phonemes 
    return queue 
    '''
  
    
    if syllableText in dictSyll2XSAMPA:
        phonemesDictSAMPA = dictSyll2XSAMPA[syllableText]
    else:
        logger.warning(" syllable  {} not in dict".format(syllableText))
        consonants, consonants2, vocals, specials = loadXSAMPAPhonetizers()
        phonemesDictSAMPA = toXSAMPAPhonemes(syllableText, consonants, consonants2, vocals, specials)
        dictSyll2XSAMPA[syllableText] = phonemesDictSAMPA # add syllable to dict
    
    phonemesDictSAMPAQueue = tokenizePhonemes(phonemesDictSAMPA)
    
    return  phonemesDictSAMPAQueue, phonemesDictSAMPA


def loadPhonemesFromAnno(lyricsTextGrid, syllableIdx):
    '''
    For one syllable, load list of phonemes from annotation TextGrid, sieve out duplicate  phonemes 
    '''
    phonemesAnnoList, fromPhonemeIdx, toPhonemeIdx, syllableText, dummy = parsePhonemes(lyricsTextGrid, syllableIdx)
    
    if syllableText == '': # skip empty syllables
         
        phoenemeSil = Phoneme('sil')
        phoenemeSil.setBeginTs(phonemesAnnoList[fromPhonemeIdx][0])
        phoenemeSil.setEndTs(phonemesAnnoList[fromPhonemeIdx][1])
        phonemesAnno = [phoenemeSil]
        return phonemesAnno,syllableText
    
# details tier has same phoneme duplicated
    phonemesAnno = removeDuplicatePhonemes(phonemesAnnoList, fromPhonemeIdx, toPhonemeIdx)
    
    return phonemesAnno,  syllableText