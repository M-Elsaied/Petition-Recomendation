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
import TextCleaning
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

class LDA:


    def preprocessing(self):
        cur=self.userDocs.find({}, no_cursor_timeout=True)
        cursor=cur#.limit(8)
        doc_complete=[]
        doc_clean=[]
        tList=[]
        count=0
        for u in cursor:
            t_tweetsText=""
            t_tweetsHashtags=0
            t_tweetsFavorite_count=0
            t_tweetsRetweets_count = 0
            tweetsCollectedFilteredNo=0
            tweetsAvgLength = 0
            t_tweetsFilteredLength=0
            usertweets=self.tweetsDocs.find({"user_id":u['id']}, no_cursor_timeout=True)
            for ut in usertweets:
                tweetsCollected=ut['id_str']
                tweetsText=ut['text']
                tweetsFavorite_count=ut['favorite_count']
                tweetsRetweets_count=ut['retweet_count']
                tweetsHashtags = ut['hashtagsNumber']
                tweetsURL = ut['urls']
                tweetsRetweets_status = ut['retweeted_status']
            countTweets=0
            for t in tweetsCollected:
                if not tweetsURL[countTweets] and not tweetsRetweets_status[countTweets]:
                    t_tweetsText=t_tweetsText+" "+tweetsText[countTweets]
                    t_tweetsHashtags+=tweetsHashtags[countTweets]
                    t_tweetsFavorite_count += tweetsFavorite_count[countTweets]
                    t_tweetsRetweets_count += tweetsRetweets_count[countTweets]
                    tweetsCollectedFilteredNo+=1
                    t_tweetsFilteredLength+=len(tweetsText[countTweets])
                countTweets+=1
            if tweetsCollectedFilteredNo==0:
                tweetsAvgLength = 0
            else:
                tweetsAvgLength = t_tweetsFilteredLength / tweetsCollectedFilteredNo
            post={}
            try:
                post['tweetsText']=t_tweetsText
                post['tweetsHashtags'] = t_tweetsHashtags
                post['tweetsFavorite_count'] = t_tweetsFavorite_count
                post['tweetsRetweets_count'] = t_tweetsRetweets_count
                post['tweetsCollectedFilteredNo'] = tweetsCollectedFilteredNo
                post['tweetsCollectedNo'] = countTweets
                post['tweetAvgLength'] = tweetsAvgLength
                self.userDocs.update({'id': u['id']}, {"$set": post}, upsert=False)
            except Exception as e:
                print 'error in setting LDA for user: ' + str(u['id'])+'iteration: '+str(count)
                print(e)
            count+=1



    def __init__(self):
        client = MongoClient('mongodb://localhost:27017/')
        self.db = client.ClimateChange
        self.userDocs = self.db.UserNew
        self.tweetsDocs = self.db.TweetsNew
        self.totalDocs=self.tweetsDocs.find({"$or": [{"GT": 0}, {"GT": 1}]},no_cursor_timeout=True).count()
        self.filteredWords=[]
        for i in range(self.totalDocs):
            self.filteredWords.append("")
        self.corpusVectorized=None
        self.vectorizer=None

    # LDA with 80% training and 20% testing as well as computing preplexity
    def get_LDA(self, nonRatingUsersLimit):
        verbNoun=['VBZ','VBP','VBN','VBG','VBD','VB','NNS','NNPS','NNP','NN']
        adverbAdjectives=['WRB','RBS','RBR','RB','JJS','JJR','JJ']
        cur=self.userDocs.find({"$or": [{"GT": 0}, {"GT": 1}]}, no_cursor_timeout=True)
        cur1=cur.sort('id', 1)
        cursor=cur1#.limit(8)
        doc_complete=[]
        doc_clean=[]
        tList=[]
        count=0
        exclude = set(string.punctuation)
        stop = set(stopwords.words('english'))
        lines = open("stop3").read().splitlines()

        dict = enchant.DictWithPWL("en_US")
        typos = set()
        wnl = WordNetLemmatizer()
        for word in lines:
            print word
            stop.add(word)
        myStop = ["a", "about", "above", "above", "across", "after", "afterwards", "again", "against", "all",
                     "almost", "alone", "along", "already", "also", "although", "always", "am", "among", "amongst",
                     "amoungst", "amount", "an", "and", "another", "any", "anyhow", "anyone", "anything", "anyway",
                     "anywhere", "are", "around", "as", "at", "back", "be", "became", "because", "become", "becomes",
                     "becoming", "been", "before", "beforehand", "behind", "being", "below", "beside", "besides",
                     "between", "beyond", "bill", "both", "bottom", "but", "by", "call", "can", "cannot", "cant", "co",
                     "con", "could", "couldnt", "cry", "de", "describe", "detail", "do", "done", "down", "due",
                     "during", "each", "eg", "eight", "either", "eleven", "else", "elsewhere", "empty", "enough", "etc",
                     "even", "ever", "every", "everyone", "everything", "everywhere", "except", "few", "fifteen",
                     "fify", "fill", "find", "fire", "first", "five", "for", "former", "formerly", "forty", "found",
                     "four", "from", "front", "full", "further", "get", "give", "go", "had", "has", "hasnt", "have",
                     "he", "hence", "her", "here", "hereafter", "hereby", "herein", "hereupon", "hers", "herself",
                     "him", "himself", "his", "how", "however", "hundred", "ie", "if", "in", "inc", "indeed",
                     "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter", "latterly", "least",
                     "less", "ltd", "made", "many", "may", "me", "meanwhile", "might", "mill", "mine", "more",
                     "moreover", "most", "mostly", "move", "much", "must", "my", "myself", "name", "namely", "neither",
                     "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone", "nor", "not", "nothing",
                     "now", "nowhere", "of", "off", "often", "on", "once", "one", "only", "onto", "or", "other",
                     "others", "otherwise", "our", "ours", "ourselves", "out", "over", "own", "part", "per", "perhaps",
                     "please", "put", "rather", "re", "same", "see", "seem", "seemed", "seeming", "seems", "serious",
                     "several", "she", "should", "show", "side", "since", "sincere", "six", "sixty", "so", "some",
                     "somehow", "someone", "something", "sometime", "sometimes", "somewhere", "still", "such", "system",
                     "take", "ten", "than", "that", "the", "their", "them", "themselves", "then", "thence", "there",
                     "thereafter", "thereby", "therefore", "therein", "thereupon", "these", "they", "thickv", "thin",
                     "third", "this", "those", "though", "three", "through", "throughout", "thru", "thus", "to",
                     "together", "too", "top", "toward", "towards", "twelve", "twenty", "two", "un", "under", "until",
                     "up", "upon", "us", "very", "via", "was", "we", "well", "were", "what", "whatever", "when",
                     "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "whereupon",
                     "wherever", "whether", "which", "while", "whither", "who", "whoever", "whole", "whom", "whose",
                     "why", "will", "with", "within", "without", "would", "yet", "you", "your", "yours", "yourself",
                     "yourselves", "the", 'http', 'https', '://', 'www', 'com', '8800', '...', '....','//','/','..', 'yep', '.).', '](#', '.:).',
                    '++..', 'github', 'etc', 'also', 'org', 'gee', 'let', 'know', 'ever',
                    'vcntr', 'falseamount', 'isig']
        for word in myStop:
            stop.add(word)

        for p in cursor:
            #strip HTML tags from tweet
            temp=""
            strip = TextCleaning.strip_tags(p['tweetsText'].encode('UTF-8'))
            doc_complete.append(strip)
            strip1=TextCleaning.cleanURLEmailMention(self,strip)
            words = set(nltk.corpus.words.words())
            #EnCleanedDoc=" ".join(w for w in nltk.wordpunct_tokenize(strip1) if not w.isalpha())#w.lower() in words or
            EnCleanedDoc = unicode(strip1, errors='ignore')
            text = nltk.word_tokenize(EnCleanedDoc)
            countAdjAdv=0
            countNounVerb=0
            tp = nltk.pos_tag(text)
            for (w, pos) in tp:
                if len(w) > 2 and w.isalpha() and w.lower() not in stop:
                    if pos in verbNoun or pos in adverbAdjectives:
                        temp=temp+" "+wnl.lemmatize(w.lower(), TextCleaning.get_wordnet_pos(pos))
                        if pos in verbNoun:
                            countNounVerb += 1
                        elif pos in adverbAdjectives:
                            countAdjAdv += 1
            if countNounVerb ==0:
                expressivness=0
            else:
                expressivness=countAdjAdv / countNounVerb
            doc_clean.append(temp)
            tList.append(p['id'])
            count+=1
            self.userDocs.update({"id": p['id']}, {"$set": {"LDA_cleanedDescription": temp,"expressivness":expressivness}}, False, False)

        # add non rating users to the sample
        cur = self.userDocs.find({ "GT": { "$exists": False }} , no_cursor_timeout=True).limit(nonRatingUsersLimit)
        for p in cur:
            #strip HTML tags from tweet
            temp=""
            strip = TextCleaning.strip_tags(p['tweetsText'].encode('UTF-8'))
            doc_complete.append(strip)
            strip1=TextCleaning.cleanURLEmailMention(self,strip)
            words = set(nltk.corpus.words.words())
            #EnCleanedDoc=" ".join(w for w in nltk.wordpunct_tokenize(strip1) if not w.isalpha())#w.lower() in words or
            EnCleanedDoc = unicode(strip1, errors='ignore')
            text = nltk.word_tokenize(EnCleanedDoc)
            countAdjAdv=0
            countNounVerb=0
            tp = nltk.pos_tag(text)
            for (w, pos) in tp:
                if len(w) > 2 and w.isalpha() and w.lower() not in stop:
                    if pos in verbNoun or pos in adverbAdjectives:
                        temp=temp+" "+wnl.lemmatize(w.lower(), TextCleaning.get_wordnet_pos(pos))
                        if pos in verbNoun:
                            countNounVerb += 1
                        elif pos in adverbAdjectives:
                            countAdjAdv += 1
            if countNounVerb ==0:
                expressivness=0
            else:
                expressivness=countAdjAdv / countNounVerb
            doc_clean.append(temp)
            tList.append(p['id'])
            count+=1
            self.userDocs.update({"id": p['id']}, {"$set": {"LDA_cleanedDescription": temp,"expressivness":expressivness,"GT":-1}}, False, False)


        # Creating the object for LDA model using gensim library
        Lda = gensim.models.ldamodel.LdaModel

        # Running LDA with the threshold after getting the optimum perplexity from PetitionsLDAPerplexity.py
        top =50
        # Running and Trainign LDA model on the document term matrix.
        self.vectorizer = TfidfVectorizer()
        self.corpusVectorized = self.vectorizer.fit_transform(doc_clean)
        print self.corpusVectorized
        df_vect = pd.DataFrame(self.corpusVectorized.toarray(), columns=self.vectorizer.get_feature_names())
        print df_vect
        corpus = gensim.matutils.Sparse2Corpus(self.corpusVectorized, documents_columns=False)
        print corpus
        id2word = {}
        for key, val in self.vectorizer.vocabulary_.items():
            id2word[val] = key
        print id2word
        #id2word = dict((v, k) for k, v in self.vectorizer.vocabulary_.iteritems())
        ldamodel = models.LdaModel(corpus, num_topics=top, id2word=id2word, passes=50)
        LDAOut=ldamodel.print_topics(num_topics=top, num_words=10)
        lda_docs = ldamodel[corpus]
        c=0
        for row in lda_docs:
            post = {}
            for tops in range(0, top):
                post['TFIDF_LDA_' + str(top) + 'topics_topic' + str(tops)] = 0
            for tup in row:
                try:
                    post['TFIDF_LDA_'+str(top)+'topics_topic' + str(tup[0])] = tup[1]
                except Exception as e:
                    print(e)
            try:
                self.userDocs.update({'id': tList[c]}, {"$set": post}, upsert=False)
            except Exception as e:
                print 'error in setting LDA for user: ' + str(tList[c])
                print(e)
            print row
            print len(row)
            c+=1

    def renameTFIDFColumn(self):
        cur = self.userDocs.find({"$or": [{"GT": 0}, {"GT": 1}]}, no_cursor_timeout=True)
        for u in cur:
            post={}
            for key, value in u.iteritems():
                if "TFIDF_LDA_50topic_" in key:
                    key.rfind('_')
                    start=key.rfind('_')+1
                    num=key[start:]
                    post['TFIDF_LDA_50topics_topic'+num]=u[key]
            try:
                self.userDocs.update({'id': u['id']}, {"$set": post}, upsert=False)
            except Exception as e:
                print 'error in setting LDA for user: ' + str(u['id'])
                print(e)


def main():
    obj = LDA()
    obj.get_LDA(500)
    #obj.preprocessing()
    #obj.get_LDA_TFIDF(40)
    #obj.getUsersWithTopic(30)
    #'snack','business','customer'
    obj.getUsersWithWords('Yemen')
    #obj.renameTFIDFColumn()

if __name__ == '__main__':
    main()