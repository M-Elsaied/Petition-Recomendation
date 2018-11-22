
"""
Created on Nov-Dec 2014

@author: ahmed

getting the emotion matrix for all petitions content fields (Title)
"""

import pandas as pd
import pylab
import nltk
from pandas import *
from pylab import *
from nltk.book import *
import numpy
import matplotlib
import math
from matplotlib import pylab, mlab, pyplot
from datetime import datetime
import re
from collections import Counter
import nltk, re, pprint
from nltk import word_tokenize
import pickle
from collections import defaultdict
import csv
from nltk.corpus import stopwords
from IPython.core.pylabtools import figsize, getfigs
from pymongo import MongoClient


inq = pickle.load(file('harvard_inquirer.pickle'))  # harvard emotions lookup
np = numpy
plt = pyplot
pd.set_option('display.height', 10000)
pd.set_option('display.max_rows', 10000)
pd.set_option('display.max_columns', 10000)
pd.set_option('display.width', 10000)

counter = 0  # petitions counter
allClassesT = []  # all classes for emotions in all petitions title
allClassesO = []  # all classes for emotions in all petitions overview

classesT = []  # all classes of emotions for each petition title
classesO = []  # all classes of emotions for each petition overview

# initialize the petitions titles emotions to be empty for the 899 petition
for i in range(899):
    classesT.append([])  # reset the emotions list for each petition title
    classesO.append([])  # reset the emotions list for each petition overview



# open the petitions CSV
with open('C:/Anaconda/datasets/petitionPandas.csv') as csvfile:
    petitions = csv.DictReader(csvfile)
    for row in petitions:
        tokensT = word_tokenize(row['TITLE'])  # tokenize title
        tokensO = word_tokenize(row['OVERVIEW'])  # tokenize overview
        # print len(tokens)
        sentsT = row['TITLE'].split('.')  # split title sentences
        sentsO = row['OVERVIEW'].split('.')  # split overview sentences
        # calculate average len of Title sentences in characters
        avg_len_sentences_charsT = sum(len(x) for x in sentsT) / len(sentsT)
        # calculate average len of Overview sentences in characters
        avg_len_sentences_charsO = sum(len(x) for x in sentsO) / len(sentsO)

        # calculate average len of title sentences in words
        avg_len_sentences_wordsT = sum(len(x.split()) for x in sentsT) / len(sentsT)
        # calculate average len of overview sentences in words
        avg_len_sentences_wordsO = sum(len(x.split()) for x in sentsO) / len(sentsO)
        # calculate average len of Title words in characters
        avg_len_wordsT = sum(len(x) for x in sentsT) / len(tokensT)
        # calculate average len of Overview words in characters
        avg_len_wordsO = sum(len(x) for x in sentsO) / len(tokensO)

        wordsT = [w.lower() for w in tokensT]
        # Sorting the title vocabulary
        vocabT = sorted(set(wordsT))

        wordsO = [w.lower() for w in tokensO]
        # Sorting the overview vocabulary
        vocabO = sorted(set(wordsO))

        # We only want to work with lowercase for the comparisons
        scentenceT = row['TITLE'].lower()

        # remove punctuation and split into seperate words
        wordsT = re.findall(r'\w+', scentence, flags=re.UNICODE | re.LOCALE)
        important_wordsT = []

        # Filter out non semantic words and puntuations
        important_wordsT = [w for w in wordsT if not w in stopwords.words('english')]

        # check the semantic for tokens as adjective, verb or noun
        for wordT in important_wordsT:
            allClasses += inq[(wordT, 'jj')]  # check adjective, adverb
            allClasses += inq[(wordT, 'nn')]  # check noun
            allClasses += inq[(wordT, 'vb')]  # check verb
            print inq[(wordT, 'jj')]
            print inq[(wordT, 'nn')]
            print inq[(wordT, 'vb')]
            # increment the counter and get the next petition
        counter += 1
        # for i in range(len(ed)):
counter = 0
# write the titles vs emotions classes matrix in PetitionTitle CSV and PetitionOverview csv
file = open("C:/Career/DSU/GA/PetitionTitle.csv", "w")
file = open("C:/Career/DSU/GA/PetitionOverview.csv", "w")
# Adding the header for the petition info and emotions classes that where detected in any petition
fieldnamesT = 'PETITION_ID' + ',TITLE' + ','
fieldnamesO = 'PETITION_ID' + ',OVERVIEW' + ','
td = defaultdict(int)
od = defaultdict(int)
# cluster all Title repitions of emotions class in one entry in dictionary
for wordT in allClasses:
    td[wordT] += 1
# cluster all Overview repitions of emotions class in one entry in dictionary
for wordT in allClasses:
    td[wordT] += 1
# Add all existing emotion classes to the header of the CSV
for i in td:
    fieldnames = fieldnames + i + ','
# write all fields and exclude the extra comma
file.write(fieldnames[:len(fieldnames) - 1])
file.write("\n")

# open a DB connnection with the petitions table to retrieve petitions
db = MySQLdb.connect(host="localhost",  # your host, usually localhost
                     user="root",  # your username
                     passwd="",  # your password
                     db="temp_db",  # name of the data base
                     charset="utf8"  # encoding
                     )
cur = db.cursor()
cur.execute("SELECT * FROM temp_db.noDupPetition")
# iterate through petitions and add ID and title
for row in cur.fetchall():
    rowStr = ''
    rowStr = row[2] + ',' + row[3] + ','
    scentence = row[3].lower()

    # remove punctuation and split into seperate words
    words = re.findall(r'\w+', scentence, flags=re.UNICODE | re.LOCALE)
    important_words = []
    # filter the semantic words only in the title tokens
    for word in words:
        if word not in stopwords.words('english'):
            important_words.append(word)
            # check sentiment and emotional classes
    for word in important_words:
        classes[counter] += inq[(word, 'jj')]  # check adjective, adverb
        classes[counter] += inq[(word, 'nn')]  # check noun
        classes[counter] += inq[(word, 'vb')]  # check verb
    # check the count of emotional classes for the important word in the petition field
    d = defaultdict(int)
    # add emotions exised in all petitions and initialize with 0
    for word in allClasses:
        d[word] = 0
        print word
        n = d[word]
        print d[word]

    # add emotions exised in current petition with the number of occurence of words with this semantic
    for word in classes[counter]:
        d[word] += 1
        print word
        n = d[word]
        print d[word]
    # add the row to the CSV except the comma in the end
    for i in d:
        rowStr = rowStr + str(d[i]) + ','
    file.write(rowStr[:len(rowStr) - 1])
    file.write("\n")
    counter += 1
file.close()

