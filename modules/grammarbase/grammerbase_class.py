import json


class PhrasePattern(object):
    def __init__(self, phrase_type, core_word_index, features, freq, meaning, symbol=None, examples=None):
        self.phrase_type = phrase_type
        self.pos_tag = self.phrase_type
        self.core_word_index = core_word_index
        self.features = json.loads(features)
        self.freq = float(freq)
        self.meaning = meaning
        self.symbol = symbol
        if examples:
            self.examples = examples
        else:
            self.examples = None

    def __str__(self):
        return self.__repr__()

    # def __setitem__(self, k, v):
    #     self.k = v

    def __repr__(self):
        s = ""
        s += "features: %s" % (self.features)
        s += ", phrase_type: %s" % (self.phrase_type)
        s += ", freq: %s" % (self.freq)
        s += ", meaning: %s" % (self.meaning)
        s += ", symbol: %s" % (self.symbol)
        s += ", examples: %s" % (self.examples)
        return s


class SubSentencePattern(object):
    def __init__(self, parse_str, freq, ss_type, meaning, ss_type2, examples=None):
        self.parse_str = parse_str
        self.freq = float(freq)
        self.ss_type = ss_type
        self.meaning = meaning
        self.ss_type2 = ss_type2
        if examples:
            self.examples = examples
        else:
            self.examples = None
