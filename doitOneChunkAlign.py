'''
Created on Oct 13, 2014

@author: joro
'''
import sys
import os
from lyricsParser import createSyllables, divideIntoSectionsFromAnno
from MusicXmlParser import MusicXMLParser, syllables2Lyrics



parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 

pathUtils = os.path.join(parentDir, 'utilsLyrics')
if pathUtils not in sys.path:
    sys.path.append(pathUtils)
from Utilz import writeListToTextFile


pathEvaluation = os.path.join(parentDir, 'AlignmentEvaluation')
if pathEvaluation not in sys.path:
    sys.path.append(pathEvaluation)
from PraatVisualiser import tokenList2TabFile



pathAlignmentDuration = os.path.join(parentDir, 'AlignmentDuration')
if pathAlignmentDuration not in sys.path:
    sys.path.append(pathAlignmentDuration)


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
from hmm.examples.main  import loadSmallAudioFragment

from Utilz import readListOfListTextFile

ANNOTATION_EXT = '.TextGrid'
evalLevel = 3 

segmentationDir = os.path.join(parentDir, 'segmentation')
if segmentationDir not in sys.path: sys.path.append(segmentationDir)
from assignNonVocals import assignNonVocals



def doitOneChunkAlign(URIrecordingNoExt, musicXMLParser,  whichSentence, currSentence, withScores, withVocalPrediction):
    

    fromTs = currSentence[0]
    toTs = currSentence[1]
    
    listNonVocalFragments = []
    if withVocalPrediction:

        ### derive name URI of prediction file
        URIRecName = os.path.basename(URIrecordingNoExt)
        token1 = URIRecName.split('-')[0]
        tokens = URIRecName.split('-')[1].split('_')
        token2 = tokens[0]
        token3 = tokens[1]
        VJPpredictionFile = segmentationDir + '/data/output_VJP_' + token1 + token2 + token3 + '/predictionVJP.txt'
    #     VJPpredictionFile = '/Users/joro/Documents/Phd/UPF/voxforge/myScripts/segmentationShuo/data/output_VJP_laoshengerhuang04/predictionVJP.txt'
    #     VJPpredictionFile = '/Users/joro/Documents/Phd/UPF/voxforge/myScripts/segmentationShuo/data/output_VJP_danxipi01/predictionVJP.txt'
        listNonVocalFragments = assignNonVocals(VJPpredictionFile, fromTs, toTs)
    
    URIRecordingChunk = URIrecordingNoExt + "_" + str(fromTs) + '_' + str(toTs) + '.wav'
    if (withScores):
        tokenLevelAlignedSuffix = '.syllables_dur'
    else:
        tokenLevelAlignedSuffix = '.syllables'

    detectedAlignedfileName = os.path.splitext(URIRecordingChunk)[0] + tokenLevelAlignedSuffix

    fromSyllable = currSentence[2]
    toSyllable = currSentence[3]
    
    # already decoded
    if os.path.isfile(detectedAlignedfileName):
        print "{} already exists. No decoding".format(detectedAlignedfileName)
        detectedTokenList  = readListOfListTextFile(detectedAlignedfileName)
        correctDuration, totalDuration = _evalAccuracy(URIrecordingNoExt + ANNOTATION_EXT, detectedTokenList, evalLevel, fromSyllable, toSyllable  )
#         correctDuration= 0; totalDuration=1 
        return correctDuration, totalDuration 
    
    
    
    REF_SYLLABLE_DUR_IN_MIN_UNIT = 4
    # deviationInSec
    
    ###### 1) load Lyrics
    Phonetizer.initLookupTable(True,  'phonemeMandarin2METUphonemeLookupTableSYNTH')
    
    
    if withScores: 
        lyrics = musicXMLParser.getLyricsForSection(whichSentence) # indexing in python
#         lyrics.printSyllables()

            
    else:
        syllables = currSentence[4]
        lyrics = syllables2Lyrics(syllables)
#         lyrics.printSyllables()
        

    withSynthesis = True
#     2) load features
    lyricsWithModels, obsFeatures  = loadSmallAudioFragment(lyrics,  URIrecordingNoExt, withSynthesis, fromTs, toTs)
    
    
    ##### align
    usePersistentFiles = 'False'
    alpha = 0.97
    from hmm.Parameters import Parameters
    ONLY_MIDDLE_STATE = False
    params  = Parameters(alpha, ONLY_MIDDLE_STATE)
    
    alignmentErrors, detectedTokenList, dummycorrectDuration, dummytotalDuration = alignOneChunk(obsFeatures, lyricsWithModels, listNonVocalFragments, alpha, evalLevel, usePersistentFiles, tokenLevelAlignedSuffix, URIrecordingNoExt)
    
    # store decoding results in a file FIXME: if with duration it is not mlf 
    detectedAlignedfileName =  tokenList2TabFile(detectedTokenList, os.path.splitext(URIRecordingChunk)[0], tokenLevelAlignedSuffix)

    correctDuration, totalDuration = _evalAccuracy(URIrecordingNoExt + ANNOTATION_EXT, detectedTokenList, evalLevel, fromSyllable, toSyllable  )
    acc = correctDuration / totalDuration
    print "result is: " + str(acc)
    
    
    
    return correctDuration, totalDuration

#### this is example usage, not part of the library
if __name__ == '__main__':
        
        rootURI = '/Users/joro/Documents/Phd/UPF/arias_dev_01_t_70/'
        URIrecordingNoExt =  rootURI + 'laosheng-erhuang_04'
        URIrecordingNoExt =  rootURI + 'laosheng-xipi_02'
#         URIrecordingNoExt =  rootURI + 'dan-xipi_02'
        
        URIrecordingNoExt =  rootURI + 'dan-xipi_01'
        lyricsTextGrid = URIrecordingNoExt + '.TextGrid'

        # load ts for different sentences
#         fromTss, toTss = loadSectionTimeStamps(sectionAnnoURI)
        listSentences = divideIntoSectionsFromAnno(lyricsTextGrid)
        
        withScores  = 1
        musicXMLParser = None
        
        if withScores:
            musicXmlURI = URIrecordingNoExt + '_score.xml'
            musicXMLParser = MusicXMLParser(musicXmlURI, lyricsTextGrid)
        
        withVocalPrediction = 1
        for whichSentence, currSentence in  enumerate(listSentences):
            correctDuration, totalDuration = doitOneChunkAlign(URIrecordingNoExt, musicXMLParser,  whichSentence, currSentence, withScores, withVocalPrediction)
    

