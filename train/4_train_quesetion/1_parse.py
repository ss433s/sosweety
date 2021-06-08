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


from modules.knowledgebase.kb import KnowledgeBase
from modules.trainer.trainer import Trainer
# from modules.utils.utils import stanford_simplify

corpus_file_path = 'data/corpus/dureader_questions/total'
corpus_file_path = os.path.join(root_path, corpus_file_path)

train_dir = 'data/train_question'
train_dir = os.path.join(root_path, train_dir)
parse_result_dir = 'parse_result'
parse_result_dir = os.path.join(train_dir, parse_result_dir)
if not os.path.exists(parse_result_dir):
    os.makedirs(parse_result_dir)

pos_tags_file_name = 'pos_tags_file'
pos_tags_file_path = os.path.join(parse_result_dir, pos_tags_file_name)

KB = KnowledgeBase()
trainer = Trainer(KB, multiprocess=1)
trainer.raw_parse(corpus_file_path, pos_tags_file_path)
