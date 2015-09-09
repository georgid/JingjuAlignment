# -*- coding: utf-8 -*-
'''
Created on Jun 14, 2015

@author: joro
'''
from music21 import *
from SyllableJingju import SyllableJingju
from cjklib.reading import ReadingFactory
import logging

from Lyrics import Lyrics
from Word import Word
from Phonetizer import Phonetizer
from lyricsParser import createSyllables, stripPunctuationSings
import sys
import os.path

# 64th of note
MIN_DUR_UNIT = 64

class MusicXMLParser(object):
    '''
    infer duration of lyrics from score. 
    loops though all notes and rests sequentially
    a new syllable start, whenever a text is attached to a note (a pause after a note is considered a syllable with no text)
    if no text, add note values to current syllable  
    '''

    
    def __init__(self, MusicXmlURI, lyricsTextGrid):
        '''
        Constructor
        '''
        self._loadSyllables( MusicXmlURI, lyricsTextGrid)
        
#        lyrics for each sentence/line 
        self.listSentences = []
        self.divideIntoSections()
        
        # list of  section names and their lyrics. 
        self.sectionLyrics = []
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
    
    
    def _loadSyllables(self, MusicXmlURI, lyricsTextGrid):
        '''
        top=most method
        '''
        self.listSyllables = []
        
        if not os.path.isfile(MusicXmlURI):
            sys.exit("file {} does not exist, please name it so".format(MusicXmlURI))
        score = converter.parse(MusicXmlURI)
        notesAndRests = score.flat.notesAndRests
        currSyllable = None
        currSyllTotalDuration = None
        
        for noteOrRest in notesAndRests:
            currSyllable, currSyllTotalDuration = self.parseCurrTxtToken(currSyllable, currSyllTotalDuration, noteOrRest)
        
        # last syllable
        currSyllable.setDurationInMinUnit(currSyllTotalDuration)
        self.listSyllables.append(currSyllable)
        
        ##### here workaround for not reading lyrics
        
        
        syllablesAllPinyin = createSyllables(lyricsTextGrid, -1, -1 )
        
        counter = 0
        for syl in self.listSyllables:
            if syl.text == 'REST':
                pass
            else:
                if counter == len(syllablesAllPinyin):
                    sys.exit(" syllable {} is last available from syllablesPinyin".format(syllablesAllPinyin[counter-1].text))
                print "mandarin:{}and pinyin: {} ".format(syl.text, syllablesAllPinyin[counter].text)
                syl.text = syllablesAllPinyin[counter].text
                counter +=1
        print "len syllables in muicXML= {} and len syllables in TextGrid = {}".format(counter, len(syllablesAllPinyin))

        # end of workaround 
        
    def divideIntoSections(self):
        '''
        same as lyricsParser.divideIntoSections just class variable name self.listSyllable is different
        '''
        
        currSectionLyrics =  []
        for syl in self.listSyllables:
            isEndOfSentence, syl.text = stripPunctuationSings(syl.text)
            if isEndOfSentence:
                
                currSectionLyrics.append(syl)
                self.listSentences.append(currSectionLyrics)
                currSectionLyrics =  []
            else:
                currSectionLyrics.append(syl)

        
    def parseCurrTxtToken(self, currSyllable, syllTotalDuration, noteOrRest):
        '''
        discriminate between cases with or without lyrics and rest and no rest
        '''
        currNoteDuration = noteOrRest.duration.quarterLength * MIN_DUR_UNIT / 4
