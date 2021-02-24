class Node(object):
    def __init__(self,data):
        self.data = data
        self.skip = None
        
    def __str__(self):
        if self.data:
            return str(self.data)
        raise ValueError('Node Data NOT Exist!')

        
class Vector(object):
    def __init__(self,datas = []):
        self.length = 0
        self.nodes = []
        for data in datas:
            self.insert(data)
        
    def sort(self):
        self.nodes = sorted(self.nodes, key=lambda node:node.data)
        return self
        
    def insert(self, data):
        self.nodes.append(Node(data))
        self.length += 1
        return self
        
    def show(self):
        datas = []
        for node in self.nodes:
            datas.append(str(node.data))
        print('->'.join(datas))
        
    def __str__(self):
        datas = []
        for node in self.nodes:
            datas.append(str(node.data))
        return '->'.join(datas)
        
    def __len__(self):
        return self.length

    def __getitem__(self, idx):
        try: 
            return self.nodes[idx]
        except Exception as e:
            print(e)
    
    def make_skip(self, gap=5):
        self.sort()
        for idx in list(range(0,self.length,gap))[:-1]:
            self.nodes[idx].skip = idx + gap

def save_obj(obj, name):
    import pickle
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
    import pickle
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)

def and_query(vec_A, vec_B, use_skip=True):
    if len(vec_A) == 0 or len(vec_B) == 0:
        return Vector()
    res = []
    ka = 0
    kb = 0
    if use_skip:
        while ka < len(vec_A) and kb < len(vec_B):
            if vec_A[ka].data == vec_B[kb].data:
                res.append(vec_A[ka].data)
                ka += 1
                kb += 1
            elif vec_A[ka].data < vec_B[kb].data:
                if vec_A[ka].skip != None and vec_A[vec_A[ka].skip].data <= vec_B[kb].data:
                    while vec_A[ka].skip != None and vec_A[vec_A[ka].skip].data <= vec_B[kb].data:
                        ka = vec_A[ka].skip
                else:
                    ka += 1
            else:
                if vec_B[kb].skip != None and vec_B[vec_B[kb].skip].data <= vec_A[ka].data:
                    while vec_B[kb].skip != None and vec_B[vec_B[kb].skip].data <= vec_A[ka].data:
                        kb = vec_B[kb].skip
                else:
                    kb += 1
        return Vector(res)
    else:
        while ka < len(vec_A) and kb < len(vec_B):
            if vec_A[ka].data == vec_B[kb].data:
                res.append(vec_A[ka].data)
                ka += 1
                kb += 1
            elif vec_A[ka].data < vec_B[kb].data:
                ka += 1
            else:
                kb += 1
        return Vector(res)

def and_not_query(vec_A, vec_B):
    res = []
    ka = 0
    kb = 0
    while ka < len(vec_A) and kb < len(vec_B) - 1:
        while kb < len(vec_B) - 1 and vec_B[kb+1].data < vec_A[ka].data:
            kb += 1
        if kb == len(vec_B) - 1:
            break
        if vec_B[kb+1].data == vec_A[ka].data:
            ka += 1
            kb += 1
        else:
            if vec_B[kb].data == vec_A[ka].data:
                ka += 1
            elif vec_B[kb].data > vec_A[ka].data:
                res.append(vec_A[ka].data)
                ka += 1
            else:
                res.append(vec_A[ka].data)
                ka += 1
    if kb == len(vec_B) - 1 and ka < len(vec_A):
        for idx in range(ka,len(vec_A)):
            res.append(vec_A[idx].data)
    return Vector(res)

def not_query(vec_A, COUNT):
    if len(vec_A) == 0:
        return Vector(list(range(1,COUNT+1)))
    idx = 0
    res = []
    flag = vec_A[idx].data
    for num in range(1,COUNT+1):
        if num != flag:
            res.append(num)
        else:
            if idx == len(vec_A) - 1:
                pass
            else:
                idx += 1
            flag = vec_A[idx].data    
    return Vector(res)

def or_query(vec_A, vec_B):
    res = []
    ka = 0
    kb = 0
    while ka < len(vec_A) and kb < len(vec_B):
        if vec_A[ka].data == vec_B[kb].data:
            res.append(vec_A[ka].data)
            ka += 1
            kb += 1
        elif vec_A[ka].data < vec_B[kb].data:
            res.append(vec_A[ka].data)
            ka += 1
        else:
            res.append(vec_B[kb].data)
            kb += 1
    if ka < len(vec_A):
        for idx in range(ka,len(vec_A)):
            res.append(vec_A[idx].data)
    if kb < len(vec_B):
        for idx in range(kb,len(vec_B)):
            res.append(vec_B[idx].data)
    return Vector(res)

def parse_query(inverted_index, query, use_skip=True):
    import re

    sub_query_list = re.split(r'[&]', query)
    
    sub_query = sub_query_list[0].replace(" ","").replace("(","").replace(")","")
    if "|" in sub_query:
        text_list = re.split(r'[|]', sub_query)
        if "!" in text_list[0]:
            cur_vec = not_query(inverted_index[text_list[0][1:]], COUNT)
        else:
            cur_vec = inverted_index[text_list[0]]
        for text in text_list[1:]:
            if "!" in text:
                cur_vec = or_query(cur_vec, not_query(inverted_index[text[1:]], COUNT))
            else:
                cur_vec = or_query(cur_vec, inverted_index[text])
    else:
        if "!" in sub_query:
            cur_vec = not_query(inverted_index[sub_query.replace("!","")], COUNT)
        else:
            cur_vec = inverted_index[sub_query]

    for sub_query in sub_query_list[1:]:
        sub_query = sub_query.replace(" ","").replace("(","").replace(")","")
        if "|" in sub_query:
            text_list = re.split(r'[|]', sub_query)
            if "!" in text_list[0]:
                tmp_vec = not_query(inverted_index[text_list[0][1:]], COUNT)
            else:
                tmp_vec = inverted_index[text_list[0]]
            for text in text_list[1:]:
                if "!" in text:
                    tmp_vec = or_query(tmp_vec, not_query(inverted_index[text[1:]], COUNT))
                else:
                    tmp_vec = or_query(tmp_vec, inverted_index[text])
            cur_vec = and_query(cur_vec, tmp_vec, use_skip=use_skip)
        else:
            if "!" in sub_query:
                cur_vec = and_not_query(cur_vec, inverted_index[sub_query.replace("!","")])
            else:
                cur_vec = and_query(cur_vec, inverted_index[sub_query], use_skip=use_skip)    
    return cur_vec

def res_show(res_vec):
    import re
    for idx in range(len(res_vec)):
        num = res_vec[idx].data
        html = f'.\cacm\CACM-{str(num).zfill(4)}.html'
        with open(html,'r',encoding="utf-8") as f:
            html = f.readlines()

        tmp = []
        for line in html:
            if '<' in line or '\t' in line or line == '\n':
                pass
            else:
                tmp.append(line[:-1])

        title = ""
        for line in tmp:
            if "CACM" in line:
                break
            title += " " + line
        title = re.sub(' +', ' ', title)
        
        print(f"CACM-{str(num).zfill(4)}.html:\n",title)
        print("------------------------------------------------------------------------------")
    
punc = '\[\]~`!#$%&*_+=|\';":/.,?><~·！@#￥%……&*（）——+-=“：’；、。，？》《{}()^' #-

COUNT = 3204