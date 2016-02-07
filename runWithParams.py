'''
Created on Dec 5, 2014

@author: joro
'''
import logging
import sys
import numpy
from MusicXmlParser import MusicXMLParser
from hmm.ParametersAlgo import ParametersAlgo

from doitOneChunkAlign import doitOneChunkAlign
from lyricsParser import divideIntoSentencesFromAnnoWithSil
from runitHTK import runitHTK
from matplotlib.pyplot import legend

import matplotlib.pyplot as plt
from utilsLyrics.Utilz import getMeanAndStDev, tokenList2TabFile




def runWithParameters(argv):
    
    if len(argv) != 4:
            print ("Tool to get alignment accuracy of one jingju aria with different parameters ")
            print ("usage: {}   <URIRecording No Extension>  <deviation_INSeconds> withRules".format(argv[0]) )
            sys.exit()
    
    URIrecordingNoExt =  argv[1]
    lyricsTextGrid = URIrecordingNoExt + '.TextGrid'
    
   
    withRules = int(argv[3])
    correctDurationHTK = 0
    totalDurationHTK = 1
    accuracyListHTK = []
    correctDurationHTK, totalDurationHTK, accuracyListHTK = runitHTK(["dummy", URIrecordingNoExt ])       
    
    
    # load total # different sentences + their rspective ts
#         fromTss, toTss = loadSectionTimeStamps(sectionAnnoURI)
    listSentences = divideIntoSentencesFromAnnoWithSil(lyricsTextGrid, withRules) #uses TextGrid annotation to derive structure. TODO: instead of annotation, uses score
    
    ParametersAlgo.DEVIATION_IN_SEC = float(argv[2])
    musicXMLParser = None
        
    withDurations = 0

    if withDurations == 1:
        musicXmlURI = URIrecordingNoExt + '_score.xml'
        musicXMLParser = MusicXMLParser(musicXmlURI, lyricsTextGrid)
    

    
    correctDurationOracle = 0
    totalDurationOracle = 1
    accuracyListOracle = []
    
    
    correctDuration = 0
    totalDuration = 1
    accuracyList = []
    tokenListAlignedAll = []
    
    withVocalPrediction = 0
#     for whichSentence, currSentence in  reversed(list(enumerate(listSentences))):
    for whichSentence, currSentence in  enumerate(listSentences):
        
        currSentence.printSyllables()
        
        withOracle = 1
        correctDurationOracle, totalDurationOracle, dummy, dummy = doit(withOracle, withRules, URIrecordingNoExt, musicXMLParser, withDurations, correctDurationOracle, totalDurationOracle, accuracyListOracle, withVocalPrediction, whichSentence, currSentence)

        
            
        # calc local acc
        withOracle = 0
        correctDuration,  totalDuration,  tokenListAligned, sentenceBeginTs  = doit(withOracle, withRules, URIrecordingNoExt, musicXMLParser, withDurations, correctDuration, totalDuration, accuracyList, withVocalPrediction, whichSentence, currSentence)
        tokenListAlignedAll.extend(tokenListAligned)
          

    tokenAlignedfileName =  tokenList2TabFile(tokenListAlignedAll, URIrecordingNoExt, '.syllables_total')
    
    plotAccuracyList(accuracyListOracle, 'oracle', 'r')
    plotAccuracyList(accuracyList, 'DHMM', 'g')
    plotAccuracyList(accuracyListHTK, 'baseline', 'b')
    
    
    legend(loc=3, fontsize=12)
    plt.axvline(2.5)
    plt.axvline(7.5)
    plt.xlabel('lyrics lines', fontsize=12)
    plt.ylabel('overall accuracy', fontsize=12)

#     plt.show()
    
    
    return  correctDurationHTK, totalDurationHTK, correctDurationOracle, totalDurationOracle, correctDuration, totalDuration


def calcAccuracy(whichSentence, currCorrectDuration, currTotalDuration, correctDuration, totalDuration):
    
    '''
    helper calc correct duration 
    '''
    currAcc = currCorrectDuration / currTotalDuration
   
    print "sentence {}: acc ={:.2f}".format(whichSentence, currAcc)
    correctDuration += currCorrectDuration
    totalDuration += currTotalDuration
    
    return currAcc, correctDuration, totalDuration




def doit( withOracle, withRules, URIrecordingNoExt, musicXMLParser, withDurations, correctDuration, totalDuration, accuracyList, withVocalPrediction, whichSentence, currSentence):
   
    currCorrectDuration, currTotalDuration, detectedTokenList, sentenceBeginTs = doitOneChunkAlign(URIrecordingNoExt, musicXMLParser, whichSentence, currSentence, withOracle, withDurations, withVocalPrediction, withRules) # calc local accuracy
    currAcc, correctDuration, totalDuration = calcAccuracy(whichSentence, currCorrectDuration, currTotalDuration, correctDuration, totalDuration)
    accuracyList.append(currAcc)
    
    return correctDuration, totalDuration, detectedTokenList, sentenceBeginTs


def plotAccuracyList(accuracyList, labelText, colorText):
    
    point  = colorText + 'o' 
    plt.plot(accuracyList, point, label=labelText) # plot mean and st dev
    mean, stDev, median = getMeanAndStDev(accuracyList)
#     plt.errorbar(len(accuracyList) / 2.0, mean, stDev, ecolor=colorText, linestyle='None', marker='^')
    
      
  
  
    
if __name__ == '__main__':
    runWithParameters(sys.argv)
#     runWithParametersAll(sys.argv)


#     example: 
# python /Users/joro/Documents/Phd/UPF/voxforge/myScripts/JingjuAlignment/runWithParams.py /Users/joro/Documents/Phd/UPF/arias_dev_01_t_70/ 1 0.1 dan-xipi_01 0
# python /Users/joro/Documents/Phd/UPF/voxforge/myScripts/JingjuAlignment/runWithParams.py /Users/joro/Documents/Phd/UPF/arias_dev_01_t_70/ 1 0.1 laosheng-xipi_02 0

# python /Users/joro/Documents/Phd/UPF/voxforge/myScripts/JingjuAlignment/runWithParams.py /Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/praat/fold2/wangjiangting_dushoukong 2
# 

# output is printed on the console after each aria is done