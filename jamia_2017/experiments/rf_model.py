from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.ensemble import RandomForestClassifier


# random forest pipeline def
f1 = CountVectorizer(
        input=u'content',
        encoding=u'utf-8',
        decode_error=u'strict',
        strip_accents=None,
        lowercase=True,
        preprocessor=None,
        tokenizer=None,
        stop_words=None,
        ngram_range=(1, 2),
        analyzer=u'word',
        max_df=.94,
        min_df=1,
        max_features=1000,
        vocabulary=None,
        binary=False,
        )
tfidf = TfidfTransformer(norm='l1', use_idf=True)
rf = RandomForestClassifier(
    oob_score=True,
    n_estimators=150,
    max_depth=None,
    max_features='sqrt',
    random_state=0
)
model = Pipeline([
        ('count', f1),
        ('tfidf', tfidf),
        ('rf',rf)
    ])
