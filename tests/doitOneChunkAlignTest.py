# -*- coding: utf-8 -*-

'''
Created on Sep 23, 2015

@author: joro

'''
from doitOneChunkAlign import doitOneChunkAlign
import os
from lyricsParser import \
    divideIntoSentencesFromAnnoWithSil
from MusicXmlParser import MusicXMLParser

def readPinYinTest():
    URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/ariasAnnotated/2-16_伴奏：听兄言不由我花容惊变.TextGrid'
    allSentences = divideIntoSentencesFromAnnoWithSil(URIrecordingNoExt)
    print allSentences
    

def doitOneChunkTest():
    '''
    test
        '''
    URIrecordingNoExt = os.path.abspath('dan-xipi_01')
    
    URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/arias_dev_01_t_70/dan-xipi_02'
    URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/praat/yutangchun_yutangchun'
    URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/praat/xixiangji_biyuntian'

    URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/praat/wangjiangting_dushoukong'
    
    URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/praat/shiwenhui_tingxiongyan'
 
    lyricsTextGrid = URIrecordingNoExt + '.TextGrid'

    whichSentence = 1

    ###########################################################
         
    withDurations = 0
    musicXMLParser = None
#     musicXmlURI = URIrecordingNoExt + '_score.xml'
#     musicXMLParser = MusicXMLParser(musicXmlURI, lyricsTextGrid)
    
    
    listSentences = divideIntoSentencesFromAnnoWithSil(lyricsTextGrid) #uses TextGrid annotation to derive structure
    sentence = listSentences[whichSentence]
        
    withVocalPrediction = 0
    
    withOracle = 1
    currCorrectDuration, currTotalDuration = doitOneChunkAlign(URIrecordingNoExt, musicXMLParser, whichSentence, sentence, withOracle, withDurations, withVocalPrediction)  
 
    currAcc = currCorrectDuration / currTotalDuration
    print "sentence {}: acc ={:.2f}".format(whichSentence, currAcc)
     
if __name__ == '__main__':
#     readPinYinTest()
    doitOneChunkTest()
