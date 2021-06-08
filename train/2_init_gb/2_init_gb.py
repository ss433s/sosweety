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

KB = KnowledgeBase(memory_mode=False)

init_gb_dir = 'data/init_gb'
init_gb_dir = os.path.join(root_path, init_gb_dir)
parse_result_dir = 'parse_result'
parse_result_dir = os.path.join(init_gb_dir, parse_result_dir)
pos_tags_file_name = 'pos_tags_file'
pos_tags_file_name = '123'
pos_tags_file_path = os.path.join(parse_result_dir, pos_tags_file_name)
if not os.path.exists(pos_tags_file_path):
    raise('no pos_tag_file')

analyse_result_dir = 'analyse_result'
analyse_result_dir = os.path.join(init_gb_dir, analyse_result_dir)
if not os.path.exists(analyse_result_dir):
    os.makedirs(analyse_result_dir)


trainer = Trainer(KB, multiprocess=3)
trainer.analyse(pos_tags_file_path, analyse_result_dir)
