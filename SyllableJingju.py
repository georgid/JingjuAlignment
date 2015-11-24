'''
Created on Oct 8, 2014

@author: joro
'''
import os
import sys
import sys

from numpy.ma.core import ceil



parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 

pathHMMDuration = os.path.join(parentDir, 'AlignmentDuration')
if pathHMMDuration not in sys.path:
    sys.path.append(pathHMMDuration)


from Phoneme import Phoneme
from Phonetizer import Phonetizer
from _SyllableBase import _SyllableBase


from hmm.ParametersAlgo import ParametersAlgo
import logging 

logger = logging.getLogger(__name__)

class SyllableJingju(_SyllableBase):
        ''' syllables class for each chinse/jingju phoneme (using phonemeSet mandarin from Weng Lei)
        BUT not meant to be used alone, instead Syllable is a part of a Word class
        '''
        def __init__(self, text, noteNum):
            _SyllableBase.__init__(self, text, noteNum)
           
#         def get_Duration(self):
#             return self.duration    
        
            self.durationPhonemes = None
        
        def createPhonemeClasses(self, phonemesList):
            '''
            no mapping to turkish
            '''
            for phonemeID in phonemesList:
                self.phonemes.append(Phoneme(phonemeID))
            
            if self.hasShortPauseAtEnd:
                self.phonemes.append(Phoneme('sp'))


        def mandarin2METUbet(self, mandarinPhonemes):
            '''
            create Phonemes objects form phoneme IDs. map to turkish METU
            '''
            if not Phonetizer.lookupTable:
                sys.exit("Phonetizer.lookupTable not defined. do Phonetizer.initlookupTable at beginning of all code")
            
            turkihMETUphonemeIDs = []
            for ph in mandarinPhonemes:
                turkihMETUphonemeIDs = Phonetizer.grapheme2phonemeList(ph, turkihMETUphonemeIDs)
            
        #### create Phonemes as field
            self.createPhonemeClasses(turkihMETUphonemeIDs)


        def expandToPhonemes(self):
            '''
            one-to-one function: PINYIN characters to turkish METU. 
            as intermediate step mandarin phoneset are used.   
            '''
            self.text = self.text.strip()
            
            ######################
            ### pinyin to mandarin phonemeSet
            if not Phonetizer.phoneticDict:
                sys.exit("Phonetizer.phonetic Dict not defined. do Phonetizer.initPhoneticDict at beginning of all code")   
            
            self.phonemes = []    

            #  notes for instrument
            if self.text == 'REST':
                # TODO: replace with other model instead of silence
                self.phonemes.append(Phoneme('sil'))
                # TODO: does sp at end of sp make sence? 
#                 self.phonemes.append(Phoneme('sp'))
                self.hasShortPauseAtEnd = False
                return
            
            if self.text not in Phonetizer.phoneticDict:
                sys.exit("unknown syllable {} Please add it to the dict".format(self.text))
                  
            mandarinPhonemes = Phonetizer.phoneticDict[self.text]
              
            ####################
            #### create Phonemes objects form phoneme IDs. map to turkish METU
            
            self.mandarin2METUbet(mandarinPhonemes)
#             self.createPhonemeClasses(mandarinPhonemes)
        

        
        def calcPhonemeDurations(self):
            '''
            rule-based assignment of durations using Initial-Middle-final rules
            all consonant durations set to CONSONANT_DURATION 
                        '''
            cofficinetTempo = 1
            
            if self.phonemes is None:
                self.expandToPhonemes()
            
            if self.getNumPhonemes() == 0:
                sys.exit("syllable {} with no phonemes!".format(self.text))
                return
            
            
            #copy to local var
            consonant_duration = ParametersAlgo.CONSONANT_DURATION
            
            # Workaround: reduce consonant durationInMinUnit for syllables with very short note value. 
            while (self.getNumPhonemes() - 1) * consonant_duration >= self.durationInNumFrames:
                logger.warn("Syllable {} has very short durationInMinUnit: {} . reducing the fixed durationInMinUnit of consonants".format(self.text, self.durationInMinUnit) )
                consonant_duration /=2
            
            #################
            ## assign durations 
            #############
            
          
            initPhoneme = self.phonemes[0]
            finalPhoneme = self.phonemes[-1]
            
#                               
            if not initPhoneme.isVowel():  # initial is consonant
                initPhoneme.durationInNumFrames = consonant_duration

                if not finalPhoneme.isVowel():                 # final is consonant
                    finalPhoneme.durationInNumFrames = consonant_duration
                    for currPhoneme in self.phonemes[1:-1]:
                        currPhoneme.durationInNumFrames = (self.durationInNumFrames - 2 * consonant_duration) / len(self.phonemes[1:-1])
                        
                else:   # final is vowel
                    dur = (self.durationInNumFrames - float(consonant_duration) ) / len(self.phonemes[1:])
                    ceilDur = int(ceil(dur))
                    for currPhoneme in self.phonemes[1:-1]:
                        currPhoneme.durationInNumFrames = ceilDur
                    finalPhoneme.durationInNumFrames = self.durationInNumFrames - (len(self.phonemes[1:-1]) * ceilDur)
            
            else: # initial is vowel
                if not finalPhoneme.isVowel(): 
                    finalPhoneme.durationInNumFrames = consonant_duration
                    for currPhoneme in self.phonemes[:-1]:
                        currPhoneme.durationInNumFrames = (self.durationInNumFrames -   consonant_duration) / len(self.phonemes[:-1])
                else:   # final is vowel
                    for currPhoneme in self.phonemes:
                        currPhoneme.durationInNumFrames = self.durationInNumFrames / len(self.phonemes) 
     

       