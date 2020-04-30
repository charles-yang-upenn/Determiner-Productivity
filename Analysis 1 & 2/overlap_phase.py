#!/usr/bin/python
import sys
import os
import glob
import re
import string
import fileinput
import difflib
import random
import math


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


def Harmonic(n):
    s=0
    for i in range(1, n+1):
        s+=1.0/i
    return s

def expected_overlap(N, S, r, b):
    hN = Harmonic(N)
    p = 1.0/(r*hN)
    eo = 1 - sum( [ math.pow((p*di+1.0-p), S) for di in [b, 1.0-b] ] ) + math.pow(1-p, S)
    assert eo>0, '%d, %.6f'%(r, eo)
    return eo

def average_expected_overlap(N, S, b):
    sumo = 0
    for r in range(1, N+1):
        sumo += expected_overlap(N, S, r, b)
    return sumo/N


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
            timestamp = name[:len(name)-5]
            break

    # data for the phase, from start to the end of the timestamp, pad longlist as well
    # ppp is the child data from start to the end of the timestamp
    ppp = []
    for i in range(start, len(longlist)):
        ppp.append(data[i])
    for i in range(len(longlist), len(data)):
        if data[i].split()[2].startswith(timestamp):
            longlist.append(data[i])
            ppp.append(data[i])

    for i in range(0, len(ppp)):  # select eligible--chi counts must be in ppp
        nnn = ppp[i].split()[1]
        if  nnn in masterlist and freqcounts(nnn, ppp) >=2 and freqcounts(nnn, mother)>=2:
            childsample.append(ppp[i])
#            print "c-in-phase-mot--cS--mS", freqcounts(nnn, ppp), freqcounts(nnn, mother), len(longlist)-start, len(mother)

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

def count_overlap(w, data):
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

def draw_match(big, small, word, data):
    # small is strictly smaller than big
    
    a = 0
    the = 0
    for i in range(small):
        ind = random.randint(1, big)
        for j in range(0, len(data)):
            if data[j].split()[1]==word and ccc == ind:
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

    uniqw = []
    for i in range(0, len(chi)):
        nnn = chi[i].split()[1]
        if nnn not in uniqw:
            uniqw.append(nnn)

    overlap_c = 0.0
    overlap_m = 0.0

    sample_size = 0

    for i in range(0, len(uniqw)):
        nnn = uniqw[i]
        motc = freqcounts(nnn, mot)
        chic = freqcounts(nnn, chi)


        if motc >= chic:
            sample_size += chic
        else:
            sample_size += motc

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

def find_bias(data):

    uniqw = []
    for i in range(0, len(data)):
        nnn = data[i].split()[1]
        if nnn not in uniqw:
            uniqw.append(nnn)


    big = 0
    small = 0
    for i in range(0, len(uniqw)):
        a = 0
        the = 0
        for j in range(0, len(data)):
            if uniqw[i] == data[j].split()[1]:
                if data[j].split()[0] == 'a':
                    a += 1
                else:
                    the +=1
        if a >= the:
            big += a
            small += the
        else:
            big += the
            small += a
    return float(big)/float(big+small)
    
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


   
    start = 0
    for p in range(1, 2): #check pred vs. emp in phase one

        cutoff = 50*p

        longlist, childsample = phase(chidata, motdata, masterlist, cutoff, start)
        # childsample is a subset of longlist that meets the selection req.

        phasesample = []
        for i in range(start, len(longlist)):
            phasesample.append(longlist[i])
            
        start = len(longlist) #for beginning of next phase

        tmp = calculate_overlap(phasesample)
        S = int(tmp[0])
        N = int(tmp[1])
        O = int(tmp[2])
        bias = find_bias(phasesample)

        print kid, p, N, S, ("%.3f" % bias), ("%.3f" % (float(S)/float(N))),  ("%.3f" % (float(O)/float(N))), ("%.3f" % average_expected_overlap(N, S, bias))

    

        

    
if __name__ == "__main__":
    main()    
            

    
