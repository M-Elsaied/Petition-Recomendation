from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string
from nltk.stem import PorterStemmer
import re
import sys
import numpy as np
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from gensim.models import LdaModel, LsiModel
import gensim
import os
import pandas as pd

reload(sys)
sys.setdefaultencoding('utf8')



#Cleaning includes converting lowercase, remove stopwords wordnet, pucntuation
# remove email, mentions, URLs, use WordNet Lemmatizer and porter stemmer

class Assignment3:

    def __init__(self):
        self.directory = "/Users/ahmed/Desktop/DSU/Courses/INFS770/L4/awd_2003/"
        self.docs = []
        self.totalDocs=0
        self.Eighty= 0
        self.vectorizer=None
        self.corpusVectorized=None
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
        exclude = set(string.punctuation)
        self.stopWords = set(nltk.corpus.stopwords.words('english'))
        for word in mysqlStop:
            self.stopWords.add(word)
        for word in exclude:
            self.stopWords.add(word)


    def getAbstracts(self):
        all_files = os.listdir(self.directory)  # get a list of filenames in the directory
        for afile in all_files:  # for each file
            filename = self.directory + afile
            f = open(filename, 'rU')
            file_content = f.read()  # read each file as a string
            abstract = file_content.split("Abstract", 1)[
                1]  # we want to extract abstract from the file and remove things before "Abstract"
            self.docs.append(abstract)  # add the abstract to the corpus
            self.totalDocs=len(self.docs)
            self.Eighty = round(float(0.8*len(self.docs)))
        f.close()
        return  self.docs

    def remove_stopwords(self,doc):
        return " ".join([i for i in doc.lower().split() if i not in self.stopWords])


    def tokenizeAbstract(self):
        # tokenize each document
        #tokenized = map(nltk.word_tokenize, no_punc)
        no_stopwords = map(self.remove_stopwords, self.docs)
        # replace punctuation with space
        no_punc = map(lambda x: re.sub("[^a-z]", " ", x), no_stopwords)

        maxdf=float(self.Eighty/self.totalDocs)
        self.vectorizer = TfidfVectorizer(min_df=1, max_df=maxdf)
        self.corpusVectorized = self.vectorizer.fit_transform(no_punc)
        return self.corpusVectorized

    def truncatedSVD(self,topics):
        tsvd = TruncatedSVD(n_components=topics)
        tsvd.fit(self.corpusVectorized)
        print np.round(tsvd.transform(self.corpusVectorized), 3)
        #print tsvd.singular_values_
        print tsvd.explained_variance_ratio_

    def LDA(self, topics):
        # convert the vectorized data to a gensim corpus object
        corpus = gensim.matutils.Sparse2Corpus(self.corpusVectorized, documents_columns=False)
        # maintain a dictionary for index-word mapping
        id2word = dict((v, k) for k, v in self.vectorizer.vocabulary_.iteritems())
        print id2word
        # build the lda model
        lda = LdaModel(corpus, num_topics=topics, id2word=id2word, passes=10)
        print lda.print_topics()
        lda_docs = lda[corpus]
        for row in lda_docs:
            print row
        scores = np.round([[doc[1] for doc in row] for row in lda_docs], 3)
        print scores
        cols=[]
        for i in range(topics):
            cols.append("topic "+str(i))
        df_lda = pd.DataFrame(scores, columns=cols)
        df_lda
    # LDA with 80% training and 20% testing as well as computing preplexity


def main():
    obj = Assignment3()
    #Q1
    print obj.getAbstracts()
    #Q2
    print obj.tokenizeAbstract()
    print len(obj.vectorizer.get_feature_names())
    #Q3
    print obj.truncatedSVD(2)
    #Q4
    print obj.LDA(2)
    #Q5 and Q6
    print obj.LDA(3)
    #obj.get_LDA()

if __name__ == '__main__':
    main()