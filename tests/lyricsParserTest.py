'''
Created on Nov 6, 2015

@author: joro
'''
from lyricsParser import splitThePhoneme, splitDuplicateSyllablePhonemes
from Phoneme import Phoneme
from PhonetizerDict import tokenizePhonemes

def testSplitThePhoneme():
    
    doublePhoneme = Phoneme('eI^')
    doublePhoneme.setBeginTs(1.4)
    doublePhoneme.setEndTs(1.8)
    
    firstPhoenemeTxt = 'e'
    ph1 , ph2 = splitThePhoneme(doublePhoneme, firstPhoenemeTxt)
    print ph1
    
def testSplitDuplicateSyllablePhonemes():
    phonemesAnno = []
    
    doublePhoneme = Phoneme('eI^')
    doublePhoneme.setBeginTs(1.4)
    doublePhoneme.setEndTs(1.8)
    phonemesAnno.append(doublePhoneme)
    
    doublePhoneme2 = Phoneme('eI^')
    doublePhoneme2.setBeginTs(2.4)
    doublePhoneme2.setEndTs(2.8)
    phonemesAnno.append(doublePhoneme2)
    
    phonemesDictSAMPA = 'eI^'
    phonemesDictSAMPAQueue = tokenizePhonemes(phonemesDictSAMPA)
    phonemesAnnoSplit = splitDuplicateSyllablePhonemes(phonemesAnno, phonemesDictSAMPAQueue)
    print phonemesAnnoSplit

if __name__ == '__main__':
#     testSplitThePhoneme()
    testSplitDuplicateSyllablePhonemes()