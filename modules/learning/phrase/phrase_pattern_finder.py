import os, sys


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

from modules.learning.phrase.p2_noun_phrase_finder import NounPhraseFinder
from modules.learning.phrase.p3_hf_word_phrase_finder import HfWordPhraseFinder


class PhrasePatternFinder():
    def __init__(self, KB, multiprocess=1):
        self.KB = KB
        self.multiprocess = multiprocess
        p2_noun_phrase_finder = NounPhraseFinder(KB, multiprocess=self.multiprocess)
        p3_hf_word_phrase_finder = HfWordPhraseFinder(KB, multiprocess=self.multiprocess)
        self.finders = [p2_noun_phrase_finder, p3_hf_word_phrase_finder]

    def analyse(self, pos_tag_file_path, analyse_result_dir, cutoff=10):
        for finder in self.finders:
            finder.analyse(pos_tag_file_path, analyse_result_dir)
        return
