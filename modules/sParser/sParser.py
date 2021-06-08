import re, argparse
# import regex as re2
import jieba
import jieba.posseg
import time
# import ahocorasick
from pyhanlp import HanLP
import os, sys
# import pandas as pd

# 获取当前路径， 通过anchor文件获取项目root路径
this_file_path = os.path.split(os.path.realpath(__file__))[0]
this_path = this_file_path
root_path = this_file_path
while this_path:
    if os.path.exists(os.path.join(this_path, 'sosweety_root_anchor.py')):
        root_path = this_path
        break
    par_path = os.path.dirname(this_path)
    # print(par_path)
    if par_path == this_path:
        break
    else:
        this_path = par_path
sys.path.append(root_path)

from modules.knowledgebase.kb import KnowledgeBase
from modules.grammarbase.grammarbase import GrammarBase
from modules.sParser.parser_class import ParseResult, Word, Phrase, SubSentence, PreSubSentence
from modules.utils.utils import hanlp_simplify, jieba_simplify


###################
# sParser类 通用parser
###################
class sParser(object):
    def __init__(self, KB, mode='default', current_environment=None):
        self.mode = mode
        self.KB = KB
        self.GB = GrammarBase()
        self.current_environment = current_environment
        self.total_count = 0

    ###################
    # 主函数
    ###################
    def parse(self, text):

        result = {}
        result['parse_results'] = []
        result['k_points'] = []

        # 1，判定文本类型。对话/新闻稿/公告 等。可自动发现，自动学习
        # to do

        # 2，分句。
        # to do 优化分句
        sentences = self.cut_sent(text)

        # 3，逐句parse
        for sentence in sentences:
            # 分句的句号处理 可以直接进行分类
            # to do
            sentence = re.sub('([。！？\?])', '', sentence)
            sub_sentences = self.seg2sub_sentence(sentence)

            for sub_sentence in sub_sentences:
                # print(sub_sentence.value)
                if isinstance(sub_sentence, PreSubSentence):
                    print(sub_sentence.value)
                    # if self.mode == 'special1':  # 专门处理百度信息抽取预处理好的语料

                    parse_result = self.hanlp_parse(sub_sentence.value)
                    sub_sentence.raw_parse_result = parse_result

                    # # 遍历版
                    # all_results = []
                    # check_phrase(parse_result, all_results)

                    # 快速版
                    all_results = self.fast_check_phrase(parse_result)

                    # 返回所有results
                    if self.mode == 'default':
                        ss_result = all_results
                        result['parse_results'].append(ss_result)
                    # 返回最高分result
                    # if self.mode == 'learning':
                    #     final_result_score = 0
                    #     ss_result = []
                    #     for parse_result in all_results:
                    #         score = cal_score(parse_result)
                    #         if score > final_result_score:
                    #             ss_result = parse_result
                    #     if ss_result == []:
                    #         result['parse_results'].append(sub_sentence)  # 无解析结果返回原始的 PreSubSentence
                    #     else:
                    #         result['parse_results'].append(ss_result)  # 有解析结果返回SubSentence
                else:
                    result['parse_results'].append(sub_sentence)

        return result

    def text2ss_pos_tags(self, text, parser='hanlp'):
        sentences = self.cut_sent(text)
        ss_pos_tags = []
        for sentence in sentences:
            pos_tags = []

            if parser == 'hanlp':
                ha_parse_result = HanLP.parseDependency(sentence)
                # print(ha_parse_result)
                for i in ha_parse_result.word:
                    pos_tags.append([i.LEMMA, i.CPOSTAG])
                pos_tags = hanlp_simplify(pos_tags)

            if parser == 'jieba':
                dict_file = os.path.join(root_path, 'modules/utils/dict.txt')
                jieba.load_userdict(dict_file)
                parse_result = jieba.posseg.cut(text)
                for word, flag in parse_result:
                    pos_tags.append([word, flag])
                pos_tags = jieba_simplify(pos_tags)

            tmp_stamp = 0
            for i in range(len(pos_tags)):
                pos_tag = pos_tags[i]
                if pos_tag[0] in ['。', '！', '？', '?', '，', ',', ';', '；']:
                    ss_pos_tags.append(pos_tags[tmp_stamp: i])
                    tmp_stamp = i + 1
            if tmp_stamp < len(pos_tags):
                ss_pos_tags.append(pos_tags[tmp_stamp: len(pos_tags)])

        return ss_pos_tags

    ###################
    # 分句
    # todo 引号破折号等，引号纠错
    ###################
    def seg2sentence(self, paragraph):
        sentences = re.split('(。|！|\!|\.|？|\?)', paragraph)
        new_sents = []
        for i in range(int(len(sentences) / 2)):
            if 2 * i + 1 < len(sentences):
                sent = sentences[2 * i] + sentences[2 * i + 1]
            else:
                sent = sentences[2 * i]
            new_sents.append(sent)
        return new_sents

    def cut_sent(self, paragraph):
        paragraph = re.sub('([。！？\?])([^”’])', r"\1\n\2", paragraph)  # 单字符断句符
        paragraph = re.sub('(\.{6})([^”’])', r"\1\n\2", paragraph)  # 英文省略号
        paragraph = re.sub('(\…{2})([^”’])', r"\1\n\2", paragraph)  # 中文省略号
        paragraph = re.sub('([。！？\?][”’])([^，。！？\?])', r'\1\n\2', paragraph)
        # 如果双引号前有终止符，那么双引号才是句子的终点，把分句符\n放到双引号后，注意前面的几句都小心保留了双引号
        paragraph = paragraph.rstrip()  # 段尾如果有多余的\n就去掉它
        # 很多规则中会考虑分号;，但是这里我把它忽略不计，破折号、英文双引号等同样忽略，需要的再做些简单调整即可。
        return paragraph.split("\n")

    ###################
    # 拆分子句
    # todo 引号破折号等，引号纠错 小数点处理
    ###################
    def seg2sub_sentence(self, sentence):
        sub_sentences = re.split('(，|,|;|；)', sentence)
        new_sub_sents = []
        for i in range(len(sub_sentences)):
            if i % 2 == 0:
                sub_sent = PreSubSentence(sub_sentences[i])
            else:
                sub_sent = Word(sub_sentences[i], 'PU')
            new_sub_sents.append(sub_sent)
        return new_sub_sents

    ###################
    # 词组检测
    # 构建所有可能的词组组合
    ###################
    # 快速检测，直接递进到无phrase，不遍历所有可能组合
    def fast_check_parse_result(self, parse_result):
        no_more_phrase = False
        new_parse_result = parse_result
        while not no_more_phrase:
            this_time_no_more_phrase = True
            for phrase_pattern in self.GB.phrase_patterns:
                results = self.find_single_phrase_pattern(new_parse_result, phrase_pattern)
                if len(results) > 0:
                    this_time_no_more_phrase = False
                    new_parse_result = results[0]
                    break
            if this_time_no_more_phrase:
                no_more_phrase = this_time_no_more_phrase
        if no_more_phrase:
            return new_parse_result

    def fast_check_phrase(self, parse_result):
        final_results = []
        parse_results = [parse_result]
        parse_results.append(self.fast_known_entity_check(parse_result))
        for new_parse_result in parse_results:
            new_parse_result = self.fast_check_parse_result(new_parse_result)
            matched_ss_pattern = self.check_ss_pattern(new_parse_result)
            if len(matched_ss_pattern) > 0:
                for ss_pattern in matched_ss_pattern:
                    ss = SubSentence(ss_pattern, new_parse_result.contents)
                    final_results.append(ss)
        return final_results

    # todo 遍历式known entity check
    def check_phrase_with_known_entity(self, parse_result):
        final_results = []
        parse_results = [parse_result]
        parse_results.append(self.fast_known_entity_check(parse_result))
        for new_parse_result in parse_results:
            # print(self.total_count)
            start_time = time.time()
            self.check_phrase(new_parse_result, final_results, start_time=start_time)
        # print(self.total_count)
        return final_results

    # 先focus关键词构建句子主框架
    # todo 可以先剔除《》，（）
    # todo 重分词时更有意义
    # todo 三国演义写曹操统一北方的故事 怎么解
    # todo 三国演义写故事 -> 曹操统一北方的故事 -> ss的故事  写能接ss吗？ if能，此句有歧义 （汤显祖写牡丹亭）的故事 汤显祖写(牡丹亭的故事)
    def check_phrase_with_attention(self, parse_result):
        verb_list = []
        for item in parse_result.contents:
            if item.pos_tag == 'VV':
                verb_list.append(item)
        final_results = []
        parse_results = [parse_result]
        parse_results.append(self.fast_known_entity_check(parse_result))
        for new_parse_result in parse_results:
            # print(self.total_count)
            start_time = time.time()
            self.check_phrase(new_parse_result, final_results, start_time=start_time)
        # print(self.total_count)
        return final_results

    # 遍历所有可能组合，耗时过多
    def check_phrase(self, parse_result, final_results, mode='default', N=0, start_time=None):
        not_done = []
        final_results_str = [str(final_result) for final_result in final_results]

        # 自身就在ss_pattern中
        # self.total_count += 1
        matched_ss_pattern = self.check_ss_pattern(parse_result)
        if len(matched_ss_pattern) > 0:
            for ss_pattern in matched_ss_pattern:
                ss = SubSentence(ss_pattern, parse_result.contents)
                # todo 有可能有ss_str相同 但结构不同的情况出现
                if str(ss) not in final_results_str:
                    final_results.append(ss)
                    final_results_str.append(str(ss))

        # 替换phrase后在ss_pattern中
        for i in range(len(self.GB.phrase_patterns)):
            phrase_pattern = self.GB.phrase_patterns[i]
            # if i % 10 == 0:
            #     print(i, N)
            new_parse_results = self.find_single_phrase_pattern(parse_result, phrase_pattern)
            not_done.append(len(new_parse_results) == 0)
            for new_parse_result in new_parse_results:
                if phrase_pattern.symbol == 'VV|NN|DEG|NN':
                    print('11')
                    pass
                matched_ss_pattern = self.check_ss_pattern(new_parse_result)
                # self.total_count += 1
                if len(matched_ss_pattern) > 0:
                    for ss_pattern in matched_ss_pattern:
                        ss = SubSentence(ss_pattern, new_parse_result.contents)
                        if str(ss) not in final_results_str:
                            final_results.append(ss)
                            final_results_str.append(str(ss))

                    # 初始化时开启这句，找到就退出循环
                    if mode == 'init':
                        break

                if mode == 'init' and len(final_results) > 0:
                    break
                # if N < 5:
                if start_time is not None and time.time() - start_time < 30:
                    self.check_phrase(new_parse_result, final_results, mode, N + 1, start_time)

                # 不给start time就无限找下去
                if start_time is None:
                    self.check_phrase(new_parse_result, final_results, mode, N + 1, start_time)
        if all(not_done):
            return

    # 检测单个phrase pattern 在一份parse result中的所有位置
    def find_single_phrase_pattern(self, parse_result, phrase_pattern):

        def match_one_feature(parse_result_content, feature):
            result = False
            if list(feature.keys())[0] == 'concept':
                rst = self.KB.word_belong_to_concept(parse_result_content.core_word, feature['concept'])
                if len(rst) > 0:
                    result = True
            if list(feature.keys())[0] == 'word':
                if parse_result_content.value == feature['word']:
                    result = True
            if list(feature.keys())[0] == 'pos_tag':
                if parse_result_content.pos_tag == feature['pos_tag']:
                    result = True

            # 正则符合，需谨慎
            if list(feature.keys())[0] == 'special_symbol':
                if feature['special_symbol'] == '*':
                    result = True

            return result

        new_parse_results = []
        first_feature = phrase_pattern.features[0]

        # for j in range(len(parse_result.pos_tags) - len(special_pattern.features) + 1):
        #     if match_one_feature(parse_result.contents[j], first_feature):
        #         i = 1
        #         while len(parse_result.contents) > j + i and len(special_pattern.features) > i:
        #             if match_one_feature(parse_result.contents[j + i], special_pattern.features[i]):
        #                 i += 1
        #                 continue
        #             else:
        #                 break

        #         if i == len(special_pattern.features):
        #             new_parse_result_contents = parse_result.contents[0:j]
        #             contents = parse_result.contents[j: j + i]
        #             special_phrase = SpecialPhrase(special_pattern, contents)
        #             new_parse_result_contents.append(special_phrase)
        #             if j + i < len(parse_result.contents):
        #                 new_parse_result_contents += parse_result.contents[j + i: len(parse_result.contents)]
        #             new_parse_result = ParseResult(new_parse_result_contents)
        #             new_parse_results.append(new_parse_result)
        # return new_parse_results

        # 目前限制很多，只识别*且*至少一个,且*不能在开头和结尾
        for j in range(len(parse_result.pos_tags) - len(phrase_pattern.features) + 1):
            if match_one_feature(parse_result.contents[j], first_feature):
                # 确定是否包含特殊feature
                pattern_contain_special = False
                for feature in phrase_pattern.features:
                    if 'special_symbol' in feature:
                        pattern_contain_special = True
                        break

                # 有*
                if pattern_contain_special:
                    full_match = False
                    i = 1
                    while len(parse_result.contents) > j + i and len(phrase_pattern.features) > i:
                        current_feature = phrase_pattern.features[i]
                        if match_one_feature(parse_result.contents[j + i], current_feature):
                            if 'special_symbol' in current_feature and current_feature['special_symbol'] == '*':
                                next_feature = phrase_pattern.features[i+1]
                                if match_one_feature(parse_result.contents[j + i + 1], next_feature):
                                    i += 2
                                    full_match = True
                                    break
                                else:
                                    for k in range(1, len(parse_result.contents) - j - i):
                                        if match_one_feature(parse_result.contents[j + i + k], next_feature):
                                            i += k + 1
                                            full_match = True
                                            break
                                    if full_match:
                                        break
                            i += 1
                        else:
                            break
                # 没有*
                else:
                    i = 1
                    while len(parse_result.contents) > j + i and len(phrase_pattern.features) > i:
                        if match_one_feature(parse_result.contents[j + i], phrase_pattern.features[i]):
                            i += 1
                            # continue
                        else:
                            break
                    full_match = i == len(phrase_pattern.features)

                if full_match:
                    new_parse_result_contents = parse_result.contents[0:j]
                    contents = parse_result.contents[j: j + i]
                    phrase = Phrase(phrase_pattern, contents)
                    new_parse_result_contents.append(phrase)
                    if j + i < len(parse_result.contents):
                        new_parse_result_contents += parse_result.contents[j + i: len(parse_result.contents)]
                    new_parse_result = ParseResult(new_parse_result_contents)
                    new_parse_results.append(new_parse_result)
        return new_parse_results

    # check_sub_sentence  返回所有匹配到的ss_pattern
    def check_ss_pattern(self, parse_result):
        result = []
        for ss_pattern in self.GB.ss_patterns:
            if parse_result.parse_str == ss_pattern.parse_str:
                result.append(ss_pattern)
        return result

    # 检测一个sub_sentence的meaning是否全部成立
    # 参数为一个sub_sentence
    # 返回结果是一个【Bool】的list，每一个值代表每一条meaning是否成立
    def logic_check(self, sub_sentence):
        logic_rules_check = []
        if sub_sentence.meaning != '-' and sub_sentence.meaning is not None:
            logic_rules = sub_sentence.meaning.split(',')
            for logic_rule in logic_rules:
                this_rule_check = False
                logic_rule = logic_rule.strip().split(':')
                # print(logic_rule)
                index1 = int(logic_rule[1])
                index2 = int(logic_rule[2])

                # 不同rules分别判定
                # dobj
                if logic_rule[0] == 'dobj':
                    verb = sub_sentence.contents[index1].core_word
                    obj = sub_sentence.contents[index2].core_word
                    verb_methods = self.KB.get_word_ids(verb, 1)
                    verb_objs = []
                    for method_id, _ in verb_methods:
                        verb_objs += self.KB.get_method_objs(method_id)
                    obj_concepts = self.KB.get_word_ids(obj, 0)
                    for concept_id, _ in obj_concepts:
                        if concept_id in verb_objs:
                            this_rule_check = True
                            break
                    logic_rules_check.append(this_rule_check)

                # subj
                if logic_rule[0] == 'nsubj':
                    subj = sub_sentence.contents[index1].core_word
                    verb = sub_sentence.contents[index2].core_word
                    subj_concepts = self.KB.get_word_ids(subj, 0)
                    subj_methods = []
                    for concept_id, _ in subj_concepts:
                        subj_methods += self.KB.get_concept_methods(concept_id)
                    verb_methods = self.KB.get_word_ids(verb, 1)
                    for method_id, _ in verb_methods:
                        if method_id in subj_methods:
                            this_rule_check = True
                            break
                    logic_rules_check.append(this_rule_check)
        return logic_rules_check

    # 检测是否存在已知实体，有的话，替换为普通NN
    def fast_known_entity_check(self, parse_result):
        no_more_entity = False
        new_parse_result = parse_result
        while not no_more_entity:
            this_time_no_more_entity = True
            for i in range(len(new_parse_result.contents)):
                max_length = 0
                this_item = new_parse_result.contents[i]
                word = this_item.value
                word_id = self.KB.get_word_ids(word, 0)
                if len(word_id) != 0:
                    max_length = 1
                    final_word = word
                new_word = word
                for j in range(4):
                    if i+j+1 < len(new_parse_result.contents):
                        new_word = new_word + new_parse_result.contents[i+j+1].value
                        word_id = self.KB.get_word_ids(new_word, 0)
                        if len(word_id) != 0:
                            max_length = j+2
                            final_word = new_word
                if max_length > 1:
                    new_parse_result_contents = new_parse_result.contents[0:i]
                    concept_word = Word(final_word, 'NN')
                    new_parse_result_contents.append(concept_word)
                    if max_length+i < len(new_parse_result.contents):
                        new_parse_result_contents += new_parse_result.contents[max_length+i: len(new_parse_result.contents)]
                    new_parse_result = ParseResult(new_parse_result_contents)
                    this_time_no_more_entity = False
                    break
            if this_time_no_more_entity:
                no_more_entity = this_time_no_more_entity
        return new_parse_result

    ###################
    # hanlp parse
    ###################
    # def hanlp_parse(self, text):
    #     ha2stanford_dict = {}
    #     with open('../utils/ha2stanford') as f:
    #         lines = f.readlines()
    #         for line in lines:
    #             line = line.strip().split('\t')
    #             ha2stanford_dict[line[0]] = line[1]
    #     ha_parse_result = HanLP.parseDependency(text)
    #     # print(ha_parse_result)
    #     words = []
    #     for i in ha_parse_result.word:
    #         word = Word(i.LEMMA, ha2stanford_dict[i.CPOSTAG], i.CPOSTAG)
    #         words.append(word)
    #     parse_result = ParseResult(words)
    #     return parse_result

    ###################
    # stanford parse
    ###################
    def stanford_parse(self, text):
        return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c",
                        "--corpus",
                        default="../data/corpus/train.txt",
                        help="corpus file folder for training",
                        required=False)
    args = parser.parse_args()

    KB = KnowledgeBase(memory_mode=False)
    # parse_result = hanlp_parse('纵横中文网。')
    # check_known_concepts(parse_result)

    text = '北京（中国的首都）是北京。'
    text = '宝马和奔驰联合开发无人驾驶技术'
    text = '北京是首都'

    # parser = sParser(KB, mode='learning')
    parser = sParser(KB)
    rst = parser.parse(text)
    print(rst)

