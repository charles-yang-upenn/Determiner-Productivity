#!/usr/bin/python
import sys
import os
import glob
import re
import string
import fileinput
import difflib
import random



def readindata(filen, key):
    # read in file. look for line containing key
    # and extract the next line (%mor) that contains D-N data
    # N is tagged as 'n' and not PL
    # extract DN in D-N-x if X is not N
    # extract DN in D-x-N (Pine 8-19-2018)
    # last clause deadling with utterance final adjacent D-N

    data = []

    fp = open(filen, 'U')
    seen = 0
    for line in fp:
        if key in line:
            seen = 1
        if "%mor:" in line and seen == 1:
            words = line.split()
            fn = words[0]
            
            for i in range(0, len(words)-2): # find D Ns X, where X is not Ns
                if (words[i] == "det:art|a" or words[i] == "det:art|an" or words[i] == "det:art|the") and (words[i+1].startswith("n|") and  words[i+1].find("PL") == -1) and not (words[i+2].startswith("n|") and words[i+2].find("PL") == -1):
                    if words[i] == "det:art|a" or words[i] == "det:art|an":
                        data.append(('a '+words[i+1][2:]+' '+fn))
                    else:
                        if words[i] == "det:art|the":
                            data.append(('the '+words[i+1][2:]+' '+fn))
                            
            for j in range(0, len(words)-2): # for D X Ns, extract the second N (Pine 8-19-2018)
                if (words[j] == "det:art|a" or words[j] == "det:art|an" or words[j] == "det:art|the") and (words[j+2].startswith("n|") and  words[j+2].find("PL") == -1):
                    if words[j] == "det:art|a" or words[j] == "det:art|an":
                        data.append(('a '+words[j+2][2:]+' '+fn))
                    else:
                        if words[j] == "det:art|the":
                            data.append(('the '+words[j+2][2:]+' '+fn))

             # only the last two words
            i = len(words)-2
            if (words[i] == "det:art|a" or words[i] == "det:art|an" or words[i] == "det:art|the") and (words[i+1].startswith("n|") and  words[i+1].find("PL") == -1):  
                if words[i] == "det:art|a" or words[i] == "det:art|an":
                    data.append(('a '+words[i+1][2:]+' '+fn))
                else:
                    if words[i] == "det:art|the":
                        data.append(('the '+words[i+1][2:]+' '+fn))
             
            seen = 0
    fp.close()

    return data


    
def main():

        
    motdata = readindata(sys.argv[1], sys.argv[2])


    uniqn = []
    for i in range(0, len(motdata)):
        if motdata[i].split()[1] not in uniqn:
            uniqn.append(motdata[i].split()[1])

    for i in range(0, len(uniqn)):
        a = 0
        the = 0
        for j in range(0, len(motdata)):
            if motdata[j].split()[1] == uniqn[i]:
                if motdata[j].split()[0] == 'a':
                    a = 1
                else:
                    the = 1
        if a == 1 and the == 1:
            print uniqn[i]
            
        


    
if __name__ == "__main__":
    main()    
            

    
