#!/usr/bin/python
import sys
import os
import glob
import re
import string
import fileinput
import difflib
import random

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

def phase(data, masterlist, cutoff):

    childsample = []
    for i in range(0, len(data)):
        nnn = data[i].split()[1]
        if nnn in masterlist and freqcounts(nnn, data)>=2:
            childsample.append(data[i])

    if uniqwords(childsample) < cutoff:
        childsample = []
    return childsample


def build_mothersample(chi, mot):

    childn = []
    for i in range(0, len(chi)):
        nnn = chi[i].split()[1]
        if nnn not in childn:
            childn.append(nnn)

    motsample = []
    for i in range(0, len(childn)):
        chinc = freqcounts(childn[i], chi)
        motnc = freqcounts(childn[i], mot)
        print(chinc, motnc)

        for j in range(chinc):
            ind = random.randint(1, motnc)
            ccc = 0
            for k in range(0, len(mot)):
                if mot[k].split()[1] == childn[i]:
                    ccc +=1
                if ccc == ind:
                    motsample.append(mot[k])
    return motsample
    

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

def marker(l):
    w1 = l.split()[0]
    return w1.startswith('@') or w1.startswith('%') or w1.startswith('*')
def main():

        
    motdata = []
    fp = open(sys.argv[1], 'U')
    seen = 0
    line = []
    for l in fp:
        line.append(l.replace("\n", " "))

    fp.close()


    fp = open(sys.argv[1], 'w')
    for i in range(0, len(line)-1):
        if marker(line[i]):
            fp.write(line[i],)
        if not marker(line[i+1]):
            fp.write(" "+line[i+1]+'\n')
            i +=1
        else:
            fp.write('\n')


            
        


    
if __name__ == "__main__":
    main()    
            

    
