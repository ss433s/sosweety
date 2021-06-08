# import time
import os, sys
import json
import csv

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

from modules.utils.utils import csv_to_xlsx


class ConceptAndUpperConceptFinder(object):
    def __init__(self, KB, multiprocess=1):
        self.KB = KB
        self.multiprocess = multiprocess

    def analyse(self, ordered_phrase_pattern_file_path, cutoff=2):
        analyse_result_dir = os.path.dirname(ordered_phrase_pattern_file_path)
        ordered_phrase_pattern_file = open(ordered_phrase_pattern_file_path)
        ordered_phrase_pattern_file_reader = csv.reader(ordered_phrase_pattern_file)

        # 找出所有feature都是word并且不在kb里的phrase，也就是新的概念
        new_concept_file_path = os.path.join(analyse_result_dir, 'new_concept.csv')
        new_concept_xls_file_path = os.path.join(analyse_result_dir, 'new_concept.xlsx')
        new_concept_file = open(new_concept_file_path, 'w', encoding='utf-8-sig')
        new_concept_file_writer = csv.writer(new_concept_file)

        line = ordered_phrase_pattern_file.readline()
        for line in ordered_phrase_pattern_file_reader:
            phrase_pattern = json.loads(line[0])
            all_item_is_word = True
            for item in phrase_pattern:
                if not (len(item.keys()) == 1 and 'word' in item):
                    all_item_is_word = False
            if all_item_is_word:
                # print(phrase_pattern)
                phrase_value = ''.join([x['word'] for x in phrase_pattern])
                word_id = self.KB.get_word_ids(phrase_value, 0)
                if len(word_id) == 0:
                    new_concept_file_writer.writerow([line[0], phrase_value, line[1], 0])

        new_concept_file.close()
        csv_to_xlsx(new_concept_file_path, new_concept_xls_file_path)

        # 从新概念中找出潜在的upper concept
        with open(new_concept_file_path, encoding='utf-8-sig') as new_concept_file:
            csv_reader = csv.reader(new_concept_file)
            high_freq_word_set = set()
            word2phrases_dict = {}
            phrase_pattern_freq_dict = {}
            for row in csv_reader:
                phrase_pattern = json.loads(row[0])
                phrase_pattern_freq_dict[row[0]] = int(row[2])
                for item in phrase_pattern:
                    word = item['word']
                    if word in word2phrases_dict:
                        word2phrases_dict[word].append(phrase_pattern)
                    else:
                        word2phrases_dict[word] = [phrase_pattern]
                    if len(word2phrases_dict[word]) > cutoff:
                        high_freq_word_set.add(word)

        new_upper_concept_with_example_dict = {}
        new_upper_concept_freq_dict = {}
        for high_freq_word in high_freq_word_set:
            word_site_dict = {}
            for phrase_pattern in word2phrases_dict[high_freq_word]:
                for i in range(len(phrase_pattern)):
                    item = phrase_pattern[i]
                    if item['word'] == high_freq_word:
                        word_site = str(i) + '_' + str(len(phrase_pattern))
                if word_site in word_site_dict:
                    word_site_dict[word_site].append(phrase_pattern)
                else:
                    word_site_dict[word_site] = [phrase_pattern]

            for word_site in word_site_dict:
                if len(word_site_dict[word_site]) >= cutoff:
                    word_site_split = word_site.split('_')
                    site = int(word_site_split[0])
                    phrase_length = int(word_site_split[1])

                    # todo 暂时只考虑2个词的
                    new_upper_concept_list = []
                    if site == 0 and phrase_length == 2:
                        new_upper_concept_list = [phrase_pattern[1]['word'] for phrase_pattern in word_site_dict[word_site]]
                        new_upper_concept_list.sort()
                        new_upper_concept_freq = sum([phrase_pattern_freq_dict[json.dumps(phrase_pattern, ensure_ascii=False)] for phrase_pattern in word_site_dict[word_site]])
                    if site == 1 and phrase_length == 2:
                        new_upper_concept_list = [phrase_pattern[0]['word'] for phrase_pattern in word_site_dict[word_site]]
                        new_upper_concept_list.sort()
                        new_upper_concept_freq = sum([phrase_pattern_freq_dict[json.dumps(phrase_pattern, ensure_ascii=False)] for phrase_pattern in word_site_dict[word_site]])

                    if new_upper_concept_list != []:
                        new_upper_concept = '|'.join(new_upper_concept_list)
                        phrase_example = word_site_dict[word_site][0]
                        # 同一个concept可以通过不同的关联词找到
                        if new_upper_concept in new_upper_concept_with_example_dict:
                            new_upper_concept_with_example_dict[new_upper_concept].append(phrase_example)
                            new_upper_concept_freq_dict[new_upper_concept] += new_upper_concept_freq
                        else:
                            new_upper_concept_with_example_dict[new_upper_concept] = [phrase_example]
                            new_upper_concept_freq_dict[new_upper_concept] = new_upper_concept_freq

        new_upper_concept_file_path = os.path.join(analyse_result_dir, 'new_upper_concept.csv')
        new_upper_concept_xls_file_path = os.path.join(analyse_result_dir, 'new_upper_concept.xlsx')
        new_upper_concept_file = open(new_upper_concept_file_path, 'w', encoding='utf-8-sig')
        new_upper_concept_file_writer = csv.writer(new_upper_concept_file)

        sorted_new_upper_concept_freq_dict = sorted(new_upper_concept_freq_dict.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
        for new_upper_concept, _ in sorted_new_upper_concept_freq_dict:
            new_upper_concept_file_writer.writerow([new_upper_concept, json.dumps(new_upper_concept_with_example_dict[new_upper_concept], ensure_ascii=False), new_upper_concept_freq_dict[new_upper_concept], new_upper_concept])
        csv_to_xlsx(new_upper_concept_file_path, new_upper_concept_xls_file_path)

        return


# test
from modules.knowledgebase.kb import KnowledgeBase

if __name__ == '__main__':
    train_dir = 'data/train_question'
    train_dir = os.path.join(root_path, train_dir)
    test_file_path = 'analyse_result/noun_phrase/ordered_phrase_pattern.csv'
    test_file_path = os.path.join(train_dir, test_file_path)
    KB = KnowledgeBase()
    finder = ConceptAndUpperConceptFinder(KB)
    finder.analyse(test_file_path)