#         self.logger.debug("currNoteDuration: {}".format(currNoteDuration))
#         print "currNoteDuration: {}".format(currNoteDuration)
        if noteOrRest.isRest:
            if not (currSyllable is None) and not (syllTotalDuration is None):
                if currSyllable.text == 'REST':
                    if not (currSyllable is None) and not (syllTotalDuration is None):
                        syllTotalDuration = syllTotalDuration + currNoteDuration
                else:
                    textPinYin = 'REST'
                    currSyllable, syllTotalDuration = self.finishCurrentAndCreateNewSyllable(textPinYin, currSyllable, syllTotalDuration, currNoteDuration)

                
        # '' (no lyrics at note) so still at same syllable
        elif noteOrRest.isNote:
            if (not noteOrRest.hasLyrics()) or (noteOrRest.hasLyrics() and noteOrRest.lyrics[0].text.strip().startswith('（') or noteOrRest.lyrics[0].text.strip()==''):
                if not (currSyllable is None) and not (syllTotalDuration is None):
                    syllTotalDuration = syllTotalDuration + currNoteDuration
        
            else: # has lyrics => has end of curr syllable
                lyrics = noteOrRest.lyrics
                if len(lyrics) > 1: # sanity check
                    print "syllable {} has {} characters".format(lyrics, len(lyrics))
                # convert to pinyin: maybe use this instead: https://pypi.python.org/pypi/pinyin/0.2.5
                if len(lyrics) != 0: # skip lyrics of len 0
                    f = ReadingFactory()
                    a = lyrics[0].text
                    textPinYin = f.convert(a, 'MandarinBraille', 'Pinyin')

                    currSyllable, syllTotalDuration = self.finishCurrentAndCreateNewSyllable(textPinYin, currSyllable, syllTotalDuration, currNoteDuration)
        
        return currSyllable, syllTotalDuration


    def finishCurrentAndCreateNewSyllable(self, textSyllable, currSyllable, syllTotalDuration, noteValue):
        if not (currSyllable is None) and not (syllTotalDuration is None): # save last syllable and duration
            currSyllable.setDurationInMinUnit(syllTotalDuration)
            self.listSyllables.append(currSyllable)
        
         # init next syllable and its duration
        dummyNote = -1
        currSyllable = SyllableJingju(textSyllable, dummyNote)
        syllTotalDuration = noteValue
        return currSyllable, syllTotalDuration
    
    def getLyricsForSection(self, whichSection):
        syllables = self.listSentences[whichSection]
        return syllables2Lyrics(syllables)

def syllables2Lyrics(syllables):
        
        listWords = []
        for syllable in syllables:
            # word of only one syllable
            word, dummy = createWord([], syllable)
            listWords.append(word)
    

        # load phonetic dict 
        Phonetizer.initPhoneticDict('syl2phn46.txt')                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
    
        ## 3) create lyrics
        # here is called Syllable.expandToPhonemes.
        lyrics = Lyrics(listWords)
        return lyrics

        


def createWord(syllablesInCurrWord, currSyllable):
        '''
        create a new word ending in currect syllable  
        '''        
        currSyllable.text = currSyllable.text.rstrip()
        currSyllable.setHasShortPauseAtEnd(True)
        syllablesInCurrWord.append(currSyllable)
    # create new word
        word = Word(syllablesInCurrWord)
        return word, syllablesInCurrWord   
    
    
if __name__=='__main__':
    MusicXmlURI = '/Users/joro/Documents/Phd/UPF/arias/dan-xipi_01_score.xml'
    lyricsTextGrid = '/Users/joro/Documents/Phd/UPF/arias/dan-xipi_01.TextGrid'
    
    
    MusicXmlURI = '/Users/joro/Documents/Phd/UPF/arias_dev_01_t_70/dan-xipi_02_score.xml'
    lyricsTextGrid = '/Users/joro/Documents/Phd/UPF/arias_dev_01_t_70/dan-xipi_02.TextGrid'

    musicXMLParser = MusicXMLParser(MusicXmlURI, lyricsTextGrid)
    
    Phonetizer.initLookupTable(True,  'phonemeMandarin2METUphonemeLookupTableSYNTH')

    for i in range(len(musicXMLParser.listSentences)):
        print i, " ",  musicXMLParser.getLyricsForSection(i)
    
#     for syll in musicXMLParser.listSyllables:
#         print syll