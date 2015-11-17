'''
Created on Nov 6, 2015

@author: joro
'''
from lyricsParser import splitThePhoneme, mergeDuplicateSyllablePhonemes,\
    syllables2Lyrics, createSyllable
from Phoneme import Phoneme
from PhonetizerDict import tokenizePhonemes
from SyllableJingju import SyllableJingju

def testSplitThePhoneme():
    
    doublePhoneme = Phoneme('eI^')
    doublePhoneme.setBeginTs(1.4)
    doublePhoneme.setEndTs(1.8)
    
    firstPhoenemeTxt = 'e'
    ph1 , ph2 = splitThePhoneme(doublePhoneme, firstPhoenemeTxt)
    print ph1
    
def testMergeDuplicateSyllablePhonemes():
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
    phonemesAnnoSplit = mergeDuplicateSyllablePhonemes(phonemesAnno, phonemesDictSAMPAQueue)
    print phonemesAnnoSplit

def testMergeDuplicateSyllablePhonemes3():
    phonemesAnno = []
    
    
    doublePhoneme = Phoneme('j')
    doublePhoneme.setBeginTs(1.4)
    doublePhoneme.setEndTs(1.8)
    phonemesAnno.append(doublePhoneme)
    
    doublePhoneme2 = Phoneme('En')
    doublePhoneme2.setBeginTs(2.4)
    doublePhoneme2.setEndTs(2.8)
    phonemesAnno.append(doublePhoneme2)
    
    syllablesLIst = []
    syllablesLIst = createSyllable(syllablesLIst, 'yan')
    
    lyrics = syllables2Lyrics(syllablesLIst)
    syllable = lyrics.listWords[0].syllables[0]
   
    phonemesAnnoSplit = mergeDuplicateSyllablePhonemes(phonemesAnno, syllable.phonemes)
    print phonemesAnnoSplit



def testMergeDuplicateSyllablePhonemes2():
    phonemesAnno = []
    
    
    
    doublePhoneme = Phoneme('@')
    doublePhoneme.setBeginTs(1.4)
    doublePhoneme.setEndTs(1.8)
    phonemesAnno.append(doublePhoneme)
    
    doublePhoneme2 = Phoneme("r\\'")
    doublePhoneme2.setBeginTs(2.4)
    doublePhoneme2.setEndTs(2.8)
    phonemesAnno.append(doublePhoneme2)
    
    doublePhoneme3 = Phoneme('')
    doublePhoneme3.setBeginTs(2.9)
    doublePhoneme3.setEndTs(2.94)
    phonemesAnno.append(doublePhoneme3)
    
    doublePhoneme4 = Phoneme("r\\'")
    doublePhoneme4.setBeginTs(3.1)
    doublePhoneme4.setEndTs(3.9)
    phonemesAnno.append(doublePhoneme4)
    
    syllablesLIst = []
    syllablesLIst = createSyllable(syllablesLIst, 'er')
    
    lyrics = syllables2Lyrics(syllablesLIst)
    syllable = lyrics.listWords[0].syllables[0]
    
    phonemesAnnoSplit = mergeDuplicateSyllablePhonemes(phonemesAnno, syllable.phonemes)
    print phonemesAnnoSplit

if __name__ == '__main__':
#     testSplitThePhoneme()
#     testMergeDuplicateSyllablePhonemes()
    testMergeDuplicateSyllablePhonemes3()