import os
import re

from tensorflow.python.platform import gfile
import tensorflow as tf

class DataUtils():


    def __init__(self, from_train_file='data/train.en',
                 from_vocab_file='data/vocab.en',
                 to_train_file='data/train.vi',
                 to_vocab_file='data/vocab.vi',
                 from_dev_file='data/tst2012.en',
                 to_dev_file='data/tst2012.vi',
                 from_test_file='data/tst2013.en',
                 to_test_file='data/tst2013.vi'):

        # Do we need these?
        self._PAD = b"_PAD"
        self._GO = b"_GO"
        self._EOS = b"_EOS"
        self._UNK = b"_UNK"
        self._START_VOCAB = [_PAD, _GO, _EOS, _UNK]

        self.PAD_ID = 0
        self.GO_ID = 1
        self.EOS_ID = 2
        self.UNK_ID = 3

        self.from_train_file   = from_train_file
        self.source_vocab_file = from_vocab_file
        self.to_train_file     = to_train_file
        self.to_vocab_file     = to_vocab_file
        self.from_dev_file     = from_dev_file
        self.to_dev_file       = to_dev_file
        self.from_test_file    = from_test_file
        self.to_test_file      = to_test_file

        vocab, rev_vocab = self.initialize_vocabulary(from_train_file)
        self.en_vocab_from_train = vocab
        self.en_rev_vocab_from_train = rev_vocab

        vocab, rev_vocab = self.initialize_vocabulary(to_train_file)
        self.en_vocab_to_train = vocab
        self.en_vocab_to_train = rev_vocab

        vocab, rev_vocab = self.initialize_vocabulary(from_dev_file)
        self.en_vocab_from_dev = vocab
        self.en_rev_vocab_from_dev = rev_vocab

        vocab, rev_vocab = self.initialize_vocabulary(to_dev_file)
        self.en_vocab_to_dev = vocab
        self.en_vocab_to_dev = rev_vocab

        vocab, rev_vocab = self.initialize_vocabulary(from_test_file)
        self.en_vocab_from_dev = vocab
        self.en_rev_vocab_from_dev = rev_vocab

        vocab, rev_vocab = self.initialize_vocabulary(to_test_file)
        self.en_vocab_to_test = vocab
        self.en_vocab_to_test = rev_vocab


# Regular expressions used to tokenize.
_WORD_SPLIT = re.compile(b"([.,!?\"':;)(])")
_DIGIT_RE = re.compile(br"\d")

    def initialize_vocabulary(self, vocabulary_path):
        print("called initialize_vocabulary method")
        if gfile.Exists(vocabulary_path):
            rev_vocab = []
            with gfile.GFile(vocabulary_path, "rb") as f:
                rev_vocab.extend(f.readlines())
            rev_vocab = [tf.compat.as_bytes(line.strip()) for line in rev_vocab]
            vocab = dict([x,y] for (y,x) in enumerate(rev_vocab))
            return vocab, rev_vocab
        else:
            raise ValueError("Vocabulary file %s not found", vocabulary_path)

    # Rewrote basic_tokenizer
    def basic_tokenizer(sentence):
        return [z.strip() for z in sent.split(" ")]

    # removed other tokenizer option
    def sentence_to_token_ids(sentence, vocabulary_path, normalize_digits=True):
        print "1"
        vocabulary, _ = self.initialize_vocabulary(vocabulary_path)
        print "2"
        words = self.basic_tokenizer(sentence)
        print "3"
        if not normalize_digits:
            return [vocabulary.get(w, self.UNK_ID) for w in words]

        # Normalize digits by 0 before looking words up in the vocabulary.
        return [vocabulary.get(self._DIGIT_RE.sub(b"0", w), UNK_ID) for w in words]

    def data_to_token_ids(data_path, target_path, vocabulary_path,
                      tokenizer=None, normalize_digits=True):
        if not gfile.Exists(target_path):
            print("Tokenizing data in %s" % data_path)
        vocab, _ = initialize_vocabulary(vocabulary_path)
        with gfile.GFile(data_path, mode="rb") as data_file:
            with gfile.GFile(target_path, mode="w") as tokens_file:
                counter = 0
                for line in data_file:
                    counter += 1
                    if counter % 100000 == 0:
                        print("  tokenizing line %d" % counter)
                    token_ids = sentence_to_token_ids(tf.compat.as_bytes(line), vocab,
                                                tokenizer, normalize_digits)
                tokens_file.write(" ".join([str(tok) for tok in token_ids]) + "\n")

    def prepare_data(data_dir, from_train_path, to_train_path, from_dev_path, to_dev_path, from_vocabulary_size,
                 to_vocabulary_size, tokenizer=None):

        # Create token ids for the training data.
        to_train_ids_path = to_train_path + (".ids%d" % to_vocabulary_size)
        from_train_ids_path = from_train_path + (".ids%d" % from_vocabulary_size)
        data_to_token_ids(to_train_path, to_train_ids_path, to_vocab_path, tokenizer)
        data_to_token_ids(from_train_path, from_train_ids_path, from_vocab_path, tokenizer)

        # Create token ids for the development data.
        to_dev_ids_path = to_dev_path + (".ids%d" % to_vocabulary_size)
        from_dev_ids_path = from_dev_path + (".ids%d" % from_vocabulary_size)
        data_to_token_ids(to_dev_path, to_dev_ids_path, to_vocab_path, tokenizer)
        data_to_token_ids(from_dev_path, from_dev_ids_path, from_vocab_path, tokenizer)

        return (from_train_ids_path, to_train_ids_path,
              from_dev_ids_path, to_dev_ids_path,
              from_vocab_path, to_vocab_path)

if __name__ == "__main__":
    du = DataUtils()
