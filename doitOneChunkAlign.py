'''
Created on Oct 13, 2014

@author: joro
'''
import sys
import os
from MusicXmlParser import MusicXMLParser, syllables2Lyrics
from lyricsParser import loadLyricsFromTextGridSentence,\
    parsePhonemeIdxsFromTextGrid



parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 

pathUtils = os.path.join(parentDir, 'utilsLyrics')
if pathUtils not in sys.path:
    sys.path.append(pathUtils)
from Utilz import writeListToTextFile


pathEvaluation = os.path.join(parentDir, 'AlignmentEvaluation')
if pathEvaluation not in sys.path:
    sys.path.append(pathEvaluation)
from PraatVisualiser import tokenList2TabFile



pathHMMDuration = os.path.join(parentDir, 'AlignmentDuration')
if pathHMMDuration not in sys.path:
    sys.path.append(pathHMMDuration)


# parser of htk-build speech model
pathHtkModelParser = os.path.join(parentDir, 'htkModelParser')
sys.path.append(pathHtkModelParser)
from htk_converter import HtkConverter



from Phonetizer import Phonetizer

from SymbTrParser import createWord

from Lyrics import Lyrics
from LyricsWithModels import LyricsWithModels
    
from WordLevelEvaluator import readNonEmptyTokensTextGrid
from AccuracyEvaluator import _evalAccuracy
from FeatureExtractor import loadMFCCs
from doitOneChunk import alignOneChunk


pathHMM = os.path.join(parentDir, 'HMMDuration')
from hmm.examples.main  import loadSmallAudioFragment,  parsePhoenemeAnnoDursOracle

from Utilz import readListOfListTextFile

ANNOTATION_EXT = '.TextGrid'
evalLevel = 3 



def doitOneChunkAlign(URIrecordingNoExt, musicXMLParser,  whichSentence, currSentence, withOracle, withDurations, withVocalPrediction):
    '''
    align one chunk only.
    @param musicXMLParser: parsed  score for whole recording
    @param whichSentence: sentence number to process  
    '''

    fromTs = currSentence[0]
    toTs = currSentence[1]
    
    listNonVocalFragments = []
    if withVocalPrediction:
        listNonVocalFragments = getListNonVocalFragments(URIrecordingNoExt, fromTs, toTs)
    
    
    if (withDurations):
        tokenLevelAlignedSuffix = '.syllables_dur'
    else:
        if withOracle:
            tokenLevelAlignedSuffix = '.syllables_oracle'
        else:
            tokenLevelAlignedSuffix = '.syllables'

    fromSyllableIdx = currSentence[2]
    toSyllableIdx = currSentence[3]
    
   
    ###### 1) load Lyrics
    lyrics = loadLyricsFromTextGridSentence(currSentence)
    
    if withDurations: # load from score instead
        lyrics = musicXMLParser.getLyricsForSection(whichSentence) # indexing in python

    withSynthesis = True

    ##### align
    usePersistentFiles = 'False'
    alpha = 0.97
    from hmm.Parameters import Parameters
    ONLY_MIDDLE_STATE = False
    params  = Parameters(alpha, ONLY_MIDDLE_STATE)
    
    lyricsWithModelsORacle = 'dummy'
    if withOracle:
        # get start and end phoneme idx from TextGrid
        phonemeListExtracted = parsePhonemeIdxsFromTextGrid(URIrecordingNoExt + ANNOTATION_EXT, fromSyllableIdx, toSyllableIdx)
        lyricsWithModelsORacle = parsePhoenemeAnnoDursOracle(lyrics, phonemeListExtracted )
     
        
    detectedTokenList, detectedPath = alignOneChunk( lyrics, withSynthesis, withOracle, lyricsWithModelsORacle, listNonVocalFragments, alpha, evalLevel, usePersistentFiles, tokenLevelAlignedSuffix, fromTs, toTs, URIrecordingNoExt)
    

    correctDuration, totalDuration = _evalAccuracy(URIrecordingNoExt + ANNOTATION_EXT, detectedTokenList, evalLevel, fromSyllableIdx, toSyllableIdx  )
    acc = correctDuration / totalDuration
    print "result is: " + str(acc)
    
    return correctDuration, totalDuration



def getListNonVocalFragments(URIrecordingNoExt, fromTs, toTs):
    segmentationDir = os.path.join(parentDir, 'segmentation')
    if segmentationDir not in sys.path:
        sys.path.append(segmentationDir)
    from assignNonVocals import assignNonVocals
### derive name URI of prediction file
    URIRecName = os.path.basename(URIrecordingNoExt)
    token1 = URIRecName.split('-')[0]
    tokens = URIRecName.split('-')[1].split('_')
    token2 = tokens[0]
    token3 = tokens[1]
    VJPpredictionFile = segmentationDir + '/data/output_VJP_' + token1 + token2 + token3 + '/predictionVJP.txt' #     VJPpredictionFile = '/Users/joro/Documents/Phd/UPF/voxforge/myScripts/segmentationShuo/data/output_VJP_laoshengerhuang04/predictionVJP.txt'
    #     VJPpredictionFile = '/Users/joro/Documents/Phd/UPF/voxforge/myScripts/segmentationShuo/data/output_VJP_danxipi01/predictionVJP.txt'
    listNonVocalFragments = assignNonVocals(VJPpredictionFile, fromTs, toTs)
    return listNonVocalFragments


