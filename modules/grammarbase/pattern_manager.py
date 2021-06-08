import os, sys
sys.path.append("..")
sys.path.append("../..")
# from sParser.parser_class import Word, ParseResult
# from sParser.sParser import fast_check_phrase, logic_check
# from utils.utils import stanford_simplify


# 当前路径和项目root路径， 可以根据需求改变../..
this_file_path = os.path.split(os.path.realpath(__file__))[0]
root_path = os.path.abspath(os.path.join(this_file_path, ".."))

phrase_file_name = 'phrase_pattern'
phrase_file_path = os.path.join(this_file_path, phrase_file_name)
ss_file_name = 'ss_pattern'
ss_file_path = os.path.join(this_file_path, ss_file_name)

modify_file = 0  # 0改phrase 1改ss

if modify_file == 0:
    with open(phrase_file_path) as file:
        line = file.readline()
        while line:
            pass

        line = file.readline()


if modify_file == 1:
    with open(ss_file_path) as file:
        line = file.readline()
        while line:
            pass

        line = file.readline()
