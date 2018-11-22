
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
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string
#from nltk.stem.porter import PorterStemmer
from nltk.stem import PorterStemmer
from gensim import corpora, models
import gensim
from pymongo import MongoClient
from HTMLParser import HTMLParser
import re
import csv
import TextCleaning
import matplotlib.pyplot as plt
import numpy as np
import re




inq = pickle.load(file('harvard_inquirer.pickle'))  # harvard emotions lookup
np = numpy
plt = pyplot
pd.set_option('display.height', 10000)
pd.set_option('display.max_rows', 10000)
pd.set_option('display.max_columns', 10000)
pd.set_option('display.width', 10000)


reload(sys)
sys.setdefaultencoding('utf8')
def prepeareLIWCPetitions():
    client = MongoClient('mongodb://localhost:27017/')
    collectionOpened = client.ClimateChange.PetitionNewOpen
    cursor = collectionOpened.find({}, no_cursor_timeout=True)
    with open('OpenedPetitionsNoStop.csv', 'wb') as csv_users:
        writer = csv.writer(csv_users)
        writer.writerow(['petition_id', 'title','description'])
        for dbp in cursor:
            '''
            strip = TextCleaning.strip_tags(dbp['title'].encode('UTF-8'))
            strip1 = strip + ". " + TextCleaning.strip_tags(dbp['overview']).encode('UTF-8')
            # strip = TextCleaning.strip_tags(dbp['title'].encode('UTF-8'))
            # strip =strip+". "+TextCleaning.strip_tags(dbp['overview'].encode('UTF-8'))
            # strip1 = u' '.join(strip).encode('utf-8').strip()
            strip1 = strip1.decode('utf-8', 'ignore').encode("utf-8")
            strip1 = re.sub(',', '.', strip1, flags=re.MULTILINE)
            strip1 = re.sub(r'^https?:\/\/.*[\r\n]*', '', strip1, flags=re.MULTILINE)
            strip1 = re.sub(r'^https?:\/\/.*[\r\n]*', '', strip1, flags=re.MULTILINE)
            tokens = word_tokenize(unicode(strip1, 'utf-8'))  # tokenize title

            # print len(tokens)
            psychFeatures = strip1.split('.')  # split title sentences

            words = [w.lower() for w in tokens]
            # Sorting the title vocabulary
            vocab = sorted(set(words))

            # We only want to work with lowercase for the comparisons
            scentence = dbp['title'].lower()

            # remove punctuation and split into seperate words
            wordsNoPucnt = re.findall(r'\w+', scentence, flags=re.UNICODE | re.LOCALE)
            important_words = []

            # Filter out non semantic words and puntuations
            important_words = [w for w in wordsNoPucnt if not w in stopwords.words('english')]
            '''
            title = re.sub(',', '.',dbp['title'])
            cleanDescription= re.sub(',', '.',dbp['cleanDescription'] , flags=re.MULTILINE)

            writer.writerow([dbp['petition_id'],title, cleanDescription])


def DBinsertLIWCEmotions():
    client = MongoClient('mongodb://localhost:27017/')
    collectionOpened = client.ClimateChange.PetitionNewOpen
    cursor = collectionOpened.find({}, no_cursor_timeout=True)
    import csv, sys
    filename = 'LIWC2015_OpenedPetitions.csv'
    header=[]
    with open(filename, 'rb') as f:
        reader = csv.reader(f)
        try:
            count=0
            for row in reader:
                if count==0:
                    for i in range(3,96):
                        header.append('LIWC_'+row[i])
                        if i==120:
                            print 'a'
                elif count>1:
                    post={}
                    for i in range(3, 96):
                        post[header[i-3]]=row[i]
                    try:
                        collectionOpened.update({'petition_id': int(row[0])}, {"$set": post}, upsert=False)
                    except Exception as e:
                        print 'error in iteration no : in updating the temp table for petition : ' + str(row[0])
                        print(e)
                count+=1
        except csv.Error as e:
            sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))




