'''
Created on Sep 18, 2015

@author: joro
'''
from lyricsParser import divideIntoSectionsFromAnno
from doitOneChunkAlign import loadLyricsFromTextGridSentence
import os
import sys

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 

pathEvaluation = os.path.join(parentDir, 'AlignmentEvaluation')
if pathEvaluation not in sys.path:
    sys.path.append(pathEvaluation)

pathHMMDuration = os.path.join(parentDir, 'HMMDuration')
if pathHMMDuration not in sys.path:
    sys.path.append(pathHMMDuration)
from hmm.examples.main import decodeWithOracle

from AccuracyEvaluator import _evalAccuracy




def test_oracle_jingju(URIrecordingNoExt,  whichSentence, fromPhonemeIdx, toPhonemeIdx):
    '''
    read phoneme-level ground truth and test with dan-xipi_02
    '''
    
    ANNOTATION_EXT = '.TextGrid'
    listSentences = divideIntoSectionsFromAnno(URIrecordingNoExt + ANNOTATION_EXT) #uses TextGrid annotation to derive structure. TODO: instead of annotation, uses score
    
    withSynthesis = False
    currSentence = listSentences[whichSentence]
    
    # consider only part of audio
  
    fromTs = currSentence[0]
    toTs = currSentence[1]

    
    lyrics = loadLyricsFromTextGridSentence(currSentence)
    
    tokenLevelAlignedSuffix = '.syllables_oracle'
    detectedAlignedfileName = URIrecordingNoExt + '_' + str(fromTs) + '_' + str(toTs) + '_'  + tokenLevelAlignedSuffix
    
    if os.path.isfile(detectedAlignedfileName):
        print "{} already exists. No decoding".format(detectedAlignedfileName)
        
        from Utilz import readListOfListTextFile
        detectedTokenList  = readListOfListTextFile(detectedAlignedfileName)
        
    else:
        detectedTokenList = decodeWithOracle(lyrics, URIrecordingNoExt, fromTs, toTs, fromPhonemeIdx, toPhonemeIdx)
          
        if not os.path.isfile(detectedAlignedfileName):
            from PraatVisualiser import tokenList2TabFile
            detectedAlignedfileName =  tokenList2TabFile(detectedTokenList, URIrecordingNoExt, tokenLevelAlignedSuffix)
            
          
        
    # eval on phrase level
    evalLevel = 2
    
    fromSyllable = currSentence[2]
    toSyllable = currSentence[3]
    

    correctDuration, totalDuration = _evalAccuracy(URIrecordingNoExt + ANNOTATION_EXT, detectedTokenList, evalLevel, fromSyllable, toSyllable )
    print "accuracy= {}".format(correctDuration / totalDuration)
    
    return detectedTokenList


if __name__ == '__main__':
    
    
    
    URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/arias_dev_01_t_70/dan-xipi_02'
    
#     whichSentence = 0
#     fromPhonemeIdx  = 2; toPhonemeIdx = 30

    
    whichSentence = 1
    fromPhonemeIdx  = 33; toPhonemeIdx = 45
    
    whichSentence = 2
    fromPhonemeIdx  = 47; toPhonemeIdx = 173
    
    test_oracle_jingju(URIrecordingNoExt,  whichSentence, fromPhonemeIdx, toPhonemeIdx)

    