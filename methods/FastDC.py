import copy
import functools
from additional_functions.Evidence import Evidences


def fast_dc(pres_space, I, threshold, readable_pres_space):
    """
    FAST-DC算法的构建证据集部分
    :param pres_space: 编号格式的谓词空间
    :param I: 数据集实例
    :param threshold: 阈值集合
    :param readable_pres_space: 字符格式的谓词空间
    :return: 返回完整证据集以及用于计算覆盖度的字典
    """
    # 给出空的证据集以及初始字典，字典第一个元素为元组对总数
    evis_set = []
    evis_cover_dict = {'max': len(I) * (len(I) - 1) / 2}
    for readable_pres in readable_pres_space:
        evis_cover_dict[readable_pres] = 0
    # 遍历元组对
    for i in range(0, len(I)-100):
        for j in range(i + 1, i+101):
            t1 = I[i]
            t2 = I[j]
            evi = Evidences(1, set())
            # 遍历谓词空间，看该元组对满足哪些谓词
            for k in range(0, len(pres_space)):
                if judge_pres(pres_space[k], t1, t2, threshold):
                    # 若满足谓词，则加入该元组对的证据中去
                    evi.addpres(readable_pres_space[k])
                    # 该谓词的覆盖度+1
                    evis_cover_dict[readable_pres_space[k]] = evis_cover_dict[readable_pres_space[k]] + 1
            # 查看当前证据是否已经被加入证据集中
            flag = True
            for old_evi in evis_set:
                # 若有，则增加该证据的出现次数
                if old_evi.sat == evi.sat:
                    old_evi.addtime(1)
                    flag = False
                    break
            # 否则将该证据加入证据集
            if flag:
                evis_set.append(evi)
    # 返回证据集以及覆盖度字典
    return evis_set, evis_cover_dict


def judge_pres(pres, t1, t2, threshold):
    """
    加入阈值后的谓词满足判断，
    :param pres: 编号格式谓词列表
    :param t1: 元组1
    :param t2: 元组2
    :param threshold: 阈值集合
    :return: 谓词是否满足
    """
    first = t1[pres[0]]
    second = t2[pres[2]]
    threshold_now = threshold[pres[3]]
    if pres[3] == 0:
        '''
        字符属性处理
        '''
        if pres[1] == '=':
            return first == second
        else:
            return not (first == second)
    else:
        '''
        数值属性处理
        '''
        threshold_down = threshold_now[0]
        threshold_up = threshold_now[1]
        if pres[1] == '=':
            return second + threshold_down <= first <= second + threshold_up
        elif pres[1] == '≠':
            return first < second + threshold_down or first > second + threshold_up
        elif pres[1] == '>':
            return first > second + threshold_up
        elif pres[1] == '<':
            return first < second + threshold_down
        elif pres[1] == '≥':
            return first >= second + threshold_down
        elif pres[1] == '≤':
            return first <= second + threshold_up


def FastDC_minimal_covers_search(evis_set_curr, X, pres_curr, MC, t_uncover, t_aim):
    """
    :param evis_set_curr: 当前未被覆盖证据
    :param X: 当前已选谓词
    :param pres_curr: 候选谓词集
    :param MC: 当前搜索到的最小覆盖集
    :param t_uncover: 未覆盖元组数
    :param t_aim: 可容忍未覆盖元组数
    :return: 完整最小覆盖集
    """
    '''
    基于MC的子集剪枝
    '''
    if cut_by_MC(X, MC):
        return MC
    '''
    查看是否覆盖
    '''
    if t_uncover <= t_aim:
        MC.append(X)
        return MC

    if len(pres_curr) == 0:
        return MC
    '''
    限制每条搜索路径长度为5
    '''
    if len(X) >= 5:
        return MC
    '''
    谓词排序
    '''
    pres_curr = Rank_P(evis_set_curr, pres_curr)

    for i in range(0, len(pres_curr)):
        '''
        根据平凡性剪枝, 相同属性生成谓词只能存在一个
        '''
        if cut_by_triviality(X, pres_curr[i]):
            continue
        '''
        加入候选谓词集中的第i个谓词
        更新各个参数
        '''
        X_next = copy.deepcopy(X)
        X_next.append(pres_curr[i])
        '''
        更新证据集
        '''
        t_uncover_next = 0
        evis_set_next = []
        for evi in evis_set_curr:
            if pres_curr[i] not in evi.sat:
                evis_set_next.append(evi)
                t_uncover_next = t_uncover_next + evi.num
        '''
        更新可选谓词
        '''
        pres_next = copy.deepcopy(pres_curr[i + 1:])

        MC = FastDC_minimal_covers_search(evis_set_next, X_next, pres_next, MC, t_uncover_next, t_aim)

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


def Rank_P(evis_set_curr, pres_curr):
    """
    :param evis_set_curr: 剩余证据集
    :param pres_curr: 剩余谓词
    :return: 谓词按照覆盖度排序
    """
    cover = []
    for p in pres_curr:
        count = 0
        for evi in evis_set_curr:
            if p in evi.sat:
                count = count + evi.num
        cover.append((p, count))
    cover.sort(key=functools.cmp_to_key(compare), reverse=True)
    P_ranked = []
    for t in cover:
        P_ranked.append(t[0])
    return P_ranked


def compare(a, b):
    if a[-1] > b[-1]:
        return 1
    elif a[-1] == b[-1]:
        return 0
    else:
        return -1