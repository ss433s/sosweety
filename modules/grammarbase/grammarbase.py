import os, sys
# import json
import pandas as pd

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

from modules.grammarbase.grammerbase_class import PhrasePattern, SubSentencePattern


class GrammarBase(object):

    def __init__(self, memory_mode=False):
        ###################
        # 读取短语库和句式库
        # todo 改成xlsx格式
        ###################
        phrase_pattern_file_path = 'base_files/phrase_pattern.csv'
        phrase_pattern_file_path = os.path.join(this_file_path, phrase_pattern_file_path)
        phrase_df = pd.read_csv(phrase_pattern_file_path)

        phrase_patterns = []
        for i in range(len(phrase_df)):
            pos_tag = phrase_df['pos_tag'][i]
            core_word_index = phrase_df['core_word_index'][i]
            features = phrase_df['features'][i]
            freq = phrase_df['freq'][i]
            meaning = phrase_df['meaning'][i]
            symbol = phrase_df['symbol'][i]
            examples = phrase_df['examples'][i]
            phrase_pattern = PhrasePattern(pos_tag, core_word_index, features, freq, meaning, symbol, examples)
            phrase_patterns.append(phrase_pattern)

        ss_pattern_file_path = 'base_files/ss_pattern.csv'
        ss_pattern_file_path = os.path.join(this_file_path, ss_pattern_file_path)
        ss_df = pd.read_csv(ss_pattern_file_path)

        ss_patterns = []
        for i in range(len(ss_df)):
            parse_str = ss_df['parse_str'][i]
            freq = ss_df['freq'][i]
            ss_type = ss_df['ss_type'][i]
            meaning = ss_df['meaning'][i]
            ss_type2 = ss_df['ss_type2'][i]
            examples = ss_df['examples'][i]
            ss_pattern = SubSentencePattern(parse_str, freq, ss_type, meaning, ss_type2, examples)
            ss_patterns.append(ss_pattern)

        self.phrase_patterns = phrase_patterns
        self.ss_patterns = ss_patterns

    # update_dict, key是phrase_patterns和ss_patterns, value是[PhrasePatterns], [SubsentencePatterns]
    # update时，先备份原csv，然后做一份新csv
    # 废弃上述方法，改为直接xls写入
    def update(update_dict):
        return


# test
if __name__ == '__main__':
    GB = GrammarBase()
