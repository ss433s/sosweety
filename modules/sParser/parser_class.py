import json


# parse result类
class ParseResult(object):
    def __init__(self, contents):
        self.contents = contents
        self.pos_tags = [i.pos_tag for i in self.contents]
        self.words = [i.value for i in self.contents]
        self.parse_str = "|".join(self.pos_tags)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        s = ""
        # s += "words: %s" % (self.words)
        # s += ", pos_tags: %s" % (self.pos_tags)
        s += "\"content: %s\"" % (self.contents)
        return s


# 单词类 value为字面， pos_tag为词性
class Word(object):
    def __init__(self, value, pos_tag, pos_tag2=None):
        self.value = value
        self.pos_tag = pos_tag if pos_tag != 'SP' else value
        # self.pos_tag = pos_tag
        self.core_word = self.value
        if pos_tag2:
            self.pos_tag2 = pos_tag2

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        s = ""
        s += "word: %s" % (self.value)
        s += ", pos_tag: %s" % (self.pos_tag)
        # s += ", parse_str: %s" % (self.parse_str)
        return s


# Phrase pattern 挪到gb去了
# class PhrasePattern(object):
#     def __init__(self, phrase_type, core_word_index, features, freq, meaning, symbol=None, examples=None):
#         self.phrase_type = phrase_type
#         self.pos_tag = self.phrase_type
#         self.core_word_index = core_word_index
#         self.features = json.loads(features)
#         self.freq = float(freq)
#         self.meaning = meaning
#         self.symbol = symbol
#         if examples:
#             self.examples = examples
#         else:
#             self.examples = None

#     def __str__(self):
#         return self.__repr__()

#     # def __setitem__(self, k, v):
#     #     self.k = v

#     def __repr__(self):
#         s = ""
#         s += "features: %s" % (self.features)
#         s += ", phrase_type: %s" % (self.phrase_type)
#         s += ", freq: %s" % (self.freq)
#         s += ", meaning: %s" % (self.meaning)
#         s += ", symbol: %s" % (self.symbol)
#         s += ", examples: %s" % (self.examples)
#         return s


class Phrase(object):
    def __init__(self, phrase_pattern, contents):
        self.contents = contents
        self.phrase_type = phrase_pattern.phrase_type
        self.features = phrase_pattern.features
        self.pos_tag = self.phrase_type
        self.core_word_index = phrase_pattern.core_word_index
        self.freq = phrase_pattern.freq
        self.meaning = phrase_pattern.meaning
        self.words = [content.value for content in self.contents]
        self.value = "".join(self.words)
        if self.core_word_index == '-':
            self.core_word = self.value
        else:
            core_word_item = self.contents[int(self.core_word_index)]
            if not isinstance(core_word_item, Word):
                self.core_word = core_word_item.core_word
            else:
                self.core_word = core_word_item.value

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        s = ""
        # s += "words: %s" % (self.words)
        s += "phrase_type: %s" % (self.phrase_type)
        s += ", freq: %s" % (self.freq)
        s += ", meaning: %s" % (self.meaning)
        s += ", features: %s" % (self.features)
        s += ", contents: %s" % (self.contents)
        return s


'''
# Special pattern和Phrase类 特殊短语 合并进phrase了
class SpecialPattern(object):
    def __init__(self, phrase_type, pos_tag, core_word_index, features, freq, meaning, symbol=None, examples=None):
        self.phrase_type = phrase_type
        self.pos_tag = self.phrase_type
        self.core_word_index = core_word_index
        self.features = json.loads(features)
        self.freq = float(freq)
        self.meaning = meaning
        self.symbol = symbol
        if examples:
            self.examples = json.loads(examples)
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


# Special pattern的实例，有具体的词语内容
class SpecialPhrase(object):
    def __init__(self, phrase_pattern, contents):
        self.contents = contents
        self.phrase_type = phrase_pattern.phrase_type
        self.features = phrase_pattern.features
        self.pos_tag = self.phrase_type
        self.core_word_index = phrase_pattern.core_word_index
        self.freq = phrase_pattern.freq
        self.meaning = phrase_pattern.meaning
        self.words = [content.value for content in self.contents]
        self.value = "".join(self.words)
        if self.core_word_index == '-':
            self.core_word = self.value
        else:
            self.core_word = self.words[int(self.core_word_index)]

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        s = ""
        # s += "words: %s" % (self.words)
        s += "phrase_type: %s" % (self.phrase_type)
        s += ", freq: %s" % (self.freq)
        s += ", meaning: %s" % (self.meaning)
        s += ", features: %s" % (self.features)
        s += ", contents: %s" % (self.contents)
        return s
'''


