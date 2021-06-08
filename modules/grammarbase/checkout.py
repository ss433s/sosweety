import os
import csv
import sqlite3


# 当前路径和项目root路径， 可以根据需求改变../..
this_file_path = os.path.split(os.path.realpath(__file__))[0]
root_path = os.path.abspath(os.path.join(this_file_path, ".."))

# 数据库如果存在，删掉重建
db_file_name = 'pattern_base.db'
db_file_path = os.path.join(this_file_path, db_file_name)
if not os.path.exists(db_file_path):
    raise Exception('DB does not exist')
pattern_db_conn = sqlite3.connect(db_file_path)
cur = pattern_db_conn.cursor()
print("Open database successfully")

phrase_csv_file_name = 'phrase_pattern.csv'
phrase_csv_file_path = os.path.join(this_file_path, phrase_csv_file_name)
ss_csv_file_name = 'ss_pattern.csv'
ss_csv_file_path = os.path.join(this_file_path, ss_csv_file_name)

phrase_writer = csv.writer(open(phrase_csv_file_path, 'w+', encoding='utf-8-sig'), dialect='excel')
sql = 'select * from PhrasePattern_tbl'
result = cur.execute(sql)
col_name_list = [tuple[0] for tuple in cur.description]
phrase_writer.writerow(col_name_list)
for row in result:
    phrase_writer.writerow(row)

ss_writer = csv.writer(open(ss_csv_file_path, 'w+', encoding='utf-8-sig'), dialect='excel')
sql = 'select * from Ss_pattern_tbl'
result = cur.execute(sql)
col_name_list = [tuple[0] for tuple in cur.description]
ss_writer.writerow(col_name_list)
for row in result:
    ss_writer.writerow(row)
