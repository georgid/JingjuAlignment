'''
Created on Oct 13, 2014

@author: joro
'''
import sys
import os
from ParsePhonemeAnnotation import loadPhonemesAnnoOneSyll
from SentenceJingju import SentenceJingju
from lyricsParser import createSyllable
from MusicXmlParser import mandarinToPinyin



parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 

# pathUtils = os.path.join(parentDir, 'utilsLyrics')
# if pathUtils not in sys.path:
#     sys.path.append(pathUtils)
from utilsLyrics.Utilz import writeListToTextFile, tokenList2TabFile, readListOfListTextFile


pathEvaluation = os.path.join(parentDir, 'AlignmentEvaluation')
if pathEvaluation not in sys.path:
    sys.path.append(pathEvaluation)



pathHMMDuration = os.path.join(parentDir, 'AlignmentDuration')
if pathHMMDuration not in sys.path:
    sys.path.append(pathHMMDuration)


# parser of htk-build speech model
# pathHtkModelParser = os.path.join(parentDir, 'htkModelParser')
# sys.path.append(pathHtkModelParser)
from htkparser.htk_converter import HtkConverter



from Phonetizer import Phonetizer

from SymbTrParser import createWord

from Lyrics import Lyrics
    
from WordLevelEvaluator import readNonEmptyTokensTextGrid
from AccuracyEvaluator import _evalAccuracy
from doitOneChunk import alignOneChunk


pathHMM = os.path.join(parentDir, 'HMMDuration')
from hmm.examples.main  import   loadSmallAudioFragment
# from hmm.examples.main  import loadSmallAudioFragmentOracle
from hmm.ParametersAlgo import ParametersAlgo



ANNOTATION_EXT = '.TextGrid'


def loadLyrics(URIrecordingNoExt, currSentence):
    
    withHTK = 0
    withSynthesis = 0
    lyricsWithModels, obsFeatures, URIrecordingChunk = loadSmallAudioFragment(currSentence, withHTK, URIrecordingNoExt, bool(withSynthesis), currSentence.beginTs, currSentence.endTs)
#     lyricsWithModels.printPhonemeNetwork()
    #         lyricsWithModels.printPhonemeNetwork()
    lyricsWithModels.printWordsAndStates()


def doitOneChunkAlign(URIrecordingNoExt, musicXMLParser, whichSentence, currSentence, withOracle, withDurations, withVocalPrediction, withRules, evalLevel ):
    '''
    align one chunk only.
    @param musicXMLParser: parsed  score for whole recording
    @param whichSentence: sentence number to process  
    '''
    
    
    deviation = str(ParametersAlgo.DEVIATION_IN_SEC)

    if (withDurations):
        tokenLevelAlignedSuffix = '.syllables_dur_gmm'
    else:
        if withOracle:
            tokenLevelAlignedSuffix = '.syllables_oracle'
        else:
            tokenLevelAlignedSuffix = '.syllables'
        
        if withRules:
            tokenLevelAlignedSuffix += '_rules'
    
    tokenLevelAlignedSuffix += '_' + deviation 
            
   

            
    if withDurations: # load from score instead
        lyrics = musicXMLParser.getLyricsForSection(whichSentence) # indexing in python
    else: lyrics = currSentence   
        
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
        for idx, syllableIdx in enumerate(range(currSentence.fromSyllableIdx, currSentence.toSyllableIdx+1)): # for each  syllable including silent syllables
            # go through the phonemes. load all 
            currSyllable = currSentence.listWords[idx].syllables[0]
            phonemesAnno, syllableTxt = loadPhonemesAnnoOneSyll(URIrecordingNoExt + ANNOTATION_EXT, syllableIdx, currSyllable)
            phonemesAnnoAll.extend(phonemesAnno)
         

    listNonVocalFragments = []
#     if withVocalPrediction:
#         listNonVocalFragments = getListNonVocalFragments(URIrecordingNoExt, fromTs, toTs)
    
    detectedTokenList, detectedPath = alignOneChunk( lyrics, withSynthesis, withOracle, phonemesAnnoAll, listNonVocalFragments, alpha, usePersistentFiles, tokenLevelAlignedSuffix, currSentence.beginTs, currSentence.endTs, URIrecordingNoExt)
    if detectedTokenList == None:
        return None, None, None, None
    correctDuration, totalDuration = _evalAccuracy(URIrecordingNoExt + ANNOTATION_EXT, detectedTokenList, evalLevel, currSentence.fromSyllableIdx, currSentence.toSyllableIdx  )
    acc = correctDuration / totalDuration
    print "result is: " + str(acc)
    
    return correctDuration, totalDuration, detectedTokenList, currSentence.beginTs

   
    

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

  