import os, sys
import json
import time


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

from modules.utils.utils import count_value_with_examples, csv_to_xlsx
from modules.learning.phrase.p4_concept_and_upper_concept_finder import ConceptAndUpperConceptFinder
import csv


class NounPhraseFinder():
    def __init__(self, KB, multiprocess=1):
        self.KB = KB

    # input file 为每行一个parse result的json string
    def analyse(self, input_file_path, output_dir_path, cutoff=10):

        # prepare output dir
        noun_phrase_pattern_dir = os.path.join(output_dir_path, 'noun_phrase')
        if not os.path.exists(noun_phrase_pattern_dir):
            os.makedirs(noun_phrase_pattern_dir)
        concept_phrase_file_path = os.path.join(noun_phrase_pattern_dir, 'concept_phrases')
        self.checkout_noun_phrase_to_file(input_file_path, concept_phrase_file_path)
        ordered_stat_file_path = os.path.join(noun_phrase_pattern_dir, 'ordered_phrase_pattern.csv')
        ordered_stat_xls_file_path = os.path.join(noun_phrase_pattern_dir, 'ordered_phrase_pattern.xlsx')
        count_value_with_examples(concept_phrase_file_path, ordered_stat_file_path, cutoff=cutoff)

        # stat file with example to phrase pattern file
        tmp_file = os.path.join(noun_phrase_pattern_dir, 'tmp.csv')
        tmp_file_writer = csv.writer(open(tmp_file, 'w+', encoding='utf-8-sig'))
        tmp_file_writer.writerow(['pos_tag', 'core_word_index', 'features', 'freq', 'meaning', 'symbol', 'examples'])
        ordered_stat_file_reader = csv.reader(open(ordered_stat_file_path, encoding='utf-8-sig'))
        for row in ordered_stat_file_reader:
            tmp_file_writer.writerow(['', '', row[0], row[1], '', '', row[2]])
        csv_to_xlsx(tmp_file, ordered_stat_xls_file_path)
        # os.remove(tmp_file)

        # find new concept and new upper concept
        concept_and_upper_concept_finder = ConceptAndUpperConceptFinder(self.KB)
        concept_and_upper_concept_finder.analyse(ordered_stat_file_path)

        print('Noun phrase pattern analyse finished at:')
        print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))

        return

    def checkout_noun_phrase_to_file(self, input_file_path, output_file_path):

        # checkout all nouns
        print('Begin to checkout all nouns')
        print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))
        input_file = open(input_file_path)
        line = input_file.readline()
        noun_id_set = set()
        word2id_dict = {}
        count = 0
        while line:
            count += 1
            if count % 15000 == 0:
                print('count %s sentences' % count)
            line = line.strip()
            pos_tags = json.loads(line)
            for word, pos_tag in pos_tags:
                if pos_tag == 'NN' and word not in word2id_dict:
                    concept_ids = self.KB.get_word_ids(word, 0)
                    word2id_dict[word] = concept_ids
                    for concept_id in concept_ids:
                        noun_id_set.add(concept_id[0])

            line = input_file.readline()
        input_file.close()

        print('This corpus has %s nouns' % len(noun_id_set))
        print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))

        # 准备关系字典和上位词set
        relation_dict = {}
        all_upper_concepts_set = set()
        for concept_id in noun_id_set:
            next_level_concept_ids = self.KB.get_concept_upper_relations(concept_id)
            relation_dict[concept_id] = next_level_concept_ids
            for next_level_concept_id in next_level_concept_ids:
                all_upper_concepts_set.add(next_level_concept_id)

        # 准备所有的上位词的feature字典
        all_features = {}
        for concept_id in all_upper_concepts_set:
            feature = {}
            word = self.KB.get_concept_word(concept_id)
            feature['concept'] = concept_id
            feature['word'] = word
            all_features[concept_id] = feature

        print('This corpus has %s upper concepts' % len(all_upper_concepts_set))
        print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))

        # 强行遍历各种可能性2-3个词
        # 返回是 【phrase， example】 phrase是feature的list， example是word的list
        def checkout_concept_phrase(pos_tags):

            def create_features_for_item(item):

                # 当前词自身作为feature
                item_raw_feature = {'word': item[0]}
                item_all_features = [item_raw_feature]
                # 获取当前词对应的所有concept id
                item_concepts = word2id_dict[item[0]]
                # 获取当前词所有的上位feature
                for concept in item_concepts:
                    concept_id = concept[0]
                    # 这个concept id 有上位关系
                    if concept_id in relation_dict:
                        # 将所有上位关系加入item_all_features
                        upper_concepts = relation_dict[concept_id]
                        for upper_concept in upper_concepts:
                            item_all_features.append(all_features[upper_concept])
                return item_all_features

            concept_phrases = []
            for i in range(len(pos_tags)-1):
                item = pos_tags[i]
                next_item = pos_tags[i+1]
                if item[1] == 'NN' and next_item[1] == 'NN':
                    item_concept_phrases = []
                    # 获取两个词的所有feature
                    item_all_features = create_features_for_item(item)
                    next_item_all_features = create_features_for_item(next_item)
                    # 交叉组合所有feature
                    for feature1 in item_all_features:
                        for feature2 in next_item_all_features:
                            item_concept_phrases.append([[feature1, feature2], [item[0], next_item[0]]])

                    concept_phrases += item_concept_phrases

                    if i < len(pos_tags) - 2:
                        next_next_item = pos_tags[i+2]
                        if next_next_item[1] == 'NN':
                            next_next_item_all_features = create_features_for_item(next_next_item)
                            for phrase, example in item_concept_phrases:
                                for feature3 in next_next_item_all_features:
                                    phrase3 = phrase + [feature3]
                                    example3 = example + [next_next_item[0]]
                                    concept_phrases.append([phrase3, example3])
            return concept_phrases

        # 找phrase, 同时写入文件
        input_file = open(input_file_path)
        line = input_file.readline()
        with open(output_file_path, 'w') as concept_phrase_file:
            count = 0
            while line:
                count += 1
                if count % 15000 == 0:
                    print('check %s sentences' % count)
                line = line.strip()
                pos_tags = json.loads(line)
                concept_phrases = checkout_concept_phrase(pos_tags)
                for concept_phrase, phrase_example in concept_phrases:
                    # todo 改成csv
                    concept_phrase_file.write((json.dumps(concept_phrase, ensure_ascii=False) + '\t' + json.dumps(phrase_example, ensure_ascii=False) + '\n'))

                line = input_file.readline()

        print('Checkout concept phrases finished at:')
        print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))

        return
