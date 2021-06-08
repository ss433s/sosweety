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
from modules.learning.learning_result_updater import Updater

train_dir = 'data/train_question'
train_dir = os.path.join(root_path, train_dir)

KB = KnowledgeBase()
updater = Updater(KB)
updater.update(train_dir)