# 挪到gb去了
# class SubSentencePattern(object):
#     def __init__(self, parse_str, freq, ss_type, meaning):
#         self.parse_str = parse_str
#         self.freq = float(freq)
#         self.ss_type = ss_type
#         self.meaning = meaning


# sub sentence  pre是临时存储用的，只有字符串，可以根据标点符号给出type
class SubSentence(object):
    def __init__(self, ss_pattern, contents):
        self.parse_str = ss_pattern.parse_str
        self.freq = ss_pattern.freq
        self.ss_type = ss_pattern.ss_type
        self.meaning = ss_pattern.meaning
        self.contents = contents

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        s = "\n"
        s += "parse_str: %s,\n" % (self.parse_str)
        s += "ss_type: %s,\n" % (self.ss_type)
        s += "freq: %s,\n" % (self.freq)
        s += "meaning: %s,\n" % (self.meaning)

#         def iter_one_level(contents):
#             has_phrase = False
#             value_list = []
#             phrase_list = []
#             for item in contents:
#                 value_list.append(item.value)
#                 if not type(item).__name__ == 'Word':
#                     has_phrase = True
#                     phrase_list.append(item)
#             print('     '.join(value_list))
#             return has_phrase, phrase_list, value_list

#         level_maxtrix = {}
#         level = 0
#         seq = 0
#         matrix_x = 0
#         matrix_y = 0
#         has_phrase = True
#         contents = self.contents
#         bottom_level_x = [i for i in range(len(contents))]
#         level_maxtrix.append(bottom_level_x)
#         while has_phrase:
#             this_level_x = level_maxtrix[level]
#             for i in range(len(contents)):
#                 item = contents[i]
#                 if not type(item).__name__ == 'Word':
#                     this_level_x[i] += len(contents)/2 - 0.5
#                     if i < len(contents):
#                         for j in range(i+1, len(contents)):
#                             this_level_x[j] += len(item)

#             this_level_has_phrase, this_level_phrase_list, this_level_value_list = iter_one_level(contents)
#             level_maxtrix[level] = this_level_value_list
#             level += 1
#             if this_level_has_phrase:
#                 for contents in this_level_phrase_list:

        level_list = []
        has_phrase = True
        contents_list = [self.contents]
        while has_phrase:
            this_level_value_list = []
            next_level_content_list = []
            has_not_phrase_list = []
            for contents in contents_list:
                contents_has_not_phrase = all([type(item).__name__ == 'Word' for item in contents])
                has_not_phrase_list.append(contents_has_not_phrase)
                this_level_value_list += [item.value for item in contents]
                for item in contents:
                    if not type(item).__name__ == 'Word':
                        next_level_content_list.append(item.contents)
            level_list.append(this_level_value_list)
            contents_list = next_level_content_list
            has_phrase = not all(has_not_phrase_list)

        s += "contents: \n"
        for level in range(len(level_list)-1, -1, -1):
            s += json.dumps(level_list[level], ensure_ascii=False) + '\n'
        return s


class PreSubSentence(object):
    def __init__(self, value, ss_type=None, raw_parse_result=None):
        self.value = value
        self.ss_type = ss_type
        self.raw_parse_result = raw_parse_result
