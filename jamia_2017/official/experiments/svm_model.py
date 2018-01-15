from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV

# svm pipeline def
f1 = CountVectorizer(
        input=u'content',
        encoding=u'utf-8',
        decode_error=u'strict',
        strip_accents=None,
        lowercase=True,
        preprocessor=None,
        tokenizer=None,
        stop_words=None,
        ngram_range=(1, 3),
        analyzer=u'word',
        max_df=.93,
        min_df=1,
        max_features=None,
        vocabulary=None,
        binary=False,
        )
tfidf = TfidfTransformer(norm='l2', use_idf=True)
svc = CalibratedClassifierCV(LinearSVC(C=30))
model = Pipeline([
        ('count', f1),
        ('tfidf', tfidf),
        ('svc',svc)
    ])
