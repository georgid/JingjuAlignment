'''
Created on Oct 1, 2015

@author: joro


'''
import os
import sys

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 

if parentDir not in sys.path:
    sys.path.append(parentDir)
    
    
from ParsePhonemeAnnotation import createDictSyll2XSAMPA,\
    validatePhonemesOneSyll, tokenizePhonemes, validatePhonemesWholeAria
from lyricsParser import divideIntoSentencesFromAnnoWithSil
import sys


def validatePhonemesOneSyllTest():
    '''
    test parsing of one syll by its syl idx
    '''
    URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/arias_dev_01_t_70/dan-xipi_02'
    lyricsTextGrid = URIrecordingNoExt + '.TextGrid'
    # TextGrid-1
    syllableIdx = 107

    dictSyll2XSAMPA = createDictSyll2XSAMPA()
    validatePhonemesOneSyll(lyricsTextGrid, syllableIdx, dictSyll2XSAMPA)
    
    
def parseWholeAriaTextGridTest(argv):
    
    URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/ariasAnnotated/yutangchun_yutangchun'
    URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/ariasAnnotated//xixiangji_biyuntian'
#     URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/ariasAnnotated/shiwenhui_tingxiongyan'
    lyricsTextGrid = URIrecordingNoExt + '.TextGrid'
    
     
    if len(argv) != 2:
            print ("Tool to check consistency of timestamps among annotation layers  ")
            print ("usage: {}   <URI_textGrid> ".format(argv[0]) )
            sys.exit()
      
    lyricsTextGrid = argv[1]
     
    validatePhonemesWholeAria(lyricsTextGrid)

    
    
def tokenizePhonemesTest():
    phonemesSAMPA = [ u"r\\'i"]
    phonemesSAMPA = [ u'j',u"iu"]
    phonemesSAMPA = [ u"@r\\'"]
    
    phonemesSAMPAQueue = tokenizePhonemes(phonemesSAMPA)
    print phonemesSAMPAQueue
    
    
def  createDictSyll2XSAMPATest():
    dictSyll2XSAMPA = createDictSyll2XSAMPA()
    syllableText = 'shang'
    phonemesDictSAMPA = dictSyll2XSAMPA[syllableText]
    print phonemesDictSAMPA
    
    
if __name__ == '__main__':
    
        
    parseWholeAriaTextGridTest(sys.argv)
  
#     validatePhonemesOneSyllTest() 
#     createDictSyll2XSAMPATest()
#     tokenizePhonemesTest()

    