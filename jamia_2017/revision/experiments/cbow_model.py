from chainer import Chain, functions as F, links as L, reporter

class TextCBOW(Chain):
    def __init__(self, embeddings, composition_func="sum"):
        super(TextCBOW, self).__init__()
        with self.init_scope():
            self.token_embeddings = L.EmbedID(embeddings.shape[0],
                                              embeddings.shape[1],
                                              embeddings)
            self.agg = getattr(F, composition_func)
            self.linear = L.Linear(embeddings.shape[1], 2)

    def __call__(self, xs):
        x_vecs = self.token_embeddings(xs)
        cbows = self.agg(x_vecs, axis=1)
        return self.linear(cbows)