def getGIEmotions():
    client = MongoClient('mongodb://localhost:27017/')
    collectionOpened = client.ClimateChange.PetitionNewOpen
    counter = 0  # petitions counter
    allClassesT = []  # all classes for emotions in all petitions title
    allClassesO = []  # all classes for emotions in all petitions overview

    classesT = []  # all classes of emotions for each petition title
    classesO = []  # all classes of emotions for each petition overview

    exclude = set(string.punctuation)
    stop = set(stopwords.words('english'))
    lines = open("stop3").read().splitlines()
    for word in lines:
        print word
        stop.add(word)

    petitionsCount = collectionOpened.find({}).count()

    cursor = collectionOpened.find({}, no_cursor_timeout=True)

    # Sort ascending, the other application should run the function but sorted descending for faster data collection
    cursor.sort('petition_id', -1)
    count = 0
    doc_complete = []
    doc_clean = []
    allClasses={}
    allClasses = set()
    # Loop on users

    for dbp in cursor:
        count+=1
        l = len(dbp)
        # remove HTML tags
        strip = TextCleaning.strip_tags(dbp['title'].encode('UTF-8'))
        strip1=strip+". "+TextCleaning.strip_tags(dbp['overview']).encode('UTF-8')
        #strip = TextCleaning.strip_tags(dbp['title'].encode('UTF-8'))
        #strip =strip+". "+TextCleaning.strip_tags(dbp['overview'].encode('UTF-8'))
        #strip1 = u' '.join(strip).encode('utf-8').strip()
        print count
        strip1 = strip1.decode('utf-8', 'ignore').encode("utf-8")
        print strip1
        strip1 = re.sub(r'^https?:\/\/.*[\r\n]*', '', strip1, flags=re.MULTILINE)
        tokens = word_tokenize(unicode(strip1, 'utf-8'))  # tokenize title

        # print len(tokens)
        psychFeatures = strip1.split('.')  # split title sentences

        # calculate average len of narrative sentences in characters
        avg_len_sentences_chars = sum(len(x) for x in psychFeatures) / len(psychFeatures)

        # calculate average len of narrative sentences in words
        avg_len_sentences_words = sum(len(x.split()) for x in psychFeatures) / len(psychFeatures)



        words = [w.lower() for w in tokens]
        # Sorting the title vocabulary
        vocab = sorted(set(words))

        # We only want to work with lowercase for the comparisons
        descriptionLower = strip1.lower()

        # remove punctuation and split into seperate words
        wordsNoPucnt = re.findall(r'\w+', descriptionLower, flags=re.UNICODE | re.LOCALE)
        important_words = []


        # Filter out non semantic words and puntuations
        important_words = [w for w in wordsNoPucnt if not w in stopwords.words('english')]

        cleanDescription = ' '.join(important_words)
        post={}
        post["avg_len_sentences_chars"]=avg_len_sentences_chars
        post["avg_len_sentences_words"] = avg_len_sentences_words
        post["cleanDescription"] = cleanDescription
        collectionOpened.update({'petition_id': dbp["petition_id"]}, {"$set": post}, upsert=False)


        # check the semantic for tokens as adjective, verb or noun
        for word in important_words:
            adjectiveSet= inq[(word, 'jj')]  # check adjective, adverb
            nounSet= inq[(word, 'nn')]  # check noun
            verbSet= inq[(word, 'vb')]  # check verb
            if len(adjectiveSet)>0:
                for s in adjectiveSet:
                    if not s in allClasses:
                        allClasses.add(s)
            if len(nounSet)>0:
                for s in nounSet:
                    if not s in allClasses:
                        allClasses.add(s)
            if len(verbSet)>0:
                for s in verbSet:
                    if not s in allClasses:
                        allClasses.add(s)
    d = defaultdict(int)
    # add emotions exised in all petitions and initialize with 0
    for word in allClasses:
        d[word] = 0
        print word
        n = d[word]
        print d[word]
    counter = 0
    cursor = collectionOpened.find({}, no_cursor_timeout=True)
    for dbp in cursor:
        # reset GI classes score for each petition
        for k in d:
            d[k]=0
        important_words = dbp['cleanDescription'].split()
        # check sentiment and emotional classes
        for word in important_words:
            adjectiveSet= inq[(word, 'jj')]  # check adjective, adverb
            nounSet= inq[(word, 'nn')]  # check noun
            verbSet= inq[(word, 'vb')]  # check verb
            if len(adjectiveSet)>0:
                for s in adjectiveSet:
                    d[s]+=1
            if len(nounSet)>0:
                for s in nounSet:
                    d[s] += 1
            if len(verbSet)>0:
                for s in verbSet:
                    d[s] += 1
        post={}
        for k in d:
            post["GI_"+k]=d[k]
        collectionOpened.update({'petition_id': dbp["petition_id"]}, {"$set": post}, upsert=False)

        counter += 1

def main():
    #getGIEmotions()
    #prepeareLIWCPetitions()
    DBinsertLIWCEmotions()
    # victory 358, open 2,929, closed 1,457 = 4,744
    # open 2,929 - 373<100 words = 2556
if __name__ == '__main__':
    main()