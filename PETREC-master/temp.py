import os
import json
import pandas as pd
import numpy as np
from re import sub, compile
from sklearn.model_selection import StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import metrics

# the location for tweets in json format
data_file = "amazon_review_texts.csv"  # you need to change this


# read the labels
df_labels = pd.read_csv(data_file,
                        names=["pid", "helpful","score","text","category"])
print df_labels.head()