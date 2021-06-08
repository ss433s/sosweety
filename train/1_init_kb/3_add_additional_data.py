import os, sys
# import json
import sqlite3
import csv

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


# additional data files
additional_data_dir = 'additional_data'
additional_data_dir = os.path.join(this_file_path, additional_data_dir)
additional_relations_file_path = os.path.join(additional_data_dir, 'additional_relations.csv')

with open(additional_relations_file_path, encoding='utf-8-sig') as additional_relations_file:
    csv_reader = csv.reader(additional_relations_file)

    for row in csv_reader:
        concept1 = get_word_id(row[0])
        concept2 = get_word_id(row[1])
        select_sql = "SELECT Concept1 FROM Concept_relation_tbl WHERE Concept1=? and Concept2=?"
        select_result = cur.execute(select_sql, [concept1, concept2]).fetchall()
        if len(select_result) == 0:
            insert_relation_sql = "INSERT INTO Concept_relation_tbl (Concept1, Concept2, Relation_type) Values (?, ?, 0)"
            cur.execute(insert_relation_sql, [concept1, concept2])

    kb_db_conn.commit()
