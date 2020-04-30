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


def getfreqsample(data, f): # get a list from data where the word frequency is f

    uniqw = []
    for i in range(0, len(data)):
        nnn = data[i].split()[1]
        if nnn not in uniqw:
            uniqw.append(nnn)

    fsample = []
    for i in range(0, len(uniqw)):
        freqc = freqcounts(uniqw[i], data)
        if freqc == f:
            for j in range(0, len(data)):
                if data[j].split()[1]==uniqw[i]:
                    fsample.append(data[j])
    return fsample

def getfreqsampleatleast(data, f): # get a list from data where the word freq is at least f

    uniqw = []
    for i in range(0, len(data)):
        nnn = data[i].split()[1]
        if nnn not in uniqw:
            uniqw.append(nnn)

    fsample = []
    for i in range(0, len(uniqw)):
        freqc = freqcounts(uniqw[i], data)
        if freqc >= f:
            for j in range(0, len(data)):
                if data[j].split()[1]==uniqw[i]:
                    fsample.append(data[j])
    return fsample

    

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





    
    kid = sys.argv[1][:-4]
    motdata = readindata(sys.argv[1], "*MOT:")

    print kid+"+mot",
    for freq in range(1, 8):
        fsample=getfreqsample(motdata, freq)
        tmp = calculate_overlap(fsample)
        print ("%.3f" % (float(tmp[2])/float(tmp[1]))),

    fsample=getfreqsampleatleast(motdata, 8)
    tmp = calculate_overlap(fsample)
    print ("%.3f" % (float(tmp[2])/float(tmp[1]))),
    
    
    chidata = readindata(sys.argv[1], "*CHI:")

    print kid, 
    for freq in range(1, 8):
        fsample=getfreqsample(chidata, freq)
        tmp = calculate_overlap(fsample)
        print ("%.3f" % (float(tmp[2])/float(tmp[1]))),

    fsample=getfreqsampleatleast(chidata, 8)
    tmp = calculate_overlap(fsample)
    print ("%.3f" % (float(tmp[2])/float(tmp[1]))),

 
    
    

        

    
if __name__ == "__main__":
    main()    
            

    
