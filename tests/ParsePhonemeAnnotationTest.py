'''
Created on Oct 1, 2015

@author: joro


'''
import os
import sys

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 

if parentDir not in sys.path:
    sys.path.append(parentDir)

dirUtilsLyrics = parentDir + 'utilsLyrics'
if parentDir + 'utilsLyrics' not in sys.path:
    sys.path.append(dirUtilsLyrics)
    
    
from ParsePhonemeAnnotation import     validatePhonemesOneSyll, tokenizePhonemes, validatePhonemesWholeAria
from lyricsParser import divideIntoSentencesFromAnnoWithSil


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
    
    
def validatePhonemesWholeAriaTest(argv):
    

    
    
    URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/praat/wangjiangting_dushoukong'
    lyricsTextGrid = URIrecordingNoExt + '.TextGrid'
    
    
#     validatePhonemesWholeAria(lyricsTextGrid)
    

##### automatic dir parsing:    
    path = '/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/praat/'
    from Utilz import findFilesByExtension
    
    lyricsTextGrids = findFilesByExtension(path, 'TextGrid')
    for lyricsTextGrid in lyricsTextGrids:
        print "working on " + lyricsTextGrid 
        validatePhonemesWholeAria(lyricsTextGrid)
    
     
     
      
#     if len(argv) != 2:
#             print ("Tool to check consistency of timestamps among annotation layers  ")
#             print ("usage: {}   <URI_textGrid> ".format(argv[0]) )
#             sys.exit()
#          
#     lyricsTextGrid = argv[1]
      

    
    
def tokenizePhonemesTest():
    phonemesSAMPA = [ u"r\\'i"]
    phonemesSAMPA = [ u'j',u"iu"]
    phonemesSAMPA = [ u"@r\\'"]
    
    phonemesSAMPAQueue = tokenizePhonemes(phonemesSAMPA)
    print phonemesSAMPAQueue
    
    
def  createDictSyll2XSAMPATest():
    dictSyll2XSAMPA = createDictSyll2XSAMPA()
    import json
    json.dump(dictSyll2XSAMPA, open("DictSyll2XSAMPA.txt",'w'), indent=4, sort_keys=True)
    syllableText = 'shang'
    phonemesDictSAMPA = dictSyll2XSAMPA[syllableText]
    print phonemesDictSAMPA
    
    
if __name__ == '__main__':
    
        
    validatePhonemesWholeAriaTest(sys.argv)
  
#     validatePhonemesOneSyllTest() 
#     createDictSyll2XSAMPATest()
#     tokenizePhonemesTest()

    