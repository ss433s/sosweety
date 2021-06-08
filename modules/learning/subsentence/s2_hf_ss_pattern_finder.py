# 先找hf word再把word前后content简化后找句式
# 目前只有pos，不太有意义
# 测试过，暂未启用

# import time
import os, sys
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

from modules.utils.utils import count_value


class SubsentencePatternFinder(object):
    def __init__(self):
        return

    def learning(self, unsolved_pos_tag_file_path, learning_file_dir, cutoff=50):
        # unsolved_pos_tag_file_dir = os.path.dirname(unsolved_pos_tag_file_path)
        if not os.path.exists(learning_file_dir):
            os.makedirs(learning_file_dir)

        with open(unsolved_pos_tag_file_path) as unsolved_pos_tag_file:
            count = 0
            high_freq_word_set = set()
            word_freq_dict = {}
            line = unsolved_pos_tag_file.readline()
            while line:
                count += 1
                if count % 10000 == 0:
                    print('Looking for high frequent word, parsed %s sentence' % count)
                pos_tags = json.loads(line)
                for word, pos_tag in pos_tags:
                    if pos_tag != 'PU':
                    # if pos_tag != 'PU' and pos_tag != 'NN':
                        if word in word_freq_dict:
                            word_freq_dict[word] += 1
                            if word_freq_dict[word] >= cutoff:
                                high_freq_word_set.add(word)
                        else:
                            word_freq_dict[word] = 1

                line = unsolved_pos_tag_file.readline()

        # 单个词pattern
        # todo 简化前后句效果才能出来
        learning_file_name = 'single_word_pattern'
        learning_file_path = os.path.join(learning_file_dir, learning_file_name)
        learning_file = open(learning_file_path, 'w')

        print(len(high_freq_word_set))
        with open(unsolved_pos_tag_file_path) as unsolved_pos_tag_file:
            count = 0
            line = unsolved_pos_tag_file.readline()
            while line:
                count += 1
                if count % 5000 == 0:
                    print('parsed %s sentence' % count)
                pos_tags = json.loads(line)
                for i in range(len(pos_tags)):
                    word = pos_tags[i][0]
                    if word in high_freq_word_set:
                        # print(pos_tags)
                        start_list = pos_tags[:i]
                        start_tag_list = [pos_tag[1] for pos_tag in start_list]
                        end_list = pos_tags[i+1:]
                        end_tag_list = [pos_tag[1] for pos_tag in end_list]
                        full_list = start_tag_list + [word] + end_tag_list
                        new_pattern = '|'.join(full_list)
                        learning_file.write(new_pattern + '\n')
                line = unsolved_pos_tag_file.readline()

        learning_file.close()
        learning_stat_file_path = os.path.join(learning_file_dir, 'ordered_single_word_ss_pattern.csv')
        count_value(learning_file_path, learning_stat_file_path, cutoff=2)
        return


unsolved_pos_tag_file_path = '/mnt/d/ubuntu/projects/new_sosweety/sosweety/data/train_0220_23_19/train_result/unsolved_pos_tag_file'
learning_file_dir = '/mnt/d/ubuntu/projects/new_sosweety/sosweety/data/train_0220_23_19/learning_result/ss_pattern_finder'
# unsolved_pos_tag_file_path = '/mnt/d/ubuntu/projects/new_sosweety/sosweety/data/train/train_result/yaoqing'
a = SubsentencePatternFinder()
a.learning(unsolved_pos_tag_file_path, learning_file_dir)
