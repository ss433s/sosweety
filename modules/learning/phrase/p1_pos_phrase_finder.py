import json, os
import pandas as pd
from sParser import Word, ParseResult, stanford_simplify, KB, phrase_patterns


###################
# 读取待处理文件
# to do
# 准备提供对外接口处理不同文件
# 本文件内为处理 pos tag数组格式, 每一行是一个sub sentence
###################
file = './init_data/process/unsolve_ss4'
unsolvable_ss_file = open(file)

# 开始finder 定义参数
cutoff = 1000

# phrase str提取
phrase_strs = []
for phrase_pattern in phrase_patterns:
    phrase_strs.append(phrase_pattern.symbol)


# parse result构建
def tuples2parse_result(tuples):
    content = []
    for word in tuples:
        tmp_word = Word(word[0], word[1])
        content.append(tmp_word)
    parse_result = ParseResult(content)
    return parse_result


# 强行遍历各种可能性2-3个词
def checkout_pos_phrase(parse_result):

    pos_phrases = []
    for i in range(len(parse_result.contents)-1):
        item = parse_result.contents[i]
        next_item = parse_result.contents[i+1]

        pos_str = '|'.join([item.pos_tag, next_item.pos_tag])
        value_str = '|'.join([item.value, next_item.value])
        if pos_str not in phrase_strs:
            pos_phrases.append([pos_str, value_str])

        if i < len(parse_result.contents) - 2:
            next_next_item = parse_result.contents[i+2]
            pos_str = '|'.join([item.pos_tag, next_item.pos_tag, next_next_item.pos_tag])
            value_str = '|'.join([item.value, next_item.value, next_next_item.value])
            if pos_str not in phrase_strs:
                pos_phrases.append([pos_str, value_str])

    return pos_phrases


lines = unsolvable_ss_file.readlines()
total_pos_phrase = []
for i in range(len(lines)):
    if i % 3000 == 0:
        print('parsed %s sentence, total %s' % (i, len(lines)))

    pos_tags = json.loads(lines[i].strip())
    # pos_tags = stanford_simplify(pos_tags)

    ss_parse_result = tuples2parse_result(pos_tags)
    total_pos_phrase += checkout_pos_phrase(ss_parse_result)


with open('./init_data/2.1.2_all_pos_phrases', 'w') as f:
    for i in total_pos_phrase:
        f.write(json.dumps(i, ensure_ascii=False) + '\n')


# pandas排序去重
# with open('./init_data/123') as f:
with open(tmp_file) as f:
    total_concept_phrase = []
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        total_concept_phrase.append(line)

    df_dict = {}
    df_dict['concept_phrase'] = total_concept_phrase
    df = pd.DataFrame(df_dict)
    df2 = df.concept_phrase.value_counts()
    # df2.to_csv('./init_data/123stat.csv')
    df3_dict = {'label': df2.index, 'count': df2.values}
    df3 = pd.DataFrame(df3_dict)
    with open('./init_data/2.1.2_all_pos_phrases_stat', 'w') as result_file:
        for i in range(len(df3)):
            result_file.write(df3['label'][i] + '\t' + str(df3['count'][i]) + '\n')
