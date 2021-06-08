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

from modules.sParser.sParser import sParser
from modules.knowledgebase.kb import KnowledgeBase
from modules.utils.utils import count_value

train_dir = 'data/train_question'
train_dir = os.path.join(root_path, train_dir)
if not os.path.exists(train_dir):
    os.makedirs(train_dir)

# 解析出parse result file
parse_result_dir = 'parse_result'
parse_result_dir = os.path.join(train_dir, parse_result_dir)
if not os.path.exists(parse_result_dir):
    os.makedirs(parse_result_dir)

pos_tags_file_name = 'pos_tags_file'
pos_tags_file_path = os.path.join(parse_result_dir, pos_tags_file_name)

KB = KnowledgeBase()
parser = sParser(KB)

with open(pos_tags_file_path) as pos_tags_file:
    # 打开语料文件
    file_path = 'question_word_raw'
    file_path = os.path.join(parse_result_dir, file_path)
    file = open(file_path, 'w')
    line = pos_tags_file.readline()
    word_freq_dict = {}
    count = 0
    while line:
        count += 1
        if count % 5000 == 0:
            print('parsed %s sentence' % count)
        line = line.strip()
        pos_tags = json.loads(line)
        for pos_tag in pos_tags:
            word = pos_tag[0]
            file.write(word + '\n')

        line = pos_tags_file.readline()
    file.close()

    stat_file_path = 'question_word_stat'
    stat_file_path = os.path.join(parse_result_dir, stat_file_path)
    count_value(file_path, stat_file_path, cutoff=5)
