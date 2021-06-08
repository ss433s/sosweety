import os, sys
import json
import sqlite3

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


def get_word_id(word):
    select_sql = "SELECT Item_id FROM Word_tbl where Word=? and type=0"
    result = cur.execute(select_sql, [word]).fetchall()
    if len(result) == 0:
        insert_concept_sql = "INSERT INTO Concept_tbl (Word) Values (?)"
        insert_concept_result = cur.execute(insert_concept_sql, [word])
        concept_id = insert_concept_result.lastrowid
        insert_word_sql = "INSERT INTO Word_tbl (Word, Item_id, Type, Frequece, Confidence) \
            Values (?, ?, 0, 0, 0.9)"
        cur.execute(insert_word_sql, [word, concept_id])
        return concept_id
    else:
        concept_id = result[0][0]
        return concept_id


# 百度信息抽取比赛实体列表
baidu_ie_entity_file = 'data/corpus/baidu_ie_competition/known_entities'
baidu_ie_corpus_file = 'data/corpus/baidu_ie_competition/train_data.json'
baidu_ie_corpus_file = os.path.join(root_path, baidu_ie_corpus_file)

# 导入上下位关系
# todo 导入fact
# todo get word id不唯一怎么解决
# todo 去重奇怪的bug where and查询奇慢
# todo 词查询优化，意义不大，速度足够快
with open(baidu_ie_corpus_file) as train_file:

    line = train_file.readline()
    count = 0
    relations_set = set()
    in_kb_relation_set = set()
    while line:
        count += 1
        if count % 10000 == 0:
            print('parsed %s sentence' % count)
        data = json.loads(line)
        for spo in data['spo_list']:

            object_id = get_word_id(spo['object'])
            object_type_id = get_word_id(spo['object_type'])
            subject_id = get_word_id(spo['subject'])
            subject_type_id = get_word_id(spo['subject_type'])

            # select_sql = "SELECT Concept1 FROM Concept_relation_tbl WHERE Concept1=? and Concept2=?"
            select_sql2 = "SELECT Concept2 FROM Concept_relation_tbl WHERE Concept1=?"

            obj_relation = str(object_id) + '_' + str(object_type_id)
            if obj_relation not in relations_set and obj_relation not in in_kb_relation_set:
                select_result2 = cur.execute(select_sql2, [object_id]).fetchall()
                select_result2_set = set()
                for concept2 in select_result2:
                    select_result2_set.add(concept2[0])
                if object_type_id not in select_result2_set:
                    relations_set.add(obj_relation)
                else:
                    in_kb_relation_set.add(obj_relation)

            subj_relation = str(subject_id) + '_' + str(subject_type_id)
            if subj_relation not in relations_set and subj_relation not in in_kb_relation_set:
                select_result2 = cur.execute(select_sql2, [subject_id]).fetchall()
                select_result2_set = set()
                for concept2 in select_result2:
                    select_result2_set.add(concept2[0])
                if subject_type_id not in select_result2_set:
                    relations_set.add(subj_relation)
                else:
                    in_kb_relation_set.add(subj_relation)

        line = train_file.readline()

    # 插入新relation
    for relation in relations_set:
        relation = relation.split('_')
        concept1 = relation[0]
        concept2 = relation[1]

        insert_relation_sql = "INSERT INTO Concept_relation_tbl (Concept1, Concept2, Relation_type) Values (?, ?, 0)"
        cur.execute(insert_relation_sql, [concept1, concept2])

    kb_db_conn.commit()
