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

import pandas as pd
import json
import csv
from modules.sParser.parser_class import ParseResult, Word


question_word_file_path = os.path.join(this_file_path, 'question_word')
question_word_set = set()
with open(question_word_file_path) as question_word_file:
    for line in question_word_file.readlines():
        line = line.strip()
        question_word_set.add(line)


###################
# 判定元组tuple1是否被包含于元组tuple2
###################
def tuple_in_tuple(tuple1, tuple2):
    if tuple1[0] >= tuple2[0] and tuple1[1] <= tuple2[1]:
        return True
    else:
        return False


###################
# parse result构建
###################
def tuples2parse_result(tuples):
    content = []
    for word in tuples:
        tmp_word = Word(word[0], word[1])
        content.append(tmp_word)
    parse_result = ParseResult(content)
    return parse_result


###################
# stanford 的postag 是列表，列表元素是（词，词性）的元组
# 该函数用于简化Stanford corenlp的词性结果
###################
def stanford_simplify(pos_tags):
    # stanford_simplify_dict = {}
    # file_path = os.path.join(this_file_path, 'stanford_simplify')
    # with open(file_path) as f:
    #     lines = f.readlines()
    #     for line in lines:
    #         line = line.strip().split('\t')
    #         stanford_simplify_dict[line[0]] = line[1]
    # result = []
    # for word, pos_tag in pos_tags:
    #     result.append((word, stanford_simplify_dict[pos_tag]))
    # return result

    stanford_simplify_dict = {}
    file_path = os.path.join(this_file_path, 'stanford_simplify')
    with open(file_path) as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip().split('\t')
            stanford_simplify_dict[line[0]] = line[1]
    result = []
    for word, pos_tag in pos_tags:
        if word in question_word_set:
            result.append((word, 'QA'))
        else:
            result.append((word, stanford_simplify_dict[pos_tag]))
    return result


###################
# 处理hanlp的分词结果，选择cpos_tag进行处理
###################
def hanlp_simplify(pos_tags):
    hanlp_simplify_dict = {}
    file_path = os.path.join(this_file_path, 'hanlp_simplify')
    with open(file_path) as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip().split('\t')
            hanlp_simplify_dict[line[0]] = line[1]
    result = []
    for word, pos_tag in pos_tags:
        if pos_tag in hanlp_simplify_dict:
            result.append((word, hanlp_simplify_dict[pos_tag]))
        else:
            result.append((word, 'OO'))
    return result


###################
# 处理hanlp的分词结果，选择cpos_tag进行处理
###################
def jieba_simplify(pos_tags):
    jieba_simplify_dict = {}
    file_path = os.path.join(this_file_path, 'jieba_simplify')
    with open(file_path) as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip().split('\t')
            jieba_simplify_dict[line[0]] = line[1]
    result = []
    for word, pos_tag in pos_tags:
        if pos_tag in jieba_simplify_dict:
            if word in question_word_set:
                result.append((word, 'QA'))
            else:
                result.append((word, jieba_simplify_dict[pos_tag]))
        else:
            result.append((word, 'OO'))
    return result


###################
# 找子串
###################
def find_all_sub_list(short_list, long_list):
    result = []
    for i in range(len(long_list)):
        if long_list[i] == short_list[0]:
            if i + len(short_list) <= len(long_list):
                full_match = True
                for j in range(len(short_list)):
                    if short_list[j] != long_list[i+j]:
                        full_match = False
                if full_match:
                    result.append(i)
    return result


###################
# 统计某文件制定列 只支持\t分割
###################
def count_value(input_file_path, ouput_file_path, column=0, cutoff=10):
    count = 0
    stat_dict = {}
    with open(input_file_path) as input_file:
        line = input_file.readline()
        while line:
            count += 1
            if count % 500000 == 0:
                print('count %s phrases' % count)
            line = line.strip().split('\t')
            item = line[column]
            if item in stat_dict:
                stat_dict[item] += 1
            else:
                stat_dict[item] = 1

            line = input_file.readline()
    df = pd.DataFrame.from_dict(stat_dict, orient='index', columns=['value'])
    df2 = df.sort_values(by=['value'], ascending=False)
    df3 = df2[df2['value'] > cutoff]
    df3.to_csv(ouput_file_path)
    return


def count_value_with_examples(input_file_path, ouput_file_path, column=0, example_column=1, cutoff=10):
    count = 0
    stat_dict = {}
    with open(input_file_path) as input_file:
        line = input_file.readline()
        while line:
            count += 1
            if count % 500000 == 0:
                print('count %s lines' % count)
            line = line.strip().split('\t')
            item = line[column]
            if item != '':
                if item in stat_dict:
                    stat_dict[item] += 1
                else:
                    stat_dict[item] = 1
            line = input_file.readline()

    # cutoff
    cutoff_stat_dict = {}
    for key, value in stat_dict.items():
        if value > cutoff:
            cutoff_stat_dict[key] = value
    del stat_dict

    # 多过一次，节省内存
    key_example_dict = {}
    with open(input_file_path) as input_file:
        line = input_file.readline()
        while line:
            count += 1
            if count % 500000 == 0:
                print('count %s lines' % count)
            line = line.strip().split('\t')
            if len(line) > 1:
                item = line[column]
                if item in cutoff_stat_dict:
                    example = line[example_column]
                    if item not in key_example_dict:
                        key_example_dict[item] = set([example])
                    elif len(key_example_dict[item]) < 5:
                        key_example_dict[item].add(example)
            line = input_file.readline()

    d_order = sorted(cutoff_stat_dict.items(), key=lambda x: x[1], reverse=True)
    with open(ouput_file_path, 'w', encoding='utf-8-sig') as ordered_stat_file:
        csv_writer = csv.writer(ordered_stat_file)
        for key, value in d_order:
            csv_writer.writerow([key, value, json.dumps(list(key_example_dict[key]), ensure_ascii=False)])
            # ordered_stat_file.write(key + '\t' + str(value) + '\t' + json.dumps(list(key_example_dict[key]), ensure_ascii=False) + '\n')

    return


def csv_to_xlsx(input_file_path, ouput_file_path):
    if os.path.getsize(input_file_path) != 0:
        csv_file = pd.read_csv(input_file_path, header=None, index_col=None)
        csv_file.to_excel(ouput_file_path, header=False, index=None)
