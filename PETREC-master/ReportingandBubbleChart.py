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
import sys
import matplotlib.pyplot as plt
import numpy as np
import nltk
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
reload(sys)
sys.setdefaultencoding('utf8')
import enchant
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet


#Cleaning includes converting lowercase, remove stopwords wordnet, pucntuation
# remove email, mentions, URLs, use WordNet Lemmatizer and porter stemmer

class Reporting:

    def __init__(self):
        client = MongoClient('mongodb://localhost:27017/')
        self.db = client.ClimateChange
        self.petitionDocs = self.db.PetitionNewOpen
        self.userDocs = self.db.UserNew
        self.totalDocs=self.petitionDocs.find({},no_cursor_timeout=True).count()
        self.filteredWords=[]
        for i in range(self.totalDocs):
            self.filteredWords.append("")
        self.corpusVectorized=None
        self.vectorizer=None

    def getPetitionsWithWords(self, word1):
        cur = self.petitionDocs.find({"overview": {'$regex': word1}}, no_cursor_timeout=True)
        for u in cur:
            #print u['id']
            print 'petition: '+str(u['petition_id'])+' overview :'+u["overview"]

    def getUsersWithTopic(self, topic):
        cur = self.userDocs.find({"$or": [{"GT": 0}, {"GT": 1}]}, no_cursor_timeout=True)
        for u in cur:
            for top in u['LDA_topic50']:
                if top[0] == topic and top[1] > 0.2:
                    print u['id']

    def getUsersWithWords(self, word1):
        cur = self.userDocs.find({"$and": [{"GT": 0}, {"tweetsText": {'$regex': word1}}]}, no_cursor_timeout=True)
        for u in cur:
            print u['id']
            count = 0
            cur1 = self.tweetsDocs.find({"user_id": u['id']}, no_cursor_timeout=True)
            for t in cur1:
                for twt in t['text']:
                    if word1 in twt and not t['retweeted_status'][count]:
                        print 'user: ' + str(u['id']) + ' tweeted :' + twt + 'with tweet id : ' + str(
                            t['id'][count])
                    count += 1

    # LDA with 80% training and 20% testing as well as computing preplexity
    def get_petitionTopics_CSV(self):
        cur=self.petitionDocs.find({}, no_cursor_timeout=True)
        cur1=cur.sort('petition_id', 1)
        cursor=cur1#.limit(8)
        count=0
        with open('petitionTopics_CSV.csv', 'wb') as csv_petitions:
            writer = csv.writer(csv_petitions)
            header=["id"]
            for x in range(0, 50):
                header.append("topic_"+str(x))
            writer.writerow(header)
            for p in cursor:
                post=[p['petition_id']]
                for x in range (0,50):
                    post.append(0)
                # strip HTML tags from tweet
                if 'LDA_topic50' in p:
                    for t in p['LDA_topic50']:
                        post[t[0]+1]=t[1]
                    writer.writerow(post)

    def getTopicsWeights_CSV(self):
        topics={}
        topicsWeights = {}
        lines = open("Topics").read().splitlines()
        count=0
        for topic in lines:
            topics[count]=topic
            topicsWeights[count] = 0
            count+=1
        cur=self.petitionDocs.find({}, no_cursor_timeout=True)
        cur1=cur.sort('petition_id', 1)
        cursor=cur1#.limit(8)
        count=0
        with open('TopicsWeight_CSV.csv', 'wb') as csv_petitions:
            writer = csv.writer(csv_petitions)
            for p in cursor:
                # strip HTML tags from tweet
                if 'LDA_topic50' in p:
                    for t in p['LDA_topic50']:
                        if t[1]>0.09:
                            topicsWeights[t[0]]+=1
            for x in range(0, 50):
                post = []
                post.append(topics[x])
                post.append(topicsWeights[x])
                writer.writerow(post)






def main():
    obj = Reporting()
    #obj.get_petitionTopics_CSV()
    obj.getTopicsWeights_CSV()
    #obj.get_LDA_TFIDF(40)

if __name__ == '__main__':
    main()