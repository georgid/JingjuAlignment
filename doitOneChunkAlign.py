'''
Created on Oct 13, 2014

@author: joro
'''
import sys
import os
from lyricsParser import syllables2Lyrics
from ParsePhonemeAnnotation import loadPhonemesAnnoOneSyll



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
    
from WordLevelEvaluator import readNonEmptyTokensTextGrid
from AccuracyEvaluator import _evalAccuracy
from FeatureExtractor import loadMFCCs
from doitOneChunk import alignOneChunk


pathHMM = os.path.join(parentDir, 'HMMDuration')
from hmm.examples.main  import   loadSmallAudioFragmentOracle
from hmm.ParametersAlgo import ParametersAlgo


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
    
    deviation = str(ParametersAlgo.DEVIATION_IN_SEC)

    if (withDurations):
        tokenLevelAlignedSuffix = '.syllables_dur_gmm'
    else:
        if withOracle:
            tokenLevelAlignedSuffix = '.syllables_oracle'
        else:
            tokenLevelAlignedSuffix = '.syllables'
    
    tokenLevelAlignedSuffix += '_' + deviation 
            
    fromSyllableIdx = currSentence[2]
    toSyllableIdx = currSentence[3]
    
   
    ###### 1) create Lyrics
    syllables = currSentence[4]
    lyrics = syllables2Lyrics(syllables)
    
    if withDurations: # load from score instead
        lyrics = musicXMLParser.getLyricsForSection(whichSentence) # indexing in python

    withSynthesis = False

    ##### align
    usePersistentFiles = 'False'
    alpha = 0.97
    from hmm.Parameters import Parameters
    ONLY_MIDDLE_STATE = False
    params  = Parameters(alpha, ONLY_MIDDLE_STATE)

     
    phonemesAnnoAll = 'dummy'
     
    if withOracle:
         
        # get start and end phoneme indices from TextGrid
        phonemesAnnoAll = []
        for idx, syllableIdx in enumerate(range(fromSyllableIdx,toSyllableIdx+1)): # for each  syllable including silent syllables
            # go through the phonemes. load all 
            currSyllable = lyrics.listWords[idx].syllables[0]
            phonemesAnno, syllableTxt = loadPhonemesAnnoOneSyll(URIrecordingNoExt + ANNOTATION_EXT, syllableIdx, currSyllable)
            phonemesAnnoAll.extend(phonemesAnno)
         
#       # TODO: compare format of phonemeListExtracted
#         lyricsWithModelsORacle = hmm.examples.main.loadSmallAudioFragmentOracle(lyrics, phonemeListExtracted )
#          
    detectedTokenList, detectedPath = alignOneChunk( lyrics, withSynthesis, withOracle, phonemesAnnoAll, listNonVocalFragments, alpha, evalLevel, usePersistentFiles, tokenLevelAlignedSuffix, fromTs, toTs, URIrecordingNoExt)
     


   


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


