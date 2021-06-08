import os, sys
import json, time
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

from modules.learning.parse_result_analyser import ParseResultAnalyser
# from modules.sParser.parser_class import Word
from modules.knowledgebase.kb import KnowledgeBase
from modules.sParser.sParser import sParser
from modules.utils.utils import tuples2parse_result


class Trainer():
    def __init__(self, KB, multiprocess=1):
        self.multiprocess = multiprocess
        self.KB = KB

    # 借助第三方分词工具的分词
    def raw_parse(self, corpus_file_path, parse_result_file_path, parser="hanlp"):
        myparser = sParser(self.KB)
        parse_result_file = open(parse_result_file_path, 'w')
        with open(corpus_file_path) as corpus_file:
            line = corpus_file.readline()
            count = 0
            while line:
                count += 1
                if count % 5000 == 0:
                    print('parsed %s sentence' % count)

                text = line.strip()
                try:
                    ss_pos_tags = myparser.text2ss_pos_tags(text)
                    for pos_tags in ss_pos_tags:
                        parse_result_file.write(json.dumps(pos_tags, ensure_ascii=False) + '\n')
                except Exception:
                    print('line %s decode error' % count)

                line = corpus_file.readline()
        parse_result_file.close()
        return

    def analyse(self, pos_tag_file_path, output_dir_path):
        analyser = ParseResultAnalyser(self.KB, multiprocess=self.multiprocess)
        analyser.analyse(pos_tag_file_path, output_dir_path)
        return

    # input file 每行是一个parse result的json string
    def train(self, input_file_path, output_dir_path, fast_check_mode=True, analyse=True):

        parse_result_dir = 'parse_result'
        parse_result_dir = os.path.join(output_dir_path, parse_result_dir)

        tmp_file_dir = os.path.join(parse_result_dir, 'tmp')
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

        print('Begin to parse at:')
        print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))
        p_list = []
        for i in range(p_count):
            p = Process(target=single_file_parse, args=(file_list[i], fast_check_mode))
            p_list.append(p)
            p.start()

        for p in p_list:
            p.join()

        # 合并tmp中的unsolved和solved文件
        unsolved_file_path = os.path.join(parse_result_dir, 'unsolved_file')
        cmd = 'cat ' + tmp_file_name_prefix + '*.unsolved >' + unsolved_file_path
        fd = os.popen(cmd)
        fd.read()
        unsolved_pos_tag_file_path = os.path.join(parse_result_dir, 'unsolved_pos_tag_file')
        cmd = 'cat ' + tmp_file_name_prefix + '*.unsolved_pos_tag >' + unsolved_pos_tag_file_path
        fd = os.popen(cmd)
        fd.read()
        solved_file_path = os.path.join(parse_result_dir, 'solved_file')
        cmd = 'cat ' + tmp_file_name_prefix + '*.solved >' + solved_file_path
        fd = os.popen(cmd)
        fd.read()

        if analyse:
            analyse_result_dir = 'analyse_result'
            analyse_result_dir = os.path.join(output_dir_path, analyse_result_dir)
            self.analyse(unsolved_pos_tag_file_path, analyse_result_dir)

        print('Train finished at:')
        print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))

        return


def single_file_parse(input_file_path, fast_check_mode):
    KB = KnowledgeBase(memory_mode=False)
    parser = sParser(KB)
    unsolved_file_path = input_file_path + '.unsolved'
    unsolved_file = open(unsolved_file_path, 'w')
    unsolved_pos_tag_file_path = input_file_path + '.unsolved_pos_tag'
    unsolved_pos_tag_file = open(unsolved_pos_tag_file_path, 'w')
    solved_file_path = input_file_path + '.solved'
    solved_file = open(solved_file_path, 'w')

    input_file_name = os.path.basename(input_file_path)
    print('Begin to parse %s' % input_file_name)
    print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))

    total_ss = 0
    parsed_ss = 0

    input_file = open(input_file_path)
    line = input_file.readline()
    while line:

        total_ss += 1
        if total_ss % 15000 == 0:
            print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))
            print('total ss is %s, parsed is %s' % (total_ss, parsed_ss))

        line = line.strip()
        pos_tags = json.loads(line)
        parse_result = tuples2parse_result(pos_tags)
        if fast_check_mode:
            all_results = parser.fast_check_phrase(parse_result)
        else:
            print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))
            all_results = parser.check_phrase_with_known_entity(parse_result)
            print(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()))
        if all_results == []:
            unsolved_file.write(json.dumps(pos_tags, ensure_ascii=False) + '\t' + 'no_parse_result\n')
            unsolved_pos_tag_file.write(json.dumps(pos_tags, ensure_ascii=False) + '\n')
        else:
            # ##################
            # # with logic check
            # ##################
            # logic_check_result = logic_check(all_results[0])
            # # if len(logic_check_result) > 0 and all(logic_check_result):
            # if all(logic_check_result):
            #     # print(all_results[0])
            #     parsed_ss += 1
            #     solved_file.write(json.dumps(sub_sentence_pos_tags, ensure_ascii=False) + '\n')
            # else:
            #     unsolved_file.write(json.dumps(sub_sentence_pos_tags, ensure_ascii=False) + '\t' + 'logic_mistake\n')

            ##################
            # without logic check
            ##################
            solved_file.write(str(all_results[0]) + '\n')

        line = input_file.readline()

    solved_file.close()
    unsolved_file.close()

    return
