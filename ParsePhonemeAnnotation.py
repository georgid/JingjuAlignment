'''
Created on Oct 6, 2015

@author: joro
'''

from lyricsParser import _findBeginEndIndices, stripPunctuationSigns,\
    divideIntoSentencesFromAnnoWithSil, divideIntoSentencesFromAnno
import os
import sys
from collections import deque
from aetools import Error

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


def validatePhonemesWholeAria(lyricsTextGrid):
    listSentences = divideIntoSentencesFromAnnoWithSil(lyricsTextGrid) #uses TextGrid annotation to derive structure. 
    dictSyll2XSAMPA = createDictSyll2XSAMPA()
    
    for whichSentence, currSentence in  enumerate(listSentences):
#         if whichSentence <3: continue
        fromSyllableIdx = currSentence[2]
        toSyllableIdx = currSentence[3]
        for syllableIdx in range(fromSyllableIdx,toSyllableIdx):
             
            validatePhonemesOneSyll(lyricsTextGrid, syllableIdx, dictSyll2XSAMPA)

def createDictSyll2XSAMPA():
        '''
        create table pinyin Syllables -> phonemes in XSAMPA 
        '''
        
        # load pinyin lyllables
        currDir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) )
        
        pinyinSyllDict = Phonetizer.readLookupTable(os.path.join(currDir, 'syl2phn46.txt'))

        # load mappings for consonants, vowels, specials
        consonants = Phonetizer.readLookupTable(os.path.join(currDir, 'syl2phoneme.consonants.txt'))
        consonants2 = Phonetizer.readLookupTable(os.path.join(currDir,'syl2phoneme.consonants2.txt'))

        vocals = Phonetizer.readLookupTable(os.path.join(currDir,'syl2phoneme.vowels.txt'))
        specials = Phonetizer.readLookupTable(os.path.join(currDir,'syl2phoneme.specials.txt'))
        
        mapDict = {}
        
        for pinyinSyll in pinyinSyllDict:
            
            xSampaPhonemes = []
            if pinyinSyll in specials:
               xSampaPhonemes = specials[pinyinSyll] 
               mapDict[pinyinSyll] = xSampaPhonemes
               continue # specials are whole syllable, so we are done
            
            foundConsonant = 0
            for consonant in consonants2:  # initial is consonant of two chars
                if pinyinSyll.startswith(consonant):
                    pinyinSyllRest = pinyinSyll[len(consonant):]
                    xSampaPhonemes.append(consonants2[consonant])
                    foundConsonant = 1     
                    break # cannot start with other consonant
                
            if not foundConsonant:  # initial is consonant of one char
                    for consonant in consonants: 
                        if pinyinSyll.startswith(consonant):
                            pinyinSyllRest = pinyinSyll[len(consonant):]
                            xSampaPhonemes.append(consonants[consonant])     
                            break # cannot start with other consonant
            
            for vocal in vocals:
                if pinyinSyllRest == vocal:
                    xSampaPhonemes.append(vocals[vocal])
                    break # cannot end with other vocal
                
            mapDict[pinyinSyll] = xSampaPhonemes       
                    

        return mapDict

def tokenizePhonemes(phonemesSAMPA):
    '''
    convert string phoneme representation of a syllable to a python list
    phonemes has initial and rest parts
    '''
    
    phonemesSAMPAQueue = deque([])

    #initial part
    if len(phonemesSAMPA) == 2:
        
        phonemesSAMPAQueue.append(phonemesSAMPA[0])
        phonemesSAMPARest = phonemesSAMPA[1]
    else:
        phonemesSAMPARest = phonemesSAMPA
    
    # tokenize
    charsSAMPA = list(phonemesSAMPARest)
    
    for char in charsSAMPA:
        if char == '^' or char == '"' or char=='\\' or char=="'":
            charsSAMPALast = phonemesSAMPAQueue.pop()
            charsSAMPALast += char
            phonemesSAMPAQueue.append(charsSAMPALast)
        
        else:
            phonemesSAMPAQueue.append(char)
    
#     if last == ''
    return phonemesSAMPAQueue


