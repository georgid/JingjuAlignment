'''
Created on Feb 15, 2016

@author: joro
'''
from SentenceJingju import SentenceJingju
import os
import sys
from lyricsParser import createSyllable

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 
pathEvaluation = os.path.join(parentDir, 'AlignmentEvaluation')
if pathEvaluation not in sys.path:
    sys.path.append(pathEvaluation)
from AccuracyEvaluator import _evalAccuracy


pathHMMDuration = os.path.join(parentDir, 'AlignmentDuration')
if pathHMMDuration not in sys.path:
    sys.path.append(pathHMMDuration)
from doitOneChunk import alignOneChunk


ANNOTATION_EXT = '.TextGrid'
evalLevel = 3

def doitOneChunkAlignWithCsv(URIrecordingNoExt, scoreFilename):
    withOracle = 0
    withDurations = 1
    withVocalPrediction= 0  
    withRules = 0
    withSynthesis = 0
    
   
    currSectionSyllables, bpm = csvDurationScoreParser(scoreFilename)
    
    
    banshiType = 'none'
    sentence = SentenceJingju(currSectionSyllables,  0, 5, 0, len(currSectionSyllables), banshiType, withRules)

    alpha = 0.97
    detectedTokenList, detectedPath = alignOneChunk( sentence, withSynthesis, withOracle, [], [], alpha,  False, '.syllRong', 0, 5, URIrecordingNoExt)
     
    correctDuration, totalDuration = _evalAccuracy(URIrecordingNoExt + ANNOTATION_EXT, detectedTokenList, evalLevel, sentence.fromSyllableIdx, sentence.toSyllableIdx  )
    acc = correctDuration / totalDuration
    print "result is: " + str(acc)
    
    return correctDuration, totalDuration, detectedTokenList, sentence.beginTs
    

def csvDurationScoreParser(scoreFilename):
    '''
    author Rong Gong
    '''
    import csv

    syllable_durations = []
    bpm                 = []
    currSentenceSyllablesLIst = []
    
    with open(scoreFilename, 'rb') as csvfile:
        score = csv.reader(csvfile)
        for idx, row in enumerate(score):
            if idx == 0:
                syllableTexts = row
            else:
                syllableDurs = row
        for sylMandarinChar, sylDur in zip(syllableTexts[1:],syllableDurs[1:]):
            pinyin = sylMandarinChar
            # pinyin = mandarinToPinyin(sylMandarinChar)
            currSentenceSyllablesLIst = createSyllable(currSentenceSyllablesLIst, pinyin, float(sylDur))
            
           
    bpm = syllableDurs[0]
                
    return currSentenceSyllablesLIst, bpm 



if __name__ == '__main__':
    scoreFilename = '/Users/joro//Downloads/fold1/neg_1_1_pinyin.csv'
    URIrecordingNoExt = '/Users/joro//Downloads/fold1/neg_1_1'
    
#     URIrecordingNoExt = sys.argv[1]
#     scoreFilename = sys.argv[2]
#     
    doitOneChunkAlignWithCsv(URIrecordingNoExt, scoreFilename)