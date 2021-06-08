# 分析parse result文件，找出新phrase pattern和subsentence pattern的程序

import os, sys

# 获取当前路径， 通过anchor文件获取项目root路径
this_file_path = os.path.split(os.path.realpath(__file__))[0]
this_path = this_file_path
while this_path:
    if os.path.exists(os.path.join(this_path, 'sosweety_root_anchor.py')):
        root_path = this_path
        break
    par_path = os.path.dirname(this_path)
    # print(par_path)
    if par_path == this_path:
        root_path = this_file_path
        break
    else:
        this_path = par_path
sys.path.append(root_path)

from modules.learning.subsentence.ss_pattern_finder import SubsentencePatternFinder
from modules.learning.phrase.phrase_pattern_finder import PhrasePatternFinder
from modules.utils.utils import csv_to_xlsx


class ParseResultAnalyser():
    def __init__(self, KB, multiprocess=1):
        self.multiprocess = multiprocess
        phrase_pattern_finder = PhrasePatternFinder(KB, multiprocess=self.multiprocess)
        ss_pattern_finder = SubsentencePatternFinder(KB, multiprocess=self.multiprocess)
        self.finders = [phrase_pattern_finder, ss_pattern_finder]
        # self.finders = [ss_pattern_finder]
        return

    def analyse(self, input_file_path, output_dir):
        for finder in self.finders:
            finder.analyse(input_file_path, output_dir)
        self.csv2xlsx(output_dir)
        return

    def csv2xlsx(self, output_dir):
        csv_file_list = [
            ['noun_phrase/tmp.csv', 'noun_phrase/ordered_phrase_pattern.xlsx'],
            'noun_phrase/new_concept.csv',
            'noun_phrase/new_upper_concept.csv',
            ['hf_word_phrase/tmp.csv', 'hf_word_phrase/ordered_phrase_pattern.xlsx'],
            'hf_word_phrase/new_concept.csv',
            'hf_word_phrase/new_upper_concept.csv',
            ['ss_pattern/tmp.csv', 'ss_pattern/ordered_stat_file.xlsx']
        ]
        for item in csv_file_list:
            if isinstance(item, list):
                file = os.path.join(output_dir, item[0])
                xl_file = os.path.join(output_dir, item[1])
            else:
                file = os.path.join(output_dir, item)
                xl_file = file[:-4] + '.xlsx'
            if os.path.exists(file):
                csv_to_xlsx(file, xl_file)


if __name__ == '__main__':
    analyser = ParseResultAnalyser('KB')
    analyse_result_dir = os.path.join(root_path, 'data/train_baidu_ie_corpus/analyse_result')
    analyser.csv2xlsx(analyse_result_dir)
