from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string
from nltk.stem import PorterStemmer
from HTMLParser import HTMLParser
import re

import nltk
from nltk.corpus import PlaintextCorpusReader
from nltk.corpus import stopwords
from nltk.corpus.reader.util import read_line_block

from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem import PorterStemmer
import enchant


from nltk.util import ngrams
from nltk.probability import FreqDist

import gensim
from gensim import corpora

import random

from nltk.corpus import wordnet

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()




    #Remove Stop words, punctuation, and extract lemmatization, and stemming.
def clean(self,doc,stop,exclude):
    lemma = WordNetLemmatizer()
    ps = PorterStemmer()
    stop_free = " ".join([i for i in doc.lower().split() if i not in stop])
    no_punc = map(lambda x: re.sub("[^a-z]", " ", x), stop_free)
    punc_free = "".join(ch for ch in no_punc if ch not in exclude)
    normalized=""
    stemmed = ""
    for word in punc_free.split():
        try:
            lWord=lemma.lemmatize(word)
        except:
            continue
        normalized=normalized+lWord+" "
    for nword in normalized.split():
        try:
            sWord=ps.stem(nword)
        except:
            continue
        stemmed=stemmed+sWord+" "
    stop_free2 = " ".join([i for i in stemmed.lower().split() if i not in stop])
    return stop_free2

#Remove Email, url and mentions from tweets
def cleanURLEmailMention(self,strip):
    # extract emails
    match = re.findall(r'[\w\.-]+@[\w\.-]+', strip)
    temp = strip
    for m in match:
        temp = strip.replace(m, '', 100)
        strip = temp
    match2 = re.findall("@([a-zA-Z0-9]{1,15})", strip)
    for m in match2:
        temp = strip.replace(m, '', 100)
        strip = temp
    match3 = re.findall(r'^https?:\/\/.*[\r\n]*', strip)
    for m in match3:
        temp = strip.replace(m, '', 100)
        strip = temp
    return strip




def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    elif treebank_tag.startswith('W'):
        return wordnet.ADV
    else:
        return ''

