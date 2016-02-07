'''
Created on Dec 3, 2015

@author: joro
'''
import sys
import os
from runWithParams import runWithParameters

def runWithParametersAll(argv):
    
    if len(argv) != 4:
            print ("Tool to get alignment accuracy of of one jingju aria with different parameters ")
            print ("usage: {}    <deviation_INSeconds> <withRules> <withVocalPrediciton> ".format(argv[0]) )
            sys.exit()

    path = '/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/praat/'
    path = '/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/praat_rules/'

    from utilsLyrics.Utilz import findFilesByExtension
    
    correctDurationHTK = 0
    totalDurationHTK = 0
    
    correctDurationOracle = 0
    totalDurationOracle = 0
    
    correctDuration = 0
    totalDuration = 0
    
    folds = ['fold1/', 'fold2/', 'fold3/']            
    for fold_ in folds:
    
        URiREcordings = findFilesByExtension(path + fold_, 'wav')
        if len(URiREcordings) == 0:
            sys.exit("path {} has no wav recordings".format(path))
        for URiREcording in URiREcordings:
            URiREcording = os.path.splitext(URiREcording)[0] 
            print "working on " + URiREcording
            
            a, b, c, d, e, f = runWithParameters( ["dummy", URiREcording,  argv[1], argv[2]] )
            
            correctDurationHTK += a 
            totalDurationHTK += b
            
            correctDurationOracle += c
            totalDurationOracle += d
            
            correctDuration += e
            totalDuration += f
            
                
    # end of loop
    print "final HTK: {:.2f}".format(correctDurationHTK / totalDurationHTK * 100)
    print "final Oracle: {:.2f}".format( correctDurationOracle / totalDurationOracle * 100) 
    print "final xampa: {:.2f}".format( correctDuration / totalDuration * 100) 


if __name__ == '__main__':
    runWithParametersAll(sys.argv)
    
#     python /Users/joro/Documents/Phd/UPF/voxforge/myScripts/JingjuAlignment/runWithParamsAll.py  0 2 0