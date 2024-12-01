import copy
import functools
from additional_functions.Evidence import Evidences


def dc_finder(I, header, pres_space, readable_pres_space):
    """
    DC_Finder算法的构建证据集部分
    :param I: 数据实例
    :param header: 数据实例的关系模式
    :param pres_space: 编号格式谓词空间
    :param readable_pres_space:字符格式谓词空间
    :return: 返回完整证据集以及用于计算覆盖度的字典
    """
    """
    构造pils
    """
    pils = {}
    # 遍历每个属性
    for k in range(1, len(header)):
        # 为每个属性构建”值-元组“的一对多映射
        temp_dict = {}
        for i in range(0, len(I)):
            # 新值构建新映射
            if temp_dict.get(I[i][k]) is None:
                temp_dict[I[i][k]] = [i]
            # 旧值增加映射的元组
            else:
                temp_dict[I[i][k]].append(i)
        # 将每个属性的映射按照值由小到大排序
        sorted_temp_dict = dict(sorted(temp_dict.items(), key=lambda x: x[0]))
        # 加入总的pils中去，有几个属性就有几个字典
        pils[k] = sorted_temp_dict
    """
    构造谓词到btip的映射,btip为需要修正的证据的编号
    """
    btip_dict = {}
    # 遍历谓词空间
    for k in range(0, len(pres_space)):
        pres = pres_space[k]
        # 对于相等谓词
        if pres[1] == "=":
            temp_btip = []
            # 找到该谓词所涉及属性的pils
            l_list = list(pils[pres[0]].values())
            # 遍历该pils中的”值-元组“映射
            for l in l_list:
                # 如果某个映射只有一个元组，说明它没有重复值，无需考虑
                if len(l) == 1:
                    continue
                # 如果某个映射涉及多个元组，则说明其中的任意两个元组之间都满足相等谓词
                # 遍历该映射的元组集合
                for i in range(0, len(l)):
                    for j in range(i + 1, len(l)):
                        # 计算btip
                        btip = int((2*len(I) - l[i] - 1)*l[i]/2 + l[j] - l[i] - 1)
                        temp_btip.append(btip)
            # 将计算出的btip加入该相等谓词的btip字典
            if temp_btip:
                btip_dict[readable_pres_space[k]] = temp_btip
        # 对于大于谓词
        if pres[1] == ">":
            temp_btip = []
            # 找到该谓词所涉及属性的pils
            l_list = list(pils[pres[0]].values())
            # 如果该谓词的plis只有一个映射，说明该属性没有不同值，无需考虑
            if len(l_list) == 1:
                continue
            # 否则，遍历映射，找出不满足大于的部分
            for x in range(0, len(l_list)):
                for l1 in l_list[x]:
                    for y in range(x+1, len(l_list)):
                        for l2 in l_list[y]:
                            # 对任意两个映射x,y，如果x值小于y，但y中某个元组序号小于x某个元组，说明其满足大于谓词
                            if l1 > l2:
                                # 计算btip
                                btip = int((2 * len(I) - l2 - 1)*l2/2 + l1 - l2 - 1)
                                temp_btip.append(btip)
            # 将计算出的btip加入该大于谓词的btip字典
            if temp_btip:
                btip_dict[readable_pres_space[k]] = temp_btip
    """
    初始化证据集
    """
    evis_set_init = []
    pres_space_init = set()
    # 构建一个包含”≠ < ≤“的证据
    for k in range(0, len(pres_space)):
        if pres_space[k][1] == "≠" or pres_space[k][1] == "<" or pres_space[k][1] == "≤":
            pres_space_init.add(readable_pres_space[k])
    # 初始假设每个元组对均满足”≠ < ≤“
    for i in range(0, len(I)):
        for j in range(i+1, len(I)):
            evis_set_init.append(copy.deepcopy(pres_space_init))
    """
    构造修复元组对 '=', '≠', '<', '>', '≤', '≥'
    """
    for k in range(len(pres_space)):
        pres = pres_space[k]
        if pres[1] == "=":
            # 构造修复集合，字符谓词为{'=', '≠'}，非字符谓词为{'=', '≠', '<', '≥'}
            if '(String)' in header[pres[0]]:
                fix = {readable_pres_space[k], readable_pres_space[k + 1]}
            else:
                fix = {readable_pres_space[k], readable_pres_space[k + 1], readable_pres_space[k + 2],
                       readable_pres_space[k + 5]}
            # 查询该谓词是否有需要修复的证据
            if not btip_dict.get(readable_pres_space[k]):
                continue
            # 通过异或的方式修复证据集，将{'≠', '<', '≤'}改为{'=', '≤', '≥'}
            for i in btip_dict[readable_pres_space[k]]:
                evis_set_init[i] = evis_set_init[i] ^ fix
        if pres[1] == ">":
            # 构造修复集合，为{'<', '>', '≤', '≥'}
            fix = {readable_pres_space[k - 1], readable_pres_space[k], readable_pres_space[k + 1],
                   readable_pres_space[k + 2]}
            # 查询该谓词是否有需要修复的证据
            if not btip_dict.get(readable_pres_space[k]):
                continue
            # 通过异或的方式修复证据集，将{'≠', '<', '≤'}改为{'≠', '>', '≥'}
            for i in btip_dict[readable_pres_space[k]]:
                evis_set_init[i] = evis_set_init[i] ^ fix
    """
    去除重复证据
    """
    # 设置空证据集
    evis_set = []
    # 遍历初始证据集
    for evi in evis_set_init:
        flag = True
        # 对于已经加入进证据集的证据，不再加入，而是增加其出现次数
        for old_evi in evis_set:
            if old_evi.sat == evi:
                old_evi.addtime(1)
                flag = False
                break
        # 对于未加入证据集的证据，将其加入证据集，记录初始次数为1
        if flag:
            new_evi = Evidences(1, evi)
            evis_set.append(new_evi)
    """
    计算单个谓词覆盖度
    """
    evis_cover_dict = {'max': len(I) * (len(I) - 1) / 2}
    for readable_pres in readable_pres_space:
        count = 0
        # 依次查询每个谓词在证据集中出现了几次
        for evi in evis_set:
            if readable_pres in evi.sat:
                count = count + evi.num
        evis_cover_dict[readable_pres] = count

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


def DC_Finder_minimal_covers_search(evis_set_curr, X, pres_curr, MC, t_uncover, t_aim):
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

        MC = DC_Finder_minimal_covers_search(evis_set_next, X_next, pres_next, MC, t_uncover_next, t_aim)

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