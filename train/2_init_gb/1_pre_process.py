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

from modules.utils.utils import stanford_simplify


init_gb_dir = 'data/init_gb'
init_gb_dir = os.path.join(root_path, init_gb_dir)
if not os.path.exists(init_gb_dir):
    os.makedirs(init_gb_dir)

parse_result_dir = 'parse_result'
parse_result_dir = os.path.join(init_gb_dir, parse_result_dir)
if not os.path.exists(parse_result_dir):
    os.makedirs(parse_result_dir)

pos_tags_file_name = 'pos_tags_file'
pos_tags_file_path = os.path.join(parse_result_dir, pos_tags_file_name)

with open(pos_tags_file_path, 'w') as pos_tags_file:
    # 打开语料文件
    file_path = 'data/corpus/baidu_ie_competition/parse_file_total'
    file_path = os.path.join(root_path, file_path)
    file = open(file_path)
    line = file.readline()
    count = 0
    while line:
        count += 1
        if count % 5000 == 0:
            print('parsed %s sentence' % count)
        line = line.strip().split('\t')
        pos_tags = json.loads(line[1].strip())
        pos_tags = stanford_simplify(pos_tags)

        tmp_stamp = 0
        for i in range(len(pos_tags)):
            pos_tag = pos_tags[i]
            if pos_tag[0] in ['。', '！', '？', '?', '，', ',', ';', '；']:
                pos_tags_file.write(json.dumps(pos_tags[tmp_stamp: i], ensure_ascii=False) + '\n')
                tmp_stamp = i + 1
        if tmp_stamp < len(pos_tags):
            pos_tags_file.write(json.dumps(pos_tags[tmp_stamp: len(pos_tags)], ensure_ascii=False) + '\n')

        line = file.readline()
    file.close()
