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
from sklearn.feature_extraction.text import TfidfVectorizer
reload(sys)
sys.setdefaultencoding('utf8')



#Cleaning includes converting lowercase, remove stopwords wordnet, pucntuation
# remove email, mentions, URLs, use WordNet Lemmatizer and porter stemmer

class LDAPreplexity:

    def __init__(self):
        client = MongoClient('mongodb://localhost:27017/')
        self.db = client.ClimateChange
        self.petitionDocs = self.db.PetitionNewOpen
        self.totalDocs=self.petitionDocs.find({},no_cursor_timeout=True).count()
        #self.Eighty= 0.8*self.totalDocs
        #self.Twenty = 0.2*self.totalDocs
        self.Eighty= 8
        self.Twenty= 2
        self.corpusVectorized=None
        self.vectorizer=None

    # LDA with 80% training and 20% testing as well as computing preplexity
    def get_LDA(self):
        verbNoun=['VBZ','VBP','VBN','VBG','VBD','VB','NNS','NNPS','NNP','NN']
        adverbAdjectives=['WRB','RBS','RBR','RB','JJS','JJR','JJ']
        articles = self.petitionDocs
        cur=articles.find({}, no_cursor_timeout=True)
        cur1=cur.sort('petition_id', 1)
        cursor=cur1.limit(int(self.Eighty))
        doc_complete=[]
        doc_clean=[]
        doc_completeT=[]
        doc_cleanT=[]
        tList=[]
        tListT = []
        count=0
        exclude = set(string.punctuation)
        stop = set(stopwords.words('english'))
        lines = open("stop3").read().splitlines()
        for word in lines:
            print word
            stop.add(word)
        mysqlStop = ["a", "about", "above", "above", "across", "after", "afterwards", "again", "against", "all",
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
                     "yourselves", "the"]
        for word in mysqlStop:
            stop.add(word)

        for p in cursor:
            #strip HTML tags from tweet
            strip = TextCleaning.strip_tags(p['title'].encode('UTF-8')+" "+p['overview'].encode('UTF-8'))
            doc_complete.append(strip)
            strip1=TextCleaning.cleanURLEmailMention(self,strip)
            words = set(nltk.corpus.words.words())
            EnCleanedDoc=" ".join(w for w in nltk.wordpunct_tokenize(strip1) \
                 if w.lower() in words or not w.isalpha())
            EnCleanedDoc = unicode(EnCleanedDoc, errors='ignore')
            maxdf = float(self.Eighty / self.totalDocs)
            self.vectorizer = TfidfVectorizer(min_df=1, max_df=maxdf)
            self.corpusVectorized = self.vectorizer.fit_transform(EnCleanedDoc)
            text = nltk.word_tokenize(EnCleanedDoc)
            posTag = nltk.pos_tag(text)
            countAdjAdv=0
            countNounVerb=0
            for cat in posTag:
                if cat[1] in verbNoun:
                    countNounVerb+=1
                elif cat[1] in adverbAdjectives:
                    countAdjAdv+=1
            if countNounVerb ==0:
                expressivness=0
            else:
                expressivness=countAdjAdv / countNounVerb
            cleaneddoc=TextCleaning.clean(self,EnCleanedDoc,stop,exclude)
            doc_clean.append(cleaneddoc)
            tList.append(p['petition_id'])
            count+=1
            self.petitionDocs.update({"petition_id": p['petition_id']}, {"$set": {"LDA_cleanedDescription": EnCleanedDoc,"expressivness":expressivness}}, False, False)


        # list for tokenized documents in loop
        doc_tok = [doc.split() for doc in doc_clean]
        # Creating the term dictionary of our courpus, where every unique term is assigned an index.
        dictionary = corpora.Dictionary(doc_tok)
        # Converting list of documents (corpus) into Document Term Matrix using dictionary prepared above.
        doc_term_matrix = [dictionary.doc2bow(doc) for doc in doc_tok]


        # Prepare the testing dataset
        countT=0
        cur=articles.find({}, no_cursor_timeout=True)
        cur1=cur.sort('petition_id', -1)
        cursor=cur1.limit(int(self.Twenty))
        for p in cursor:
            #strip HTML tags from tweet
            strip = TextCleaning.strip_tags(p['title'].encode('UTF-8')+" "+p['overview'].encode('UTF-8'))
            doc_completeT.append(strip)
            strip1=TextCleaning.cleanURLEmailMention(self,strip)
            words = set(nltk.corpus.words.words())
            EnCleanedDoc=" ".join(w for w in nltk.wordpunct_tokenize(strip1) \
                 if w.lower() in words or not w.isalpha())
            EnCleanedDoc = unicode(EnCleanedDoc, errors='ignore')
            text = nltk.word_tokenize(EnCleanedDoc)
            posTag = nltk.pos_tag(text)
            countAdjAdv=0
            countNounVerb=0
            for cat in posTag:
                if cat[1] in verbNoun:
                    countNounVerb+=1
                elif cat[1] in adverbAdjectives:
                    countAdjAdv+=1
            if countNounVerb ==0:
                expressivness=0
            else:
                expressivness=countAdjAdv / countNounVerb
            cleaneddoc=TextCleaning.clean(self,EnCleanedDoc,stop,exclude)
            doc_cleanT.append(cleaneddoc)
            tListT.append(p['petition_id'])
            countT+=1
            self.petitionDocs.update({"petition_id": p['petition_id']}, {"$set": {"LDA_cleanedDescription": EnCleanedDoc,"expressivness":expressivness}}, False, False)

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
            with open('LDAout'+str(top)+'topics.txt', 'w') as f:
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
                    self.petitionDocs.update({'petition_id': tList[it]}, {"$set": post}, upsert=False)
                    str1 = ''.join(str(post['LDA_topic'+str(top)]))
                    print str(tList[it]) + ' has topics ' + str1
                except Exception as e:
                    print 'error in setting LDA for tweet: ' + str(tList[it])
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
                    self.petitionDocs.update({'petition_id': tListT[it]}, {"$set": post}, upsert=False)
                    str1 = ''.join(str(post['LDA_topic' + str(top)]))
                    print str(tListT[it]) + ' has topics ' + str1
                except Exception as e:
                    print 'error in setting LDA for tweet: ' + str(tListT[it])
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
        fig.savefig('perp')


def main():
    obj = LDAPreplexity()
    obj.get_LDA()

if __name__ == '__main__':
    main()