def parsePhonemes(lyricsTextGrid, syllableIdx):
    '''
    parse phonemes for given syllable
    '''
    highLevel = tierAliases.pinyin # read syllable in pinyin
    syllable, dummy = readNonEmptyTokensTextGrid(lyricsTextGrid, highLevel, syllableIdx, syllableIdx)
    
    lowLevel = tierAliases.details # read phonemesAnno
    dummy, phonemesListNoPauses = readNonEmptyTokensTextGrid(lyricsTextGrid, lowLevel, 0, -1)
    
    beginSyllableTs = syllable[0][0]
    endSyllableTs = syllable[0][1]
    syllablePinYinRaw = syllable[0][2].strip()
    isEndOfSentence, syllableText = stripPunctuationSigns(syllablePinYinRaw)
    
    if syllableText == '': # skip this syllable with no lyrics 
        return phonemesListNoPauses, -1, -1, syllableText 
    
    phonemesPointer = 0
    
    fromPhonemeIdx, toPhonemeIdx, dummy, dummy = _findBeginEndIndices(phonemesListNoPauses, phonemesPointer, beginSyllableTs, endSyllableTs, highLevel)
    
    return phonemesListNoPauses, fromPhonemeIdx, toPhonemeIdx, syllableText



def removeDuplicatePhonemes(phonemesListNoPauses, fromPhonemeIdx, toPhonemeIdx):
    
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
        phonemeText = phonemesListNoPauses[idx][2]
        beginTs = phonemesListNoPauses[idx][0]
        endTs = phonemesListNoPauses[idxLast][1]
       
        phonemesAnno.append((phonemeText, beginTs, endTs))
    
    # add last phoneme
    lastTokenIdx = indicesStateStarts[-1]
    phonemeText = phonemesListNoPauses[lastTokenIdx][2]
    beginTs = phonemesListNoPauses[lastTokenIdx][0]
    endTs = phonemesListNoPauses[toPhonemeIdx][1]
    
    phonemesAnno.append((phonemeText, beginTs, endTs))
    
    return phonemesAnno

def validatePhonemesOneSyll(lyricsTextGrid, syllableIdx, dictSyll2XSAMPA):
   
    phonemesListNoPauses, fromPhonemeIdx, toPhonemeIdx, syllableText = parsePhonemes(lyricsTextGrid, syllableIdx)
    if syllableText == '':
       return 
    
    # details tier has same phoneme repeating
    phonemesAnno = removeDuplicatePhonemes(phonemesListNoPauses, fromPhonemeIdx, toPhonemeIdx)
    
    if syllableText in dictSyll2XSAMPA:
        phonemesDictSAMPA = dictSyll2XSAMPA[syllableText]
    else:
        sys.exit(" syllable  {} not in dict".format(syllableText))
        
    phonemesDictSAMPAQueue = tokenizePhonemes(phonemesDictSAMPA)
    
    
    ### CHECK if phonemes from annotation correspond to dictionary:
    if len(phonemesAnno) > len(phonemesDictSAMPAQueue):
#         sys.exit(" syllables in annotaion are {} and they shoud be {}".format(phonemesAnno, phonemesDictSAMPAQueue))
#         print " syllables in annotaion are {} and they shoud be {}".format(phonemesAnno, phonemesDictSAMPAQueue)
        pass
                
    elif len(phonemesAnno) < len(phonemesDictSAMPAQueue):
        for currPhoneme in phonemesAnno:
            dictPhoneme = phonemesDictSAMPAQueue.popleft()
            
            if not currPhoneme[0] == dictPhoneme:
                # divide into two
#                 print "in annotation says {} but expected {} from dict".format(currPhoneme[0], dictPhoneme) # todo: put the two new back in queue
                  pass
              
        # missing phoneme
        while not len(phonemesDictSAMPAQueue) == 0:
            phoneme = phonemesDictSAMPAQueue.popleft()
#             print "in annotation phoneme {} is missing".format(phoneme)
    
    else: # syllables have same len
          pass  
#         print " all good: \n syllables in annotaion are {} and in dict : {}".format(phonemesAnno, phonemesDictSAMPAQueue)
