# phrase pattern finder

## 两种思路，1，直接找组合直接做特征统计；2，先找高频词再找组合然后特征统计
## 多个方案，记录如下
&nbsp;
&nbsp;

## 1 pos phrase finder  
### 旧版本文件，这种类型的phase太少了，后续用不上  
&nbsp;
&nbsp;


## 2 noun phrase finder
### 在连续三个名词的组合中寻找phrase pattern，初始化有意义，后期适用范围小
&nbsp;
### 做了大量的优化，但意义不大
### 对所有的内容先进行了提取汇总，再进行下一步分析，避免反复查库，可能多此一举了。。。。(还是很有必要的，可以尝试边读文件边提取，不过读文件只要20s)
### 具体步骤
#### 1， 提取所有名词，构建名词到concept id的字典和名词set
#### 2， 查找所有名词的上位词，构建所有上位词set
#### 3， 构建所有上位词的feature（就是一个{'concept': concept_id, 'word': word}的字典，方便记录和查看）
#### 4， 再遍历一遍文件，遇到名词从之前构建好的字典中直接调用

### 旧版找全部的2-3次组合，新版只找nn组合
### 1226版找上层关系时，递归查询所有上级，导致无意义phrase过多，改为只查单级关系
&nbsp;
&nbsp;


## 3 double word phrase finder
### 找到未解析句中的高频词(hf_word)，在前后三的范围内（不包括该高频词自己）去找共同出现的高频词（co_word）
### 所有包含了co word的组合都会被转换成字符串去解析，hf_word和co_word保留字面，其他词保留词性
### 因为要确定cutoff ，所以遍历了三遍文件
### todo应该转换成feature list而不是str的
&nbsp;
&nbsp;


# new concept
## 特征中全部为词的就是new concept
&nbsp;
&nbsp;

# new upper concept
## 某高频词附近出现的高频组合