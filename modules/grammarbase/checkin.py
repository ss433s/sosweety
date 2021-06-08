import os
import sqlite3
import pandas


# 当前路径和项目root路径， 可以根据需求改变../..
this_file_path = os.path.split(os.path.realpath(__file__))[0]
root_path = os.path.abspath(os.path.join(this_file_path, ".."))

# 数据库如果存在，删掉重建
db_file_name = 'pattern_base.db'
db_file_path = os.path.join(this_file_path, db_file_name)
if os.path.exists(db_file_path):
    os.remove(db_file_path)
pattern_db_conn = sqlite3.connect(db_file_path)
print("Open database successfully")

phrase_csv_file_name = 'phrase_pattern.csv'
phrase_csv_file_path = os.path.join(this_file_path, phrase_csv_file_name)
ss_csv_file_name = 'ss_pattern.csv'
ss_csv_file_path = os.path.join(this_file_path, ss_csv_file_name)

phrase_df = pandas.read_csv(phrase_csv_file_path)
phrase_df.to_sql('PhrasePattern_tbl', pattern_db_conn, if_exists='append', index=False)
ss_df = pandas.read_csv(ss_csv_file_path)
ss_df.to_sql('Ss_pattern_tbl', pattern_db_conn, if_exists='append', index=False)
