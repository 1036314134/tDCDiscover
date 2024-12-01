import copy
import functools
from additional_functions.Evidence import Evidences


class ECT:
    """
    上下文证据，格式为一个左元组，多个右元组，以及它们共享的证据
    """
    def __init__(self, t, tids, sat):
        self.t = t  # 左元组
        self.tids = tids  # 右元组集合
        self.sat = sat  # 证据

    def addtid(self, t2):
        self.tids.add(t2)

    def changetids(self, tids):
        self.tids = tids

    def addsat(self, sat):
        self.sat = sat

    def t(self):
        return self.t

    def tids(self):
        return self.tids

    def sat(self):
        return self.sat


def equals(pilsk, v):
    """
    返回相等元组
    :param pilsk: “值-等于该值的元组”的映射
    :param v: 目标值
    :return: 与目标值相等元组
    """
    if pilsk.get(v) is None:
        return None
    else:
        return pilsk.get(v)


def CategoricalStage(t, A, ECTs, fix):
    """
    根据相等谓词更新ECTs
    :param t: 目标值
    :param A: 目标值所涉及的”值-等于该值的元组“映射
    :param ECTs: 可能需要修复的当前ECTs
    :param fix: 修复谓词组合
    :return: 更新后的ECTs
    """
    equal = equals(A, t)
    if len(equal) == 1:
        return ECTs
    new_ECTs = []
    for ect in ECTs:
        flag = True
        fixequal = equal.intersection(ect.tids)  # 交集
        if len(fixequal) > 0:
            if ect.tids == fixequal:
                flag = False
            else:
                ect.changetids(ect.tids.difference(fixequal)) # 差集
            new_sat = ect.sat ^ fix
            new_ECTs.append(ECT(ect.t, fixequal, new_sat))
        if flag:
            new_ECTs.append(ect)
    return new_ECTs


def NumericalStage(t, A, ECTs, fix):
    """
    根据大于谓词更新ECTs
    :param t: 目标值
    :param A: 目标值所涉及的”值-大于该值的元组“映射
    :param ECTs: 可能需要修复的当前ECTs
    :param fix: 修复谓词组合
    :return: 更新后的ECTs
    """
    great = equals(A, t)
    if not great:
        return ECTs
    new_ECTs = []
    for ect in ECTs:
        fixgreat = great.intersection(ect.tids)  # 交集
        if len(fixgreat) > 0:
            new_sat = ect.sat ^ fix
            new_ECTs.append(ECT(ect.t, fixgreat, new_sat))
        ect.changetids(ect.tids.difference(fixgreat)) # 差集
        if ect.tids:
            new_ECTs.append(ect)
    return new_ECTs


