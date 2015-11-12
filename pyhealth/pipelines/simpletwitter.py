"""
SimpleTwitter

Feature Extractors:
1. Word Counts
 * Split on whitespace
 * No stop words
 * unigrams only

Final Classifier:
Naive Bayes

"""

from sklearn.pipeline import Pipeline

# Feature Extractors
from sklearn.feature_extraction.text import CountVectorizer
f1 = CountVectorizer(
        input=u'content', 
        encoding=u'utf-8', 
        decode_error=u'strict', 
        strip_accents=None, 
        lowercase=True, 
        preprocessor=None, 
        tokenizer=None, 
        stop_words=None, 
        #token_pattern=u'(?u)\\b\w\w+\b', # one alphanumeric is a token
        ngram_range=(1, 2), 
        analyzer=u'word', 
        max_df=1.0, 
        min_df=1, 
        max_features=None, 
        vocabulary=None, 
        binary=False, 
        #dtype=type 'numpy.int64'>
        )

# Final Classifier
from sklearn.naive_bayes import MultinomialNB
nb = MultinomialNB(
        alpha=1.0, # smoothing param
        fit_prior=True, 
        class_prior=None
        )


pipeline = Pipeline([
    ('count', f1), 
    ('multinb', nb)
    ])