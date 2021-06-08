###################
# 定义和读取知识库
###################
class Concept(object):
    def __init__(self, concept_id, word, methods, properties):
        self.concept_id = concept_id
        self.word = word
        self.methods = methods
        self.properties = properties


class Method(object):
    def __init__(self, method_id, word, code='-'):
        self.method_id = method_id
        self.word = word
        self.code = code


class Fact(object):
    def __init__(self, fact_id, concept1=None, restriction1=None,
                                concept2=None, restriction2=None,
                                relation=None, relation_restriction=None,
                                time=None, location=None,
                                confidence=None):
        self.fact_id = fact_id
        self.concept1 = concept1
        self.restriction1 = restriction1
        self.concept2 = concept2
        self.restriction2 = restriction2
        self.relation = relation
        self.relation_restriction = relation_restriction
        self.time = time
        self.location = location
        self.confidence = confidence
