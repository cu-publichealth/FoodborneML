""" A bells and whistles implementation of a vocab wrapper object.

It does a couple of nice things:
* It automatically includes a PAD and an UNK token
* It can construct a vocab iteratively
* It keeps the count of all tokens
* It can drop infrequent tokens and reindex the vocab based on this
    * This reindexing is deterministic

There is probably a better implementation out there... I just know this one
"""

from collections import Counter
import numpy as np
import numpy.random as npr

class Vocab():
    """ A convenience vocabulary wrapper

    TODO: Add in sampling table functionality
    """
    def __init__(self,
                 tokens=None,
                 min_count=5,
                 pad_token='<PAD>',
                 unk_token='<UNK>'):
        self.min_count = min_count
        self.pad_token = pad_token
        self.unk_token = unk_token

        self.use(tokens)
#         self.make_sampling_table()

    @property
    def n(self):
        """ The total number of tokens seen by the vocabulary.

        This **does not** include tokens which have not been seen `min_count` times
        """
        return self._n

    @property
    def v(self):
        """ The total number of unique tokens in the vocabulary.

        This **does not** include tokens which have not been seen `min_count` times
        """
        return self._v

    @property
    def pad(self):
        """ Return the PAD token """
        return self.pad_token

    @property
    def ipad(self):
        """ Return the index of the PAD token """
        return self.idx(self.pad_token)

    @property
    def unk(self):
        """ Return the UNK token """
        return self.unk_token

    @property
    def iunk(self):
        """ Return the index of the UNK token """
        return self.idx(self.unk_token)

    def idx(self, token):
        """ Return the index of a token or the index of UNK if not in vocab.

        Additionally this will return UNK if the token is in the vocab
        but has yet to be seen `min_count` times
        """
        try:
            if token is not None and token == self.pad_token:
                return self._vocab2idx[token]
            elif token in self.vocabset:
                if self.count_index[token] >= self.min_count:
                    return self._vocab2idx[token]
                else:
                    return self._vocab2idx[self.unk_token]
            else:
                return self._vocab2idx[self.unk_token]
        except KeyError:
            raise KeyError, "Unable to determine index for unkown token '{}' since vocab was init without an UNK token".format(
                token)

    def token(self, idx):
        """ Return the token corresponding to the input index `idx`.

        If the index is not in the vocabulary, or it is the index
        of a token that has not been seen `min_count` times,
        the UNK token is returned instead
        """
        if idx in self.idxset:
            token = self._idx2vocab[idx]
            if self.count_index[token] >= self.min_count:
                return token
            else:
                return self.unk_token
        else:
            return self.unk_token

    def seq2idx(self, token_sequence, as_array=False):
        """ Convert sequence of tokens to list of indices """
        ret = [ self.idx(token) for token in token_sequence ]
        return np.array(ret) if as_array else ret

    def seqs2idx(self, token_sequences, as_array=False):
        """ Convert sequence of sequence of tokens to list of list of indices """
        ret = [ self.seq2idx(token_seq, as_array=as_array) for token_seq in token_sequences ]
        return np.array(ret) if as_array else ret

    def seq2token(self, idx_sequence, as_array=False):
        """ Convert sequence of indices to list of tokens """
        ret = [ self.token(idx) for idx in idx_sequence ]
        return np.array(ret) if as_array else ret

    def seqs2token(self, idx_sequences, as_array=False):
        """ Convert sequence of sequence of indices to list of list of tokens """
        ret = [ self.seq2token(idx_seq, as_array=as_array) for idx_seq in idx_sequences ]
        return np.array(ret) if as_array else ret

    def _init_maps(self):
        self._vocab2idx, self._idx2vocab = {}, {}
        if self.pad_token:
            self._vocab2idx.update({self.pad_token:0})
            self._idx2vocab.update({0:self.pad_token})
        if self.unk_token:
            i = len(self._vocab2idx) # see if we added the pad
            self._vocab2idx.update({self.unk_token:i})
            self._idx2vocab.update({i:self.unk_token})

    def use(self, tokens):
        """ Create the vocabulary, using these tokens.

        This method will reset the vocab with these tokens.

        NOTE: `tokens` is expected to be a flat list.
        """
        self.count_index = Counter()
        self._init_maps()
        if tokens:
            self.add(tokens)

    def add(self, tokens):
        """ Add these tokens to the vocabulary.

        This can be used iteratively, adding, say, one sentence at a time.

        NOTE: `tokens` is expected to be a flat list.
        """
        # increment counts of tokens seen here
        for token in tokens:
            self.count_index[token] += 1

        # add tokens to the vocabulary if they are new
        token_set = set(tokens)
        for token in token_set:
            if token not in self._vocab2idx:
                new_idx = len(self._vocab2idx)
                self._vocab2idx[token] = new_idx
                self._idx2vocab[new_idx] = token

        # now precompute commonly used properties of the vocab (ignoring infrequent tokens)
        self.vocabset = set([ token for (token, count) in self.count_index.most_common()
                              if count >= self.min_count ])
        if self.pad_token: self.vocabset.add(self.pad_token)
        if self.unk_token: self.vocabset.add(self.unk_token)
        self.idxset = set([ self._vocab2idx[token] for token in self.vocabset ])
        self._n = sum( count for count in self.count_index.values() if count >= self.min_count )
        self._v = sum( 1 for count in self.count_index.values() if count >= self.min_count )
        if self.pad_token: self._v += 1
        if self.unk_token: self._v += 1

    def drop_infrequent(self):
        """ Drop all words from the vocabulary that have not been seen `min_count` times
        and recompute the vocabulary indices.

        This is useful for when the vocab has a long tail of infrequent words
        that we no longer wish to account for.

        NOTE: This changes indices of tokens in the vocab!
        """
        # remove all infrequent tokens from the count index
        to_remove = set(self.count_index.keys()) - self.vocabset
        for token in to_remove:
            self.count_index.pop(token)

        # now reset the vocab dicts and reindex the tokens
        self._init_maps()
        for token in sorted(self.count_index.keys()): # make it deterministic
            new_idx = len(self._vocab2idx)
            self._vocab2idx[token] = new_idx
            self._idx2vocab[new_idx] = token

        # precompute commonly used properties of the vocab
        self.vocabset = set(self._vocab2idx.keys())
        self.idxset = set(self._idx2vocab.keys())
        self._n = sum( count for count in self.count_index.values() )
        self._v = len(self._vocab2idx)

    def count(self, token):
        """ Get the count of a token.

        This includes tokens with countes below `min_count`,
        which have been seen but are not included in the vocab.
        """
        return self.count_index[token]

#     def make_sampling_table(self, power_scalar=.75):
#         # from 0 to V-1, get the frequency
#         self.vocab_distribution = np.array([ (self.count_index[self._idx2vocab[idx]]/float(self._n))**power_scalar
#                                     for idx in range(len(self.idxset))])
#         self.vocab_distribution /= np.sum(self.vocab_distribution).astype(np.float)

#     def sample(self, sample_shape):
#         # sample a tensor of indices
#         # by walking up the CDF
#         # setting each position to the index
#         # of the word which is the closest
#         # word with that CDF
#         sums = np.zeros(sample_shape)
#         rands = npr.uniform(size=sample_shape)
#         idxs = np.zeros(sample_shape)
#         for i in range(len(self.vocab_distribution)):
#             sums += self.vocab_distribution[i]
#             idxs[sums <= rands] = i
#         return idxs.astype(np.int)