'''
    # ################## old version #############
    ###################
    # 读取待处理语料，格式为每行一个数据，每个数据可以是多句话组成
    ###################
    try:
        corpus = open(args.corpus, 'r', encoding='utf-8')
    except Exception:
        corpus = open(args.corpus, 'r', encoding='gbk')

    line = corpus.readline()
    while line:
        line = line.strip()

        parser.parse(line)
        # 语料分句
        # sentences = seg2sentence(line)
        sentences = cut_sent(line)
        # CRFnewSegment_new = HanLP.newSegment("crf")
        # s = CRFnewSegment_new.seg2sentence(line)
        # print(line)
        # print(sentences)

        # 对句子进行parse
        # parse_result, clean_text, stanford_pos = hanlp_parse(line)
        # print(parse_result, clean_text, stanford_pos)
        # check_xps(parse_result)

        # 拆分子句
        for sentence in sentences:
            sentence = re.sub('([。！？\?])', '', sentence)
            sub_sentences = seg2sub_sentence(sentence)

            # parse
            # print(sub_sentences)
            # parse_result = hanlp_parse(line)

            # # find_single_special_pattern(parse_result, phrase_patterns[0])

            # final_results = []
            # check_special_phrase(parse_result, final_results)
            # print(len(final_results))
            # break
        # break
        line = corpus.readline()
    corpus.close()
'''
