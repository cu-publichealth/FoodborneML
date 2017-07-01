""" Load in word vectors from a GloVe/word2vec style files
and return an embedding matrix using a vocab object from vocab.py.

NOTE: make sure to call this after dropping infrequent words, if needed.
"""
import numpy as np
import numpy.random as npr

def get_pretrained_vectors(vocab, vec_fname, normed=True, trim=False):
    """ Generate embedding matrix according to idx mapping from vocab.

    Args:
      vocab (Vocab): vocab object containing all tokens to look up vectors for
      vec_fname (str): file path to the word vectors as a text doc
      normed (bool:True): whether or not to normalize the embeddings
      trim (bool:False): If true, a trimmed down version of the vector file,
        matching only the vocab will be output as a side effect for future use.

    Returns:
      e (np.array): float 32 matrix of embeddings, matching indices from vocab
    """
    # load in vectors in vocab
    token2vec = {}
    if trim:
        trim_fname = '/'.join(vec_fname.split('/')[:-1]+['trimmed_'+vec_fname.split('/')[-1]])
        trim_f = open(trim_fname, 'w')
    for line in open(vec_fname, 'r'):
        if line: # sometime they're empty
            split = line.split()
            token, vec = split[0], np.array([float(s) for s in split[1:]], dtype=np.float32)
            if token in vocab.vocabset:
                token2vec[token] = vec
                if trim:
                    trim_f.write(line)
    if trim:
        trim_f.close()

    # put them in a matrix
    d = token2vec.values()[0].shape[0]
    e = npr.normal(size=(vocab.v, d))
    for token, vec in token2vec.items():
        e[vocab.idx(token), :] = vec/np.linalg.norm(vec) if normed else vec
    # set the pad embedding to zeros if we have one
    if vocab.pad_token:
        print 'Setting pad token to have a zeros embeddings'
        e[vocab.ipad,:] = np.zeros(e.shape[1])
    print "Pretrained coverage: {0}/{1} = {2:2.2f}%".format(
        len(token2vec), vocab.v, float(len(token2vec))/vocab.v * 100.)
    return e
