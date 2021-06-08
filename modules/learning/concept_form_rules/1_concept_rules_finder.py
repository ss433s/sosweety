import os, sys
import csv
import sqlite3
import time

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

# 数据库路径 诡异的bug 不能在vscode的目录里
root_path_up = os.path.abspath(os.path.join(root_path, ".."))
db_path = 'data/knowledgebase/knowledgebase.db'
new_db_path = os.path.join(root_path_up, db_path)

kb_db_conn = sqlite3.connect(new_db_path)
print("Opened database successfully")
cur = kb_db_conn.cursor()

# 创建rules存储文件
rules_dir = 'data/2_concept_rules'
rules_dir = os.path.join(root_path, rules_dir)
if not os.path.exists(rules_dir):
    os.makedirs(rules_dir)
rules_file_name = 'rules'
rules_file_path = os.path.join(rules_dir, rules_file_name)
rules_file = open(rules_file_path, 'w')
rules_file_writer = csv.writer(rules_file)

cutoff = 10


# rule提取函数，输入为sub concept list， father concept， rule file
# todo 可以改为pandas去统计
def find_rules(concept1_list, concept2):

    # 前1-2个字和前N个字（N=len（concept2））
    # 后1-2个字和后N个字（N=len（concept2））
    # ??中间出现concept2

    length = len(concept2)
    f_words = []
    b_words = []
    for concept1 in concept1_list:
        char_1 = concept1[0]
        char_r1 = concept1[-1]
        f_words.append(char_1)
        b_words.append(char_r1)
        if len(concept1) >= 2:
            char_12 = concept1[0:2]
            char_r12 = concept1[-2:]
            f_words.append(char_12)
            b_words.append(char_r12)
        if length > 2 and len(concept1) >= length:
            char_n = concept1[0:length]
            char_rn = concept1[0-length:]
            f_words.append(char_n)
            b_words.append(char_rn)

    # rules = []
    f_word_freq_dict = {}
    for word in f_words:
        if word in f_word_freq_dict:
            f_word_freq_dict[word] += 1
        else:
            f_word_freq_dict[word] = 1
    for key, value in f_word_freq_dict.items():
        if value >= cutoff or (value > 0.5 * len(concept1_list) and len(concept1_list) > 5):
            # rules.append(['f', key, concept2, value, len(concept1_list)])
            rules_file_writer.writerow(['f', key, concept2, value, len(concept1_list)])

    b_word_freq_dict = {}
    for word in b_words:
        if word in b_word_freq_dict:
            b_word_freq_dict[word] += 1
        else:
            b_word_freq_dict[word] = 1
    for key, value in b_word_freq_dict.items():
        if value >= cutoff or (value > 0.5 * len(concept1_list) and len(concept1_list) > 5):
            # rules.append(['b', key, concept2, value, len(concept1_list)])
            rules_file_writer.writerow(['b', key, concept2, value, len(concept1_list)])

    return

# # pandas排序去重，不能是json，直接读字符串就行, 写csv速度更快
# # with open('./init_data/123') as f:
# with open('./init_data/all_concept_phrases') as f:
#     total_concept_phrase = []
#     lines = f.readlines()
#     for line in lines:
#         line = line.strip()
#         # concept_phrase = json.loads(line)
#         total_concept_phrase.append(line)

#     df_dict = {}
#     df_dict['concept_phrase'] = total_concept_phrase
#     df = pd.DataFrame(df_dict)
#     df2 = df.concept_phrase.value_counts()
#     df3_dict = {'label': df2.index, 'count': df2.values}
#     df3 = pd.DataFrame(df3_dict)
#     with open('./init_data/all_concept_phrases_stat', 'w') as result_file:
#         for i in range(len(df3)):
#             result_file.write(df3['label'][i] + '\t' + str(df3['count'][i]) + '\n')
#     # df2.to_csv('./init_data/123stat.csv')


###################
# 获取所有二级以上concept
###################
high_level_concept_id2word_dict = {}
select_sql = "SELECT Concept2, Concept_tbl.Word FROM Concept_relation_tbl LEFT OUTER JOIN \
                Concept_tbl ON Concept_relation_tbl.Concept2 = Concept_tbl.Concept_id"
result = cur.execute(select_sql)
count = 0
for row in result:
    count += 1
    if count % 1000000 == 0:
        print('check %s relations' % count)
    concept_id = row[0]
    high_level_concept_id2word_dict[row[0]] = row[1]

print(len(high_level_concept_id2word_dict))
count = 0
for concept_id, word in high_level_concept_id2word_dict.items():
    count += 1
    if count % 1000 == 0:
        nowStr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        print('[%s] check %s relations' % (nowStr, count))
    sub_concept_words = set()
    select_sql = "SELECT Concept1, Concept_tbl.Word FROM Concept_relation_tbl LEFT OUTER JOIN \
                    Concept_tbl ON Concept_relation_tbl.Concept1 = Concept_tbl.Concept_id where Concept2 = ?"
    result = cur.execute(select_sql, [str(concept_id)])
    for row in result:
        sub_concept_words.add(row[1])
    find_rules(list(sub_concept_words), word)

rules_file.close()
