import os
import csv


# 当前路径和项目root路径， 可以根据需求改变../..
this_file_path = os.path.split(os.path.realpath(__file__))[0]
root_path = os.path.abspath(os.path.join(this_file_path, "../.."))

# 创建rules存储文件
rules_dir = 'data/2_concept_rules'
rules_dir = os.path.join(root_path, rules_dir)

rules_file_name = 'rules'
rules_confirmed_file_name = 'rules_confirmed'
rules_todo_file_name = 'rules_todo'
rules_removed_file_name = 'rules_removed'

rules_file_path = os.path.join(rules_dir, rules_file_name)
rules_confirmed_file_path = os.path.join(rules_dir, rules_confirmed_file_name)
rules_todo_file_path = os.path.join(rules_dir, rules_todo_file_name)
rules_removed_file_path = os.path.join(rules_dir, rules_removed_file_name)

rules_file = open(rules_file_path)
rules_removed_file = open(rules_removed_file_path, 'w')
rules_confirmed_file = open(rules_confirmed_file_path, 'w')
rules_todo_file = open(rules_todo_file_path, 'w')

all_lines = csv.reader(rules_file)
rules_removed_file_writer = csv.writer(rules_removed_file)
rules_confirmed_file_writer = csv.writer(rules_confirmed_file)
rules_todo_file_writer = csv.writer(rules_todo_file)

remove_list = ['人口', '面积']
confirm_list = []

count = 0
for line in all_lines:
    # print(line)
    if line[2] in remove_list:
        rules_removed_file_writer.writerow(line)
    count += 1

rules_removed_file.close()
rules_todo_file.close()
rules_confirmed_file.close()
print(count)
