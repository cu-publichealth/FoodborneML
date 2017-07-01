import numpy as np
from chainer import Chain, functions as F, links as L, reporter
from chainer_monitor import monitor

class TextCNN(Chain):
    def __init__(self, embeddings, n_filters_per,
                 ngrams=[1,2],
                 pooling='max',
                 activation_func='leaky_relu',
                 dropout_prob=0.):
        super(TextCNN, self).__init__()
        with self.init_scope():
            self.token_embeddings = L.EmbedID(embeddings.shape[0],
                                              embeddings.shape[1],
                                              embeddings)
            self.convs = []
            for n in ngrams:
                conv = L.Convolution2D(1, n_filters_per,
                                      ksize=(n, embeddings.shape[1]),
                                      pad=(n-1, 0))
                setattr(self, 'conv_{}'.format(n), conv)
                self.convs.append(conv)
            if pooling == 'max':
                self.pool = F.max
            elif pooling == 'logsumexp':
                self.pool = F.logsumexp
            elif pooling == 'avg':
                self.pool = F.mean
            else:
                raise ValueError, 'Invalid pooling function. Must be `max`, `avg`, or `logsumexp`'
            self.f = getattr(F, activation_func)
            m = 2 if activation_func == 'crelu' else 1
            self.linear = L.Linear(m*len(ngrams)*n_filters_per, 2)
            self.p = dropout_prob

    def __call__(self, xs):
        x_vecs = F.dropout(self.token_embeddings(xs), self.p)
        # x_vecs = self.token_embeddings(xs)
        monitor('word vectors', x_vecs, self)
        # print 'x_vec shape:', x_vecs.shape
        filter_activations = [ F.dropout(self.f(conv(F.expand_dims(x_vecs,1))), self.p)
                               for conv in self.convs ]
        # filter_activations = [ self.f(conv(F.expand_dims(x_vecs,1)))
                            #   for conv in self.convs ]
        for i, f in enumerate(filter_activations):
            monitor('f(cnn(activation)) for ngram {}'.format(i), f, self)

        # We set all 0 values to 1e-15 for logsumexp.
        # This is because zero-padding actually drowns out all of the signal
        # because exp(0)=1 and we have an activation of 1 for most elements.
        # (Especially in the case of highly varying document length)
        # Although not perfectly correct, we assume anything with an activation
        # very close to zero is a pad and shouldn't be included in logsumexp
        # which we effectively do by setting it to 1e-15
        # if self.pool == F.logsumexp:
        #     for i, f in enumerate(filter_activations):
        #         print 'filter {}: % zero observations = {}'.format(
        #             i, 100.*np.sum(np.abs(f.data) < 1e-5)/float(f.data.size)
        #         )
        #         f.data[np.abs(f.data) < 1e-5] = 1e-15
        # print 'activations shape:', [a.shape for a in filter_activations]
        pooled_filters = [ self.pool(activation, axis=2)
                           for activation in filter_activations ]
        # print 'pooled concat shape:', F.hstack(pooled_filters).shape
        concat = F.dropout(F.hstack(pooled_filters), self.p)
        concat = F.hstack(pooled_filters)
        monitor('pooled concat activations', concat, self)
        return self.linear(concat)
