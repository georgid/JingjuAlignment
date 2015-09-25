# -*- coding: utf-8 -*-

'''
Created on Sep 23, 2015

@author: joro

'''
from doitOneChunkAlign import doitOneChunkAlign
import os
from lyricsParser import divideIntoSentencesFromAnno

def readPinYinTest():
    URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/ariasAnnotated/2-16_伴奏：听兄言不由我花容惊变.TextGrid'
    allSentences = divideIntoSentencesFromAnno(URIrecordingNoExt)
    print allSentences
    

def doitOneChunkTest():
    '''
    meant to be run for withScores = 0
    '''
    URIrecordingNoExt = os.path.abspath('dan-xipi_01')
    URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/arias_dev_01_t_70/dan-xipi_02'
     
    lyricsTextGrid = URIrecordingNoExt + '.TextGrid'
    whichSentence = 0
         
    listSentences = divideIntoSentencesFromAnno(lyricsTextGrid) #uses TextGrid annotation to derive structure. TODO: instead of annotation, uses score
    musicXMLParser = 'dummy'
    sentence = listSentences[whichSentence]

#   meant to be run for withScores = 0
    withScores = 0
    withVocalPrediction = 0
    currCorrectDuration, currTotalDuration = doitOneChunkAlign(URIrecordingNoExt, musicXMLParser,  whichSentence, sentence, withScores, withVocalPrediction)  
 
    currAcc = currCorrectDuration / currTotalDuration
    print "sentence {}: acc ={:.2f}".format(whichSentence, currAcc)
     
if __name__ == '__main__':
#     readPinYinTest()
    doitOneChunkTest()
