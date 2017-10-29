from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import LogisticRegression

#logistic regression pipeline def
f1 = CountVectorizer(
        input=u'content',
        encoding=u'utf-8',
        decode_error=u'strict',
        strip_accents=None, 
        lowercase=True,
        preprocessor=None,
        tokenizer=None,
        stop_words=None,
        ngram_range=(1, 1),
        analyzer=u'word',
        max_df=.95,
        min_df=1,
        max_features=None,
        vocabulary=None,
        binary=False,
        )
tfidf = TfidfTransformer(norm='l2', use_idf=True)
logreg = LogisticRegression(
    fit_intercept=True,
    C=100,
    penalty='l2',
    verbose=0
)
model = Pipeline([
        ('count', f1),
        ('tfidf', tfidf),
        ('logreg',logreg)
    ])