def ects_function_thr(header, I, pres_space, readable_pres_space, threshold):
    """
    ECT算法构建证据集
    :param header:数据实例的关系模式
    :param I: 数据实例
    :param pres_space:编号格式谓词空间
    :param readable_pres_space: 字符格式谓词空间
    :param threshold: 阈值集合
    :return:
    """
    # 通过谓词空间构建属性到阈值的映射表
    thr_dict = {}
    for pres in pres_space:
        if thr_dict.get(pres[0]) is None:
            thr_dict[pres[0]] = pres[3]
    # 构建”值-元组“映射，其中每个映射中元组共享相同值
    hash1 = {}
    # 遍历属性
    for k in range(1, len(header)):
        temp_dict = {}
        for i in range(0, len(I)):
            # 对于未出现的值创建新映射
            if temp_dict.get(I[i][k]) is None:
                temp_dict[I[i][k]] = set()
            # 将元组加入该值当中
            temp_dict[I[i][k]].add(i)
        # 对于非字符属性有更多操作
        if '(String)' not in header[k]:
            # 将创建好的映射按值由小到大排序
            sort_temp_dict = dict(sorted(temp_dict.items(), key=lambda x: x[0]))
            # 遍历附近映射，将差值小于阈值的映射中的元组都加入映射中
            temp_dict = copy.deepcopy(sort_temp_dict)
            keys = list(temp_dict.keys())
            i = 0
            j = 1
            # 先判断阈值下限
            while j < len(keys):
                if keys[i] - keys[j] >= threshold[thr_dict[k]][0]:
                    temp_dict[keys[i]] = temp_dict[keys[i]].union(sort_temp_dict[keys[j]])
                    j = j + 1
                else:
                    i = i + 1
                    j = i + 1
            i = 0
            j = 1
            # 再判断阈值上限
            while j < len(keys):
                if keys[j] - keys[i] <= threshold[thr_dict[k]][1]:
                    temp_dict[keys[j]] = temp_dict[keys[j]].union(sort_temp_dict[keys[i]])
                    j = j + 1
                else:
                    i = i + 1
                    j = i + 1
        # 将所有相等的“值-映射”加入到hash1中
        hash1[k] = temp_dict
    # 再通过hash1算出一个大于的“值-映射”，记为hash2
    hash2 = copy.deepcopy(hash1)
    for key in hash2:
        last_key = None
        for key2 in hash2[key]:
            if last_key is not None:
                hash2[key][key2] = hash2[key][key2].union(hash2[key][last_key])
            last_key = key2
    # 去掉相等的部分，只保留值大于的映射
    for key in hash2:
        for key2 in hash2[key]:
            hash2[key][key2] = hash2[key][key2].difference(hash1[key][key2])
    """
    初始化ecp
    """
    pres_space_init = set()
    # ≠ < ≤
    for k in range(0, len(pres_space)):
        if pres_space[k][1] == "≠" or pres_space[k][1] == "<" or pres_space[k][1] == "≤":
            pres_space_init.add(readable_pres_space[k])
    ECTs = {}
    # 按左元组分类元组对，假设每个元组对一开始都满足≠ < ≤
    for i in range(0, len(I)):
        ect = ECT(i, set(), set())
        for j in range(i+1, len(I)):
            ect.addtid(j)
        ect.addsat(copy.deepcopy(pres_space_init))
        ECTs[i] = [ect]
    """
    修正ECT '=', '≠', '<', '>', '≤', '≥'
    """
    for k in range(0, len(pres_space)):
        pres = pres_space[k]
        if pres[1] == "=":
            if '(String)' in header[pres[0]]:
                fix = {readable_pres_space[k], readable_pres_space[k + 1]}
            else:
                fix = {readable_pres_space[k], readable_pres_space[k + 1], readable_pres_space[k + 2],
                       readable_pres_space[k + 5]}
            for i in range(0, len(I) - 1):
                ECTs[i] = CategoricalStage(I[i][pres[0]], hash1[pres[0]], ECTs[i], fix)
        if pres[1] == ">":
            fix = {readable_pres_space[k - 1], readable_pres_space[k], readable_pres_space[k + 1],
                   readable_pres_space[k + 2]}
            for i in range(0, len(I) - 1):
                ECTs[i] = NumericalStage(I[i][pres[0]], hash2[pres[0]], ECTs[i], fix)
    """
    去除重复证据
    """
    evis_set = []
    for i in range(0, len(I) - 1):
        for ect in ECTs[i]:
            flag = True
            for old_evi in evis_set:
                if old_evi.sat == ect.sat:
                    old_evi.addtime(len(ect.tids))
                    flag = False
                    break
            if flag:
                evis_set.append(Evidences(len(ect.tids), ect.sat))
    """
    计算单个谓词覆盖度
    """
    evis_cover_dict = {'max': len(I) * (len(I) - 1) / 2}
    for readable_pres in readable_pres_space:
        count = 0
        for evi in evis_set:
            if readable_pres in evi.sat:
                count = count + evi.num
        evis_cover_dict[readable_pres] = count

    return evis_set, evis_cover_dict


def Rank_P_negative(E, preds):
    cover = []
    for p in preds:
        count = 0
        for evi in E:
            if p in evi.sat:
                count = count + evi.num
        cover.append((p, count))
    cover.sort(key=functools.cmp_to_key(compare), reverse=True)
    P_ranked = []
    for t in cover:
        if t[1] != 0:
            P_ranked.append(t[0])
    return P_ranked


def is_NIL(next_E, preds):
    for e in next_E:
        flag = True
        for p in preds:
            if p in e.sat:
                flag = False
                break
        if flag:
            return True
    return False


def negative_covers_search(path, preds, E, MC, t_uncover, t_aim):
    '''
    查看是否覆盖
    '''
    if t_uncover <= t_aim:
        MC.append(path)
        return MC

    if len(E) != 0 and len(preds) == 0:
        return MC
    '''
    限制每条搜索路径长度为5
    '''
    if len(path) >= 5:
        return MC
    '''
    谓词排序
    '''
    preds = Rank_P_negative(E, preds)

    for i in range(0, len(preds)):
        p = preds[i]
        next_preds = copy.deepcopy(preds[i + 1:])
        '''
        根据平凡性剪枝, 相同属性生成谓词只能存在一个
        '''
        if cut_by_triviality(path, p):
            continue
        '''
        更新证据集
        '''
        next_t_uncover = 0
        next_E = []
        for evi in E:
            if p not in evi.sat:
                next_E.append(evi)
                next_t_uncover = next_t_uncover + evi.num
        if not is_NIL(next_E, preds):
            next_path = copy.deepcopy(path)
            next_path.append(p)
            MC = negative_covers_search(next_path, next_preds, next_E, MC, next_t_uncover, t_aim)

    return MC


def cut_by_triviality(X, pres):
    """
    依据平凡性剪枝
    :param X: 当前已选谓词
    :param pres: 待加入谓词
    :return: 是否存在平凡性需要剪枝
    """
    flag = False
    if len(X) != 0:
        pres = pres.split(' ')
        for p in X:
            p = p.split(' ')
            if p[0] == pres[0] and p[2] == pres[2]:
                flag = True
                break
    return flag


def cut_by_MC(X, MC):
    flag = False
    for cover in MC:
        flag = True
        for pres in cover:
            if pres not in X:
                flag = False
                break
        if flag:
            break
    return flag


def compare(a, b):
    if a[-1] > b[-1]:
        return 1
    elif a[-1] == b[-1]:
        return 0
    else:
        return -1