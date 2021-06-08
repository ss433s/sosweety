# init kb

## 数据来源

### 1, zh_wiki spo统计结果 
    格式为 s|p 
### 2, 百度的关系提取结果 50种分类的结果 known_entities

### 3, zh_wiki concept relation结果（自己做的数据，46万）
### 4, cn pedia 198万数据（根据baidu card标记提取card的第一句话自己处理得到，处理方法同3）
### 5, pkubase 2500万数据，kb自带'<类型>'关系
### 6, todo 补充xlcore数据
### 7, 3-6 格式均为 concept1 \t concept2

<br/>


## 处理过程

### 1, 提取spo中的concept（s, o) 和 method （p）
### 2, merge 三套数据中的concept
### 3, 


## 数据库格式
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

Type 0 concept 1method
create_word_tbl_sql = '''CREATE TABLE Word_tbl
       (ID INTEGER PRIMARY KEY AUTOINCREMENT    NOT NULL,
       Word           TEXT    NOT NULL,
       Item_id        INT    NOT NULL,
       Type     INT    NOT NULL,
       Frequece  INT    NOT NULL,
       Confidence REAL NOT NULL);'''

relation type 目前只有0，belong to 这种
create_concept_relation_tbl_sql = '''CREATE TABLE Concept_relation_tbl
       (ID INT PRIMARY KEY AUTOINCREMENT NOT NULL,
       Concept1       INT    NOT NULL,
       Concept2       INT    NOT NULL,
       Relation_type  INT    NOT NULL);'''





#
# old version
## 是一种只提取有用的concept的方案，针对百度信息抽取比赛定制一个小型kb
0, init.sh
init_data 中执行extract_know_entities.py 提取百度信息抽取数据中所有实体
将主谓宾，百度百科(entities)，百度信息抽取中所有名词性实体合并为all_entities

1.1, init kb
将all_entities导入为Concept，利用主谓关系更新Method——table和Concept的methods属性

1.2，init kb2
利用百度信息抽取数据 更新Concept_relation_table

1.3, init kb3
cn pedia 和wiki relation 导入 项目外处理好的
cn pedia 198万 wiki 46万  交集7万 重复数据3万
Concept_relation_table 去重
