# import time
import os, sys
import json


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


class HfWordPhraseFinder(object):
    def __init__(self, KB, multiprocess=1):
        self.KB = KB
        self.multiprocess = multiprocess

    def analyse(self, pos_tag_file_path, analyse_result_dir, hf_word_cutoff=20, co_word_cutoff=5):
        # prepare output dir
        hf_word_phrase_dir = os.path.join(analyse_result_dir, 'hf_word_phrase')
        if not os.path.exists(hf_word_phrase_dir):
            os.makedirs(hf_word_phrase_dir)

        # find hf_word
        with open(pos_tag_file_path) as pos_tag_file:
            count = 0
            high_freq_word_set = set()
            word_freq_dict = {}
            line = pos_tag_file.readline()
            while line:
                count += 1
                if count % 30000 == 0:
                    print('Looking for high frequent word, parsed %s sentence' % count)
                pos_tags = json.loads(line)
                for word, pos_tag in pos_tags:
                    # if pos_tag != 'PU':
                    # exclude_list = ['的', '是']
                    if pos_tag != 'PU' and pos_tag != 'CD' and word != '的':
                        if word in word_freq_dict:
                            word_freq_dict[word] += 1
                            if word_freq_dict[word] >= hf_word_cutoff:
                                high_freq_word_set.add(word)
                        else:
                            word_freq_dict[word] = 1

                line = pos_tag_file.readline()

        # Tri-gram 找双词phrase
        double_word_phrase_file_name = 'double_word_phrase'
        double_word_phrase_file_path = os.path.join(hf_word_phrase_dir, double_word_phrase_file_name)
        double_word_phrase_file = open(double_word_phrase_file_path, 'w')

        print(len(high_freq_word_set))
        with open(pos_tag_file_path) as pos_tag_file:
            count = 0
            line = pos_tag_file.readline()
            co_hf_word_dict = {}
            while line:
                count += 1
                if count % 30000 == 0:
                    print('Looking for hf_co_word, parsed %s sentence' % count)
                pos_tags = json.loads(line)
                for i in range(len(pos_tags)):
                    word = pos_tags[i][0]
                    if word in high_freq_word_set:
                        if word not in co_hf_word_dict:
                            co_hf_word_dict[word] = {}

                        def count_co_word(pos_tags, word):
                            for pos_tag in pos_tags:
                                co_word = pos_tag[0]
                                if co_word in co_hf_word_dict[word]:
                                    co_hf_word_dict[word][co_word] += 1
                                else:
                                    co_hf_word_dict[word][co_word] = 1

                        if i-3 >= 0:
                            count_co_word(pos_tags[i-3:i], word)
                        elif i-2 >= 0:
                            count_co_word(pos_tags[i-2:i], word)
                        elif i-1 >= 0:
                            count_co_word(pos_tags[i-1:i], word)
                        if i+4 <= len(pos_tags):
                            count_co_word(pos_tags[i+1:i+4], word)
                        if i+3 <= len(pos_tags):
                            count_co_word(pos_tags[i+1:i+3], word)
                        if i+2 <= len(pos_tags):
                            count_co_word(pos_tags[i+1:i+2], word)

                line = pos_tag_file.readline()

        with open(pos_tag_file_path) as pos_tag_file:
            count = 0
            line = pos_tag_file.readline()
            while line:
                count += 1
                if count % 15000 == 0:
                    print('Looking for double word phrase, parsed %s sentence' % count)
                pos_tags = json.loads(line)
                for i in range(len(pos_tags)):
                    word = pos_tags[i][0]
                    if word in co_hf_word_dict:

                        def checkout_double_word_phrase(pos_tags, word, is_forward):
                            this_word_feature = {'word': word}
                            for i in range(len(pos_tags)):
                                pos_tag = pos_tags[i]
                                co_word = pos_tag[0]
                                if co_word in co_hf_word_dict[word] and co_hf_word_dict[word][co_word] >= co_word_cutoff:
                                    feature_list = []
                                    for j in range(len(pos_tags)):
                                        if j == i:
                                            feature = {'word': pos_tags[j][0]}
                                            feature_list.append(feature)
                                        else:
                                            feature = {'pos': pos_tags[j][1]}
                                            feature_list.append(feature)
                                    if is_forward:
                                        feature_list.append(this_word_feature)
                                    else:
                                        feature_list = [this_word_feature] + feature_list
                                    # todo 改成csv
                                    double_word_phrase_file.write(json.dumps(feature_list, ensure_ascii=False) + '\t' + json.dumps(feature_list, ensure_ascii=False) + '\n')

                        if i-3 >= 0:
                            checkout_double_word_phrase(pos_tags[i-3:i], word, True)
                        elif i-2 >= 0:
                            checkout_double_word_phrase(pos_tags[i-2:i], word, True)
                        elif i-1 >= 0:
                            checkout_double_word_phrase(pos_tags[i-1:i], word, True)
                        if i+4 <= len(pos_tags):
                            checkout_double_word_phrase(pos_tags[i+1:i+4], word, False)
                        if i+3 <= len(pos_tags):
                            checkout_double_word_phrase(pos_tags[i+1:i+3], word, False)
                        if i+2 <= len(pos_tags):
                            checkout_double_word_phrase(pos_tags[i+1:i+2], word, False)

                line = pos_tag_file.readline()

        double_word_phrase_file.close()
        double_word_phrase_stat_file_path = os.path.join(hf_word_phrase_dir, 'ordered_phrase_pattern.csv')
        double_word_phrase_stat_xls_file_path = os.path.join(hf_word_phrase_dir, 'ordered_phrase_pattern.xlsx')
        count_value_with_examples(double_word_phrase_file_path, double_word_phrase_stat_file_path, cutoff=2)

        # stat file with example to phrase pattern file
        tmp_file = os.path.join(hf_word_phrase_dir, 'tmp.csv')
        tmp_file_writer = csv.writer(open(tmp_file, 'w+', encoding='utf-8-sig'))
        tmp_file_writer.writerow(['pos_tag', 'core_word_index', 'features', 'freq', 'meaning', 'symbol', 'examples'])
        ordered_stat_file_reader = csv.reader(open(double_word_phrase_stat_file_path, encoding='utf-8-sig'))
        for row in ordered_stat_file_reader:
            tmp_file_writer.writerow(['', '', row[0], row[1], '', '', row[2]])
        csv_to_xlsx(tmp_file, double_word_phrase_stat_xls_file_path)
        # os.remove(tmp_file)

        # find new concept and new upper concept
        concept_and_upper_concept_finder = ConceptAndUpperConceptFinder(self.KB)
        concept_and_upper_concept_finder.analyse(double_word_phrase_stat_file_path)

        return


if __name__ == '__main__':
    pos_tag_file_path = '/mnt/d/ubuntu/projects/new_sosweety/sosweety/data/train/train_result/pos_tag_file'
    # pos_tag_file_path = '/mnt/d/ubuntu/projects/new_sosweety/sosweety/data/train_0220_23_19/train_result/123'
