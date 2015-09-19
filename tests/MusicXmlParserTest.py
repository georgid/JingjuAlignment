from MusicXmlParser import MusicXMLParser
import os
import sys

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 

pathHMMDuration = os.path.join(parentDir, 'AlignmentDuration')
if pathHMMDuration not in sys.path:
    sys.path.append(pathHMMDuration)


from Phonetizer import Phonetizer


if __name__=='__main__':
    
    MusicXmlURI = 'dan-xipi_01_score.xml'
    lyricsTextGrid = 'dan-xipi_01.TextGrid'
     
      
    MusicXmlURI = '/Users/joro/Documents/Phd/UPF/arias_dev_01_t_70/dan-xipi_02_score.xml'
    lyricsTextGrid = '/Users/joro/Documents/Phd/UPF/arias_dev_01_t_70/dan-xipi_02.TextGrid'

    musicXMLParser = MusicXMLParser(MusicXmlURI, lyricsTextGrid)
    
    Phonetizer.initLookupTable(True,  'phonemeMandarin2METUphonemeLookupTableSYNTH')

    for i in range(len(musicXMLParser.listSentences)):
        print i, " ",  musicXMLParser.getLyricsForSection(i)
    
#     for syll in musicXMLParser.listSyllables:
#         print syll    
