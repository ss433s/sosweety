import os, sys
import sqlite3
import time

# 获取当前路径， 通过anchor文件获取项目root路径
this_file_path = os.path.split(os.path.realpath(__file__))[0]
this_path = this_file_path
while this_path:
    if os.path.exists(os.path.join(this_path, 'sosweety_root_anchor.py')):
        root_path = this_path
        break
    par_path = os.path.dirname(this_path)
    # print(par_path)
    if par_path == this_path:
        root_path = this_file_path
        break
    else:
        this_path = par_path
sys.path.append(root_path)

# 数据库路径 诡异的bug 不能在vscode的目录里
root_path_up = os.path.abspath(os.path.join(root_path, ".."))
db_path = 'data/knowledgebase/knowledgebase.db'
db_path = '/dev/shm/knowledgebase.db'
new_db_path = os.path.join(root_path_up, db_path)

print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))
conn = sqlite3.connect(new_db_path)
print("Opened database successfully")
cur = conn.cursor()


#################
# 表结构查询
#################
# sql2 = 'SELECT name FROM sqlite_master where type=\'table\' order by name'
# rst = cur.execute(sql2)
# table_list = []
# for row in rst:
#     table_list.append(row[0])

# for table in table_list:
#     print('--------' + table + '------------')
#     sql3 = 'SELECT * FROM %s limit 10' % table
#     table_content = cur.execute(sql3)
#     for line in table_content:
#         print(line)


#################
# 原理测试
#################
# word = '商行政管理哎哎'
# insert_concept_sql = "INSERT INTO Concept_tbl (Word) Values (?)"
# insert_concept_result = cur.execute(insert_concept_sql, [word])
# sql_test = 'select Concept_id from Concept_tbl where Word=?'
# rst = cur.execute(sql_test, [word])
# for row in rst:
#     print(row)


#################
# 基本查询
#################
print('--------some test------------')
word = '王者荣耀'
sql_test = 'select Item_id from Word_tbl where Word=?'
rst = cur.execute(sql_test, [word])
for row in rst:
    print(row)

# print('--------id check------------')
# concept_id = 86
# sql_test = 'select * from Word_tbl where Item_id=?'
# rst = cur.execute(sql_test, [concept_id])
# for row in rst:
#     print(row)

# print('--------concept upstream------------')
# word = '中国共产党'
# select_sql = "SELECT Concept1, Concept_tbl.Word, Concept2 FROM Concept_relation_tbl LEFT OUTER JOIN \
#                     Concept_tbl ON Concept_relation_tbl.Concept2 = Concept_tbl.Concept_id where Concept1 in (select Item_id from Word_tbl where Word= ? and Type=0)"
# rst = cur.execute(select_sql, [word]).fetchall()
# for row in rst:
#     print(row)
# print(len(rst))

# print('--------concept downstream------------')
# word = '时间单位'
# select_sql = "SELECT Concept1, Concept_tbl.Word, Concept2 FROM Concept_relation_tbl LEFT OUTER JOIN \
#                     Concept_tbl ON Concept_relation_tbl.Concept1 = Concept_tbl.Concept_id where Concept2 in (select Item_id from Word_tbl where Word= ? and Type=0)"
# rst = cur.execute(select_sql, [word]).fetchall()
# for row in rst:
#     print(row)
# print(len(rst))


#################
# 性能测试
#################
# print('--------concept check------------')
# word = '中共党员'
# sql_test = "select * from Word_tbl where word='%s'" % word
# sql_test = "select * from Word_tbl where substr(Word,1,4)='国家地理'"

# # sql_test = "select * from Word_tbl where Word LIKE '国家%'"
# def check_word(word):
#     sql_test = "select Word from Word_tbl where Word LIKE '国家%'"
#     rst = cur.execute(sql_test).fetchall()
#     new_dict = {}
#     # print(len(rst.fetchall()))
#     for row in rst:
#         word = row[0]
#         # print(word)

# check_word(word)
# print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))
# for i in range(100000):
#     rst = cur.execute(sql_test)
#     # check_word(word)
#     break
# print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))
# # print(len(rst.fetchall()))
# for row in rst:
#     print(row)
