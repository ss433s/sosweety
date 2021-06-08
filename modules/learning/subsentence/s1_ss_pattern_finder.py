import os, sys
import json
import time
import math
from multiprocessing import Process

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

from modules.sParser.parser_class import Word
from modules.sParser.sParser import sParser
from modules.utils.utils import count_value_with_examples, tuples2parse_result, csv_to_xlsx
from modules.knowledgebase.kb import KnowledgeBase
import csv


class S1SubsentencePatternFinder():
    def __init__(self, KB, multiprocess=1):
        self.KB = KB
        self.multiprocess = multiprocess

    # input file 为每行一个parse result的json string
    def analyse(self, input_file_path, output_dir_path, cutoff=10):

        # prepare output dir
        ss_pattern_dir = os.path.join(output_dir_path, 'ss_pattern')
        tmp_file_dir = os.path.join(ss_pattern_dir, 'tmp')
        if not os.path.exists(tmp_file_dir):
            os.makedirs(tmp_file_dir)

        p_count = self.multiprocess

        # 文件分割
        with open(input_file_path) as f:
            line = f.readline()
            count = 0
            while line:
                count += 1
                line = f.readline()
        file_length = count

        file_list = []
        with open(input_file_path) as f:
            average = math.ceil(file_length/p_count)
            tmp_file_name_prefix = os.path.join(tmp_file_dir, os.path.basename(input_file_path))

            line = f.readline()
            count = 0
            file_count = 0
            tmp_file_name = tmp_file_name_prefix + str(file_count+1)
            file_list.append(tmp_file_name)
            tmp_file = open(tmp_file_name, 'w')
            while line:
                this_line_count = count // average
                if file_count == this_line_count:
                    tmp_file.write(line)
                else:
                    tmp_file.close()
                    tmp_file_name = tmp_file_name_prefix + str(this_line_count+1)
                    tmp_file = open(tmp_file_name, 'w')
                    file_list.append(tmp_file_name)
                    tmp_file.write(line)
                    file_count = this_line_count
                count += 1
                line = f.readline()
            tmp_file.close()

        print('Begin to checkout subsentence patterns')
        print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))
        p_list = []
        for i in range(p_count):
            p = Process(target=single_file_analyse, args=(file_list[i],))
            p_list.append(p)
            p.start()

        for p in p_list:
            p.join()

        output_file_path = os.path.join(ss_pattern_dir, 'ss_pattern_raw')
        cmd = 'cat ' + tmp_file_name_prefix + '*result >' + output_file_path
        fd = os.popen(cmd)
        fd.read()
        ordered_stat_file_path = os.path.join(ss_pattern_dir, 'ordered_stat_file.csv')
        count_value_with_examples(output_file_path, ordered_stat_file_path, cutoff=cutoff)
        ordered_stat_xls_file_path = os.path.join(ss_pattern_dir, 'ordered_stat_file.xlsx')

        # stat file with example to ss pattern file
        tmp_file = os.path.join(ss_pattern_dir, 'tmp.csv')
        tmp_file_writer = csv.writer(open(tmp_file, 'w+', encoding='utf-8-sig'))
        tmp_file_writer.writerow(['parse_str', 'freq', 'ss_type', 'meaning', 'ss_type2', 'examples'])
        ordered_stat_file_reader = csv.reader(open(ordered_stat_file_path, encoding='utf-8-sig'))
        for row in ordered_stat_file_reader:
            tmp_file_writer.writerow([row[0], row[1], '', '', '', row[2]])
        csv_to_xlsx(tmp_file, ordered_stat_xls_file_path)
        # os.remove(tmp_file)

        print('Subsentence analysis finished at:')
        print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))

        return


def single_file_analyse(input_file_path):
    KB = KnowledgeBase(memory_mode=False)
    parser = sParser(KB)
    ss_pattern_file_path = input_file_path + '.result'
    ss_pattern_file = open(ss_pattern_file_path, 'w')

    input_file_name = os.path.basename(input_file_path)
    print('Begin to checkout ss patterns of %s' % input_file_name)
    print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))

    # todo qa_word要不要单独处理
    # todo 加入NN|NN
    def checkout_pos_ss_pattern(simplified_parse_result):
        result_str = []
        for item in simplified_parse_result.contents:
            if item.pos_tag == 'QA':
                result_str.append(item.value)
            else:
                result_str.append(item.pos_tag)
        ss_pattern_file.write('|'.join(result_str) + '\t' + '|'.join(simplified_parse_result.words) + '\n')
        return

    # todo 真有这种吗？
    # def checkout_concept_ss_pattern(parse_result):
    #     new_parse_result = parser.fast_check_parse_result(parse_result)
    #     result_str = []
    #     for item in new_parse_result.contents:
    #         if isinstance(item, Word):
    #             result_str.append(item.value)
    #         else:
    #             result_str.append(item.pos_tag)
    #     ss_pattern_file.write('|'.join(result_str) + '\t' + '|'.join(parse_result.words) + '\n')
    #     return

    # 调用new ss finder？
    def checkout_word_ss_pattern(simplified_parse_result):
        result_str = []
        for item in simplified_parse_result.contents:
            if isinstance(item, Word):
                result_str.append(item.value)
            else:
                result_str.append(item.pos_tag)
        ss_pattern_file.write('|'.join(result_str) + '\t' + '|'.join(simplified_parse_result.words) + '\n')
        return

    input_file = open(input_file_path)

    line = input_file.readline()
    count = 0
    while line:
        count += 1
        if count % 15000 == 0:
            print('count %s sentences' % count)
        line = line.strip()
        pos_tags = json.loads(line)
        ss_parse_result = tuples2parse_result(pos_tags)
        simplified_parse_result = parser.fast_check_parse_result(ss_parse_result)
        checkout_pos_ss_pattern(simplified_parse_result)
        line = input_file.readline()

    ss_pattern_file.close()
    print('%s ss check finished at:' % input_file_name)
    print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))

    return
