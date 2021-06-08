import os, sys
import sqlite3
import time
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


#########################################
# 用于init kb的文件列表, 通常包括spo file和kb relation file(有少量缺失第二列的错误)
# 关于数据太大的问题，可以尝试取交集
# 或者只保留下一步需要用到的数据的方法
#########################################
spo_prefix = 'data/init_data/spo'
spo_files = ['nsubj_pr_stat', 'dobj_pr_stat', 'amod_pr_stat']

kb_prefix = 'data/init_data/kb_relations'
kb_files = ['pedia_relation', 'pkubase', 'wiki_relation']

# # test mode
# spo_files = ['nsubj_test', 'dobj_test']
# kb_files = ['sql_test']

exclude_file_name = 'exclude_list.txt'
exclude_file_path = os.path.join(this_file_path, exclude_file_name)
exclude_list = []
with open(exclude_file_path) as exclude_file:
    for line in exclude_file.readlines():
        line = line.strip()
        exclude_list.append(line)

# 数据库路径 诡异的bug 不能在vscode的目录里
root_path_up = os.path.abspath(os.path.join(root_path, ".."))
db_dir = 'data/knowledgebase/'
db_file = 'knowledgebase.db'
db_dir = os.path.join(root_path_up, db_dir)
if not os.path.exists(db_dir):
    os.makedirs(db_dir)
new_db_path = os.path.join(db_dir, db_file)
if os.path.exists(new_db_path):
    os.remove(new_db_path)


###################
# 初始化数据库
###################
print('Task start at:')
print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))
kb_db_conn = sqlite3.connect(new_db_path)
print("Open database successfully")

cur = kb_db_conn.cursor()

create_concept_tbl_sql = '''CREATE TABLE Concept_tbl
       (Concept_id INTEGER PRIMARY KEY AUTOINCREMENT     NOT NULL,
       Word           TEXT    NOT NULL,
       Methods        TEXT,
       Properties     TEXT);'''

create_method_tbl_sql = '''CREATE TABLE Method_tbl
       (Method_id INTEGER PRIMARY KEY AUTOINCREMENT     NOT NULL,
       Word           TEXT    NOT NULL,
       Objects        TEXT,
       Code        TEXT);'''

create_fact_tbl_sql = '''CREATE TABLE Fact_tbl
       (Fact_id INT PRIMARY KEY     NOT NULL,
       Concept1       INT    NOT NULL,
       Restriction1   TEXT    NOT NULL,
       Concept2       INT    NOT NULL,
       Restriction2   TEXT    NOT NULL,
       Relation       INT    NOT NULL,
       Relation_restriction   TEXT    NOT NULL,
       Time       TEXT,
       Location   TEXT,
       Confidence  REAL       NOT NULL);'''

create_word_tbl_sql = '''CREATE TABLE Word_tbl
       (ID INTEGER PRIMARY KEY AUTOINCREMENT    NOT NULL,
       Word           TEXT    NOT NULL,
       Item_id        INT    NOT NULL,
       Type     INT    NOT NULL,
       Frequece  INT    NOT NULL,
       Confidence REAL NOT NULL);'''

create_concept_relation_tbl_sql = '''CREATE TABLE Concept_relation_tbl
       (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
       Concept1       INT    NOT NULL,
       Concept2       INT    NOT NULL,
       Relation_type  INT    NOT NULL);'''

cur.execute(create_concept_tbl_sql)
cur.execute(create_method_tbl_sql)
cur.execute(create_fact_tbl_sql)
cur.execute(create_word_tbl_sql)
cur.execute(create_concept_relation_tbl_sql)

kb_db_conn.commit()


###################
# 读取concept和method
###################
print('Collect all concepts and methods:')
print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))

concept_words_dict = {}
method_words_dict = {}

# 读取spo file中的concept和method
for spo_file in spo_files:
    spo_file_path = os.path.join(root_path, spo_prefix, spo_file)
    with open(spo_file_path) as spo_file_handler:
        line = spo_file_handler.readline()
        while line:
            line_list = line.strip().split('\t')
            words = line_list[0].split('|')

            # 确定concept和method， 未来可能变动很大
            concept_word = ''
            method_word = ''
            if 'amod' in spo_file:
                concept_word = words[1]
            else:
                concept_word = words[0]
            if 'nsubj' in spo_file or 'dobj' in spo_file:
                method_word = words[1]

            # method_words[method_word] = 1
            # concept_words[concept_word] = 1
            if concept_word != '' and concept_word not in concept_words_dict:
                concept_words_dict[concept_word] = len(concept_words_dict)
            if method_word != '' and method_word not in method_words_dict:
                method_words_dict[method_word] = len(method_words_dict)

            line = spo_file_handler.readline()

# 读取kb file中的concept
for kb_file in kb_files:
    kb_file_path = os.path.join(root_path, kb_prefix, kb_file)
    with open(kb_file_path) as kb_file_handler:
        line = kb_file_handler.readline()
        while line:
            words = line.strip().split('\t')
            if words[0] not in concept_words_dict:
                concept_words_dict[words[0]] = len(concept_words_dict)
            if len(words) > 1:
                if words[1] not in concept_words_dict:
                    concept_words_dict[words[1]] = len(concept_words_dict)
            line = kb_file_handler.readline()

