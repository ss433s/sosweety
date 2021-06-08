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

import json
import csv
from modules.utils.utils import csv_to_xlsx

train_dir = 'data/train_question'
train_dir = os.path.join(root_path, train_dir)
ss_pattern_file_dir = 'analyse_result/ss_pattern'
ss_pattern_file_dir = os.path.join(train_dir, ss_pattern_file_dir)
ss_pattern_file_name = 'ordered_stat_file.csv'
ss_pattern_file_path = os.path.join(ss_pattern_file_dir, ss_pattern_file_name)
if not os.path.exists(ss_pattern_file_path):
    raise('no file found')

with open(ss_pattern_file_path, encoding='utf-8-sig') as ss_pattern_file:
    ss_pattern_file_reader = csv.reader(ss_pattern_file)
    modified_file_name = 'modified_ss_pattern.csv'
    modified_file_path = os.path.join(ss_pattern_file_dir, modified_file_name)
    file = open(modified_file_path, 'w', encoding='utf-8-sig')
    file_writer = csv.writer(file)

    pattern_count_dict = {}
    pattern_example_dict = {}
    for line in ss_pattern_file_reader:
        parse_str = line[0]
        examples = json.loads(line[2])

        def simplify_parse_str(parse_str):
            parse_list = parse_str.split('|')

            p1 = 0
            p2 = 0
            new_list = []
            for i in range(len(parse_list)):
                if parse_list[i] != 'NN':
                    new_list.append(parse_list[i])
                    p1 = i
                    p2 = i
                else:
                    if p2 != p1:
                        p2 += 1
                    else:
                        new_list.append('NN')
                        p2 += 1

            return '|'.join(new_list)

        simplified_parse_str = simplify_parse_str(parse_str)
        if simplified_parse_str in pattern_count_dict:
            pattern_count_dict[simplified_parse_str] += int(line[1])
        else:
            pattern_count_dict[simplified_parse_str] = int(line[1])
            pattern_example_dict[simplified_parse_str] = examples

    sorted_pattern_count_dict = sorted(pattern_count_dict.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    for pattern, count in sorted_pattern_count_dict:
        file_writer.writerow([pattern, count, json.dumps(pattern_example_dict[pattern], ensure_ascii=False)])

    file.close()

ordered_stat_xls_file_path = os.path.join(ss_pattern_file_dir, 'ordered_stat_file.xlsx')

# stat file with example to ss pattern file
tmp_file = os.path.join(ss_pattern_file_dir, 'tmp.csv')
tmp_file_writer = csv.writer(open(tmp_file, 'w', encoding='utf-8-sig'))
tmp_file_writer.writerow(['parse_str', 'freq', 'ss_type', 'meaning', 'ss_type2', 'examples'])
ordered_stat_file_reader = csv.reader(open(modified_file_path, encoding='utf-8-sig'))
for row in ordered_stat_file_reader:
    tmp_file_writer.writerow([row[0], row[1], '', '', '', row[2]])
csv_to_xlsx(tmp_file, ordered_stat_xls_file_path)
