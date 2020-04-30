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
                if (words[i] == "det:art|a" or words[i] == "det:art|an" or words[i] == "det:art|the"
) and (words[i+1].startswith("n|") and  words[i+1].find("PL") == -1) and not (words[i+2].startswith(
"n|") and words[i+2].find("PL") == -1):
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

def freqcounts(word, data):

    ccc = 0
    for i in range(0, len(data)):
        if word == data[i].split()[1]:
            ccc += 1
    return ccc

def uniqwords(data):

    ccc = 0
    uniqw = []
    for i in range(0, len(data)):
        nnn = data[i].split()[1]
        if nnn not in uniqw:
            uniqw.append(nnn)
            ccc += 1
    return ccc

def phase(data, mother, masterlist, cutoff, start):

    childsample = []
    longlist = []
    uniqw = []

    for i in range(0, len(data)): # check pairs for unique counts
        longlist.append(data[i])
        nnn = data[i].split()[0]+" "+data[i].split()[1]
        if nnn not in uniqw: 
            uniqw.append(nnn)
        if len(uniqw) == cutoff:
            name = data[i].split()[2]
            timestamp = name[:len(name)-5] # pull the prefix of the file (date): phase ends that way
            break

    # data for the phase, from start to the end of the timestamp, pad longlist as well
    # ppp is the child data from start to the end of the timestamp (Pine 8-19-2018)
    ppp = []
    for i in range(start, len(longlist)):
        ppp.append(data[i])
    for i in range(len(longlist), len(data)):
        if data[i].split()[2].startswith(timestamp):
            longlist.append(data[i])
            ppp.append(data[i])

    for i in range(0, len(ppp)):  # select eligible--chi counts must be in ppp
        nnn = ppp[i].split()[1]
        if   freqcounts(nnn, ppp) >=1 and freqcounts(nnn, mother)>=1: #dropping masterlist
            childsample.append(ppp[i])

    return longlist, childsample

    

def calculate_overlap(data):
    result = []
    result.append(len(data))
    
    uniqnoun = []
    for i in range(0, len(data)):
        nnn = data[i].split()[1]
        if nnn not in uniqnoun:
            uniqnoun.append(nnn)
    result.append(len(uniqnoun))
    
    both = 0
    for i in range(0, len(uniqnoun)):
        a = 0
        the = 0
        for j in range(0, len(data)):
            if uniqnoun[i] == data[j].split()[1]:
                if data[j].split()[0] == 'a':
                    a = 1
                if data[j].split()[0] == 'the':
                    the = 1
        if a == 1 and the == 1:
            both += 1

    result.append(both)

    return result

def count_overlap(w, data):  # use in the sample scheme: the overlap score for w in the list "data"
    a = 0
    the = 0
    for i in range(0, len(data)):
        if data[i].split()[1] == w:
            if data[i].split()[0] == "a":
                a = 1
            if data[i].split()[0] == "the":
                the = 1
                
    if a*the == 1:
        return 1.0
    else:
        return 0.0

def draw_match(big, small, word, data): #sample scheme to match the # in small with the # in large
    
    # small is strictly smaller than big
    
    a = 0
    the = 0
    for i in range(small):
        ind = random.randint(1, big)
        ccc = 0
        for j in range(0, len(data)):
            if data[j].split()[1]==word:
                ccc += 1
                if ccc == ind:
                    if data[j].split()[0] == 'a':
                        a = 1
                    if data[j].split()[0] == 'the':
                        the = 1
    if a == 1 and the == 1:
        ret = 1.0
    else:
        ret = 0.0
    return ret
    
    
def control(chi, mot):

    # uniq words in child data 
    uniqw = []
    for i in range(0, len(chi)):
        nnn = chi[i].split()[1]
        if nnn not in uniqw:
            uniqw.append(nnn)

    overlap_c = 0.0
    overlap_m = 0.0

    sample_size = 0  # token frequency used in the controlled sample

    for i in range(0, len(uniqw)):  # for each unique word in child sample
        nnn = uniqw[i]
        motc = freqcounts(nnn, mot)
        chic = freqcounts(nnn, chi)


        if motc >= chic:
            sample_size += chic
        else:
            sample_size += motc  #always match the small

        if motc == chic:  # mot and chi counts equal
            overlap_c += count_overlap(nnn, chi)
            overlap_m += count_overlap(nnn, mot)

        if motc > chic: # mot more frequent than chi
            overlap_c += count_overlap(nnn, chi)
            overlap_m += draw_match(motc, chic, nnn,  mot)

        if chic > motc: #chi more freq than mot
            overlap_m += count_overlap(nnn, mot)
            overlap_c += draw_match(chic, motc, nnn, chi)
            
    return len(uniqw), sample_size, overlap_c/float(len(uniqw)), overlap_m/float(len(uniqw))

def findbias(words, data):

    big = 0.0
    small = 0.0
    for i in range(0, len(words)):
        thec = 0.0
        ac = 0.0
        for j in range(0, len(data)):
            if data[j].split()[1] == words[i]:
                if data[j].split()[0] == 'the':
                    thec += 1.0
                else:
                    ac += 1.0
        big += (thec if thec>=ac else ac)/(thec+ac)
        small += (thec if thec<ac else ac)/(thec+ac)
        
    return big/(big+small)
            

    
def main():

    random.seed()
    
    masterlist = []
    fp = open('masterlist.txt', 'U')
    for line in fp:
        masterlist.append(line.split()[0])
    fp.close()

    kid = sys.argv[1][:-4]
    motdata = readindata(sys.argv[1], "*MOT:")
    chidata = readindata(sys.argv[1], "*CHI:")

    
    uniqw = []
    data = chidata
    
    for i in range(0, len(data)):
        nnn = data[i].split()[1]
        if nnn not in uniqw:
            uniqw.append(nnn)

    count = 1
    mostw = ""
    for i in range(0, len(uniqw)):
        c = freqcounts(uniqw[i], data)
        if c > count:
            count = c
            mostw = uniqw[i]

    mostws = []
    mostws.append(mostw)
    mostlist = []
    for i in range(0, len(data)):
        if data[i].split()[1] == mostw:
            mostlist.append(data[i])



    print kid, mostw, count, 
    ball = findbias(mostws, mostlist)
    for i in range(0, 5):
        chunk = len(mostlist)/5
        tmplist = mostlist[i*chunk:(i+1)*chunk]
        b = findbias(mostws, tmplist)
        print ("%.2f" % b), 
    print ("%.2f" % ball)
        
                                 
                
                       

    


            

    
if __name__ == "__main__":
    main()    
            

    
