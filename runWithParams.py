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
from lyricsParser import divideIntoSentencesFromAnno




def runWithParameters(argv):
    
    if len(argv) != 6:
            print ("Tool to get alignment accuracy of of one jingju aria with different parameters ")
            print ("usage: {}   <pathToRecordings> <withScores> <deviation_INSeconds> <recordingName_noExtension> <withVocalPrediciton> ".format(argv[0]) )
            sys.exit()
    
    rootURI = argv[1]
#     rootURI = '/Users/joro/Documents/Phd/UPF/arias/'
    
#     URIrecordingNoExt =  rootURI + 'laosheng-erhuang_04'
#     URIrecordingNoExt =  rootURI + 'laosheng-xipi_02'
#     URIrecordingNoExt =  rootURI + 'dan-xipi_01'
#     URIrecordingNoExt =  rootURI + 'dan-xipi_02'

    URIrecordingNoExt = rootURI + argv[4]
    lyricsTextGrid = URIrecordingNoExt + '.TextGrid'

    # load total # different sentences + their rspective ts
#         fromTss, toTss = loadSectionTimeStamps(sectionAnnoURI)
    listSentences = divideIntoSentencesFromAnno(lyricsTextGrid) #uses TextGrid annotation to derive structure. TODO: instead of annotation, uses score
    
    withScores  = int(argv[2])
    ParametersAlgo.DEVIATION_IN_SEC = float(argv[3])
    musicXMLParser = None
    
    if withScores:
        musicXmlURI = URIrecordingNoExt + '_score.xml'
        musicXMLParser = MusicXMLParser(musicXmlURI, lyricsTextGrid)
    
    correctDuration = 0
    totalDuration = 0
    accuracyList = []
    
    withVocalPrediction = int(argv[5])
    withOracle = 0
#     for whichSentence, currSentence in  reversed(list(enumerate(listSentences))):
    for whichSentence, currSentence in  enumerate(listSentences):
        currCorrectDuration, currTotalDuration = doitOneChunkAlign(URIrecordingNoExt, musicXMLParser,  whichSentence, currSentence, withOracle, withScores, withVocalPrediction)  
        
        currAcc = currCorrectDuration / currTotalDuration
        accuracyList.append(currAcc)
        print "sentence {}: acc ={:.2f}".format(whichSentence, currAcc)
        
        correctDuration += currCorrectDuration
        totalDuration += currTotalDuration

##### TRICK: take only first three sentences:
#         if whichSentence == 2:
#             break
    print "final: {:.2f}".format(correctDuration / totalDuration * 100)     
    import matplotlib.pyplot as plt
    plt.plot(accuracyList, 'ro')
    plt.show()  
    
if __name__ == '__main__':
    runWithParameters(sys.argv)

#     example: 
# python /Users/joro/Documents/Phd/UPF/voxforge/myScripts/JingjuAlignment/runWithParams.py /Users/joro/Documents/Phd/UPF/arias_dev_01_t_70/ 1 0.1 dan-xipi_01 0
# python /Users/joro/Documents/Phd/UPF/voxforge/myScripts/JingjuAlignment/runWithParams.py /Users/joro/Documents/Phd/UPF/arias_dev_01_t_70/ 1 0.1 laosheng-xipi_02 0

# output is printed on the console after each aria is done