print('Find %s concepts, %s methods' % (len(concept_words_dict), len(method_words_dict)))


###################
# 导入数据库
###################

# 导入concept和method
for concept, index in concept_words_dict.items():
    if index % 1000000 == 0:
        print('create %s concepts' % index)
    insert_concept_sql = "INSERT INTO Concept_tbl (Concept_id, Word) \
        Values (?, ?)"
    insert_word_sql = "INSERT INTO Word_tbl (Word, Item_id, Type, Frequece, Confidence) \
        Values (?, ?, 0, 0, 0.9)"
    cur.execute(insert_concept_sql, (index, concept))
    cur.execute(insert_word_sql, (concept, index))

for method, index in method_words_dict.items():
    if index % 1000000 == 0:
        print('create %s methods' % index)
    insert_method_sql = "INSERT INTO Method_tbl (Method_id, Word) \
        Values (?, ?)"
    insert_word_sql = "INSERT INTO Word_tbl (Word, Item_id, Type, Frequece, Confidence) \
        Values (?, ?, 1, 0, 0.9)"
    cur.execute(insert_method_sql, (index, method))
    cur.execute(insert_word_sql, (method, index))

kb_db_conn.commit()


# 建立index
create_index_sql = 'CREATE INDEX Method_word_index ON Method_tbl (Word);'
cur.execute(create_index_sql)
create_index_sql = 'CREATE INDEX Concept_word_index ON Concept_tbl (Word);'
cur.execute(create_index_sql)
create_index_sql = 'CREATE INDEX Word_index ON Word_tbl (Word);'
cur.execute(create_index_sql)
create_index_sql = 'CREATE INDEX ID_index ON Word_tbl (Item_id);'
cur.execute(create_index_sql)
kb_db_conn.commit()


# 根据method 更新关联的concept
print('Update spos:')
print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))

for spo_file in spo_files:
    spo_file_path = os.path.join(root_path, spo_prefix, spo_file)

    # 主谓关系提取concept的methods列表
    if 'nsubj' in spo_file:
        concept_method_dict = {}
        with open(spo_file_path) as spo_file_handler:
            line = spo_file_handler.readline()
            while line:
                line_list = line.strip().split('\t')
                words = line_list[0].split('|')

                subj = words[0]
                method = words[1]
                method_id = method_words_dict[method]
                if subj not in concept_method_dict:
                    concept_method_dict[subj] = set()
                concept_method_dict[subj].add(method_id)
                line = spo_file_handler.readline()

            count = 0
            for subj in concept_method_dict:
                concept_id = concept_words_dict[subj]
                count += 1
                if count % 10000 == 0:
                    print('update %s nsubj' % count)
                update_sql = "UPDATE Concept_tbl set Methods = ? where Concept_id=?"
                method_list = list(concept_method_dict[subj])
                cur.execute(update_sql, (json.dumps(method_list), concept_id))
            kb_db_conn.commit()

    # 动宾关系提取methods的obj列表
    if 'dobj' in spo_file:
        method_concept_dict = {}
        with open(spo_file_path) as spo_file_handler:
            line = spo_file_handler.readline()
            while line:
                line_list = line.strip().split('\t')
                words = line_list[0].split('|')

                obj = words[0]
                method = words[1]
                obj_id = concept_words_dict[obj]
                if method not in method_concept_dict:
                    method_concept_dict[method] = set()
                method_concept_dict[method].add(obj_id)
                line = spo_file_handler.readline()

            count = 0
            for method in method_concept_dict:
                count += 1
                if count % 10000 == 0:
                    print('update %s dobj' % count)
                update_sql = "UPDATE Method_tbl set Objects = ? where Word= ?"
                # print(update_sql)
                concept_list = list(method_concept_dict[method])
                cur.execute(update_sql, (json.dumps(concept_list), method))
            kb_db_conn.commit()


# 遍历relation， 录入relation表
print('Update relations:')
print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))

relations = set()
for kb_file in kb_files:
    kb_file_path = os.path.join(root_path, kb_prefix, kb_file)
    with open(kb_file_path) as kb_file_handler:
        line = kb_file_handler.readline()
        count = 0
        while line:
            count += 1
            if count % 1000000 == 0:
                print('update %s relations' % count)
            words = line.strip().split('\t')
            if len(words) > 1 and words[1] not in exclude_list:
                concept_id1 = concept_words_dict[words[0]]
                concept_id2 = concept_words_dict[words[1]]
                relation = str(concept_id1) + '|' + str(concept_id2)
                if relation not in relations:
                    relations.add(relation)
                    insert_concept_sql = "INSERT INTO Concept_relation_tbl (Concept1, Concept2, Relation_type) \
                        Values (?, ?, 0)"
                    cur.execute(insert_concept_sql, (concept_id1, concept_id2))

            line = kb_file_handler.readline()
        kb_db_conn.commit()

create_index_sql = 'CREATE INDEX Concept1_index ON Concept_relation_tbl (Concept1);'
cur.execute(create_index_sql)
create_index_sql = 'CREATE INDEX Concept2_index ON Concept_relation_tbl (Concept2);'
cur.execute(create_index_sql)
kb_db_conn.commit()

kb_db_conn.close()

print('All tasks finished at:')
print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))
