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
import matplotlib.pyplot as plt
import numpy as np
import TextCleaning
import enchant
import nltk
import sys
reload(sys)
sys.setdefaultencoding('utf8')

#Cleaning includes converting lowercase, remove stopwords wordnet, pucntuation
# remove email, mentions, URLs, use WordNet Lemmatizer and porter stemmer

class LDAPreplexity:

    def __init__(self):
        client = MongoClient('mongodb://localhost:27017/')
        self.db = client.ClimateChange
        self.userDocs = self.db.UserNew
        self.totalDocs=self.userDocs.find({"$or": [{"GT": 0}, {"GT": 1}]},no_cursor_timeout=True).count()
        self.Eighty= 0.8*self.totalDocs
        self.Twenty = 0.2*self.totalDocs
        #self.Eighty= 8
        #self.Twenty= 2

    # LDA with 80% training and 20% testing as well as computing preplexity
    def get_petitionTopics_CSV(self):
        cur=self.userDocs.find({"$or": [{"GT": 0}, {"GT": 1}]}, no_cursor_timeout=True)
        cur1=cur.sort('id', 1)
        cursor=cur1#.limit(8)
        count=0
        with open('userTopics_CSV.csv', 'wb') as csv_petitions:
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
        lines = open("TweetsLDA/Topics").read().splitlines()
        count=0
        for topic in lines:
            topics[count]=topic
            topicsWeights[count] = 0
            count+=1
        cur = self.userDocs.find({"$or": [{"GT": 0}, {"GT": 1}]}, no_cursor_timeout=True)
        cur1=cur#.sort('id', 1)
        cursor=cur1#.limit(8)
        count=0
        with open('userTopicsWeight_CSV.csv', 'wb') as csv_petitions:
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



    # LDA with 80% training and 20% testing as well as computing preplexity
    def get_LDA(self):
        verbNoun=['VBZ','VBP','VBN','VBG','VBD','VB','NNS','NNPS','NNP','NN']
        adverbAdjectives=['WRB','RBS','RBR','RB','JJS','JJR','JJ']
        cursor=self.userDocs.find({"$or": [{"GT": 0}, {"GT": 1}]}, no_cursor_timeout=True).sort('id', 1).limit(int(self.Eighty))
        doc_complete=[]
        doc_clean=[]
        doc_completeT=[]
        doc_cleanT=[]
        tList=[]
        tListT=[]
        count=0
        exclude = set(string.punctuation)
        stop = set(stopwords.words('english'))
        lines = open("stop3").read().splitlines()
        dict = enchant.DictWithPWL("en_US")
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
            temp=""
            #strip = TextCleaning.strip_tags(p['title'].encode('UTF-8')+" "+p['overview'].encode('UTF-8'))
            strip = TextCleaning.strip_tags(p['tweetsText'].encode('UTF-8'))
            doc_complete.append(strip)
            strip1=TextCleaning.cleanURLEmailMention(self,strip)
            words = set(nltk.corpus.words.words())
            EnCleanedDoc = unicode(strip1, errors='ignore')
            text = nltk.word_tokenize(EnCleanedDoc)
            countAdjAdv=0
            countNounVerb=0
            tp = nltk.pos_tag(text)
            for (w, pos) in tp:
                if pos in verbNoun or pos in adverbAdjectives:
                    if len(w) > 2 and w.isalpha() and w.lower() not in stop:
                        temp=temp+" "+wnl.lemmatize(w.lower(), TextCleaning.get_wordnet_pos(pos))
                        if pos in verbNoun:
                            countNounVerb += 1
                        elif pos in adverbAdjectives:
                            countAdjAdv += 1

            doc_clean.append(temp)
            tList.append(p['id'])
            count+=1

        # list for tokenized documents in loop
        doc_tok = [doc.split() for doc in doc_clean]
        # Creating the term dictionary of our courpus, where every unique term is assigned an index.
        dictionary = corpora.Dictionary(doc_tok)
        # Converting list of documents (corpus) into Document Term Matrix using dictionary prepared above.
        doc_term_matrix = [dictionary.doc2bow(doc) for doc in doc_tok]


        # Prepare the testing dataset
        countT=0
        cursor = self.userDocs.find({"$or": [{"GT": 0}, {"GT": 1}]}, no_cursor_timeout=True).sort('id', -1).limit(int(self.Twenty))
        for p in cursor:
            temp = ""
            #strip = TextCleaning.strip_tags(p['title'].encode('UTF-8') + " " + p['overview'].encode('UTF-8'))
            strip = TextCleaning.strip_tags(p['tweetsText'].encode('UTF-8'))
            doc_complete.append(strip)
            strip1 = TextCleaning.cleanURLEmailMention(self, strip)
            words = set(nltk.corpus.words.words())
            # EnCleanedDoc=" ".join(w for w in nltk.wordpunct_tokenize(strip1) if not w.isalpha())#w.lower() in words or
            EnCleanedDoc = unicode(strip1, errors='ignore')
            text = nltk.word_tokenize(EnCleanedDoc)
            countAdjAdv = 0
            countNounVerb = 0
            tp = nltk.pos_tag(text)
            for (w, pos) in tp:
                if pos in verbNoun or pos in adverbAdjectives:
                    if len(w) > 2 and w.isalpha() and w.lower() not in stop:
                        temp = temp + " " + wnl.lemmatize(w.lower(), TextCleaning.get_wordnet_pos(pos))
                        if pos in verbNoun:
                            countNounVerb += 1
                        elif pos in adverbAdjectives:
                            countAdjAdv += 1

            doc_cleanT.append(temp)
            tListT.append(p['id'])
            countT += 1

        # list for tokenized documents in loop
        doc_tokT = [doc.split() for doc in doc_cleanT]
        # Creating the term dictionary of our courpus, where every unique term is assigned an index.
        dictionaryT = corpora.Dictionary(doc_tokT)
        # Converting list of documents (corpus) into Document Term Matrix using dictionary prepared above.
        doc_term_matrixT = [dictionaryT.doc2bow(doc) for doc in doc_tokT]


        # Creating the object for LDA model using gensim library
        Lda = gensim.models.ldamodel.LdaModel

        # Running LDA with different number of topics and getting the lowest preplexity
        topics=[10,30,40,50,80,100]
        perplexity=[]
        for top in topics:
            # Running and Trainign LDA model on the document term matrix.
            ldamodel = Lda(doc_term_matrix, num_topics=top, id2word=dictionary, passes=50)
            LDAOut=ldamodel.print_topics(num_topics=top, num_words=10)
            perplex = Lda.bound(ldamodel, doc_term_matrixT)
            with open('UserLDAout'+str(top)+'topics.txt', 'w') as f:
                print >> f, "-----------Run for "+str(top)+" topics ---------------------------------------------"
                print >> f, LDAOut
                print >> f, "-------------------------------------------------------------------------"
                print >> f, "perplexity ="+str(perplex)
                print >> f, "-----------Run for "+str(top)+" topics ---------------------------------------------"
            f.close()
            print "-----------Run for " + str(top) + " topics ---------------------------------------------"
            print LDAOut
            print  "-------------------------------------------------------------------------"
            print "perplexity ="+str(perplex)
            print "-----------Run for "+str(top)+" topics ---------------------------------------------"
            # printing LDA results with word count parameter for each topic
            perplexity.append(perplex)

            plen=count
            for it in range(0,plen):
                print 'saving tweets topics probability distribution for topic '+str(top)
                try:
                    post = {}
                    # Prepare LDA topic scores for each petition
                    post['LDA_topic'+str(top)] = ldamodel[doc_term_matrix[it]]
                    print '' \
                          ''
                    # Update topic score in database
                    self.userDocs.update({'id': tList[it]}, {"$set": post}, upsert=False)
                    str1 = ''.join(str(post['LDA_topic'+str(top)]))
                    print str(tList[it]) + ' has topics ' + str1
                except Exception as e:
                    print 'error in setting LDA for user tweet: ' + str(tList[it])
                    print(e)

            # testing
            plen = countT
            for it in range(0, plen):
                print 'saving tweets topics probability distribution for topic ' + str(top)
                try:
                    post = {}
                    # Prepare LDA topic scores for each petition
                    post['LDA_topic' + str(top)] = ldamodel[doc_term_matrixT[it]]
                    print '' \
                          ''
                    # Update topic score in database
                    self.userDocs.update({'id': tListT[it]}, {"$set": post}, upsert=False)
                    str1 = ''.join(str(post['LDA_topic' + str(top)]))
                    print str(tListT[it]) + ' has topics ' + str1
                except Exception as e:
                    print 'error in setting LDA for user tweet: ' + str(tListT[it])
                    print(e)
        # Prepare the data
        xArr = np.array(topics)
        yArr = np.array(perplexity)
        # Plot the data

        fig = plt.figure()
        plt.plot(xArr, yArr, label='linear')
        fig.suptitle('Held-out per-word perplexity', fontsize=20)
        plt.xlabel('Number of Topics', fontsize=16)
        plt.ylabel('Perplexity', fontsize=16)

        # Show the plot
        plt.show()
        fig.savefig('UserPerp')


def main():
    obj = LDAPreplexity()
    #obj.get_LDA()
    obj.getTopicsWeights_CSV()

if __name__ == '__main__':
    main()