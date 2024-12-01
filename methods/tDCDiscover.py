import copy
import functools


def get_evis_matrix(pres_space, I, threshold, readable_pres_space):
    """
    计算证据矩阵
    :param pres_space: 编号格式谓词空间
    :param I: 数据库实例
    :param threshold: 阈值集合
    :param readable_pres_space: 字符格式谓词空间
    :return: 满足谓词集格式为'谓词编号'的证据集
    """
    # 每一行为一个元组对的满足谓词集
    evis_set = set()
    evis_list = []
    evis_num_dict = {}
    for i in range(0, len(I)):
        for j in range(i + 1, len(I)):
            evi = ""
            for pres in pres_space:
                if pres[1] == "=":
                    evi_str = calculate(pres[3], I[i][pres[0]], I[j][pres[2]], threshold[pres[3]])
                    evi = evi + evi_str
                else:
                    continue
            if evi not in evis_set:
                evis_set.add(evi)
                evis_list.append(evi)
                evis_num_dict[evi] = 1
            else:
                evis_num_dict[evi] = evis_num_dict[evi] + 1
    # 每一行为：谓词字符 谓词满足情况 谓词覆盖度
    evis_matrix = []
    max_count = len(I)*(len(I)-1)/2
    evis_cover_dict = {'max': max_count}
    for i in range(0, len(pres_space)):
        pres_evi = [readable_pres_space[i]]
        count = 0
        for j in range(0, len(evis_list)):
            evi_count = evis_num_dict[evis_list[j]]
            if evis_list[j][i] == "1":
                count = count + evi_count
                pres_evi.append(evi_count)
            else:
                pres_evi.append(0)
        # 剔除覆盖度过高的不等号
        if pres_space[i][1] == '≠' and count >= max_count*0.95:
            continue
        pres_evi.append(count)
        evis_matrix.append(pres_evi)
        evis_cover_dict[readable_pres_space[i]] = count

    return evis_matrix, evis_cover_dict


def calculate(flag, first, second, threshold_now):
    """
    :param flag: 是否为数值属性比较
    :param first: 第一个值
    :param second: 第二个值
    :param threshold_now: 该谓词的阈值阈值
    :return: 谓词满足字符串
    """
    if flag == 0:
        '''
        字符属性处理
        B1 = ['=', '≠']
        '''
        flag = (first == second)
        if flag:
            return "10"
        else:
            return "01"
    else:
        '''
        数值属性处理
        B2 = ['=', '≠', '<', '>', '≤', '≥']
        '''
        flag1 = first - second - threshold_now[0]
        flag2 = first - second - threshold_now[1]
        if flag1 < 0:
            return "011010"
            # ≠ < ≤
        elif flag2 <= 0 <= flag1:
            return "100011"
            # = ≤ ≥
        elif flag2 > 0:
            return "010101"
            # ≠ > ≥


def evis_matrix_DFS_Covers(EM, pres_curr, MC, t_uncover, t_aim):
    """
    :param evis_matrix_curr: 当前证据矩阵
    :param pres_curr: 已选谓词
    :param MC: 已找到的覆盖
    :return: MC：已找到的覆盖
    :param t_uncover: 未覆盖元组数
    :param t_aim: 可容忍未覆盖元组数
    """
    '''
    查看当前谓词组是否覆盖完全
    '''
    if t_uncover <= t_aim:
        MC.append(pres_curr)
        return MC
    '''
    限制覆盖长度
    '''
    if len(pres_curr) >= 5:
        return MC
    '''
    是否还有可选谓词
    '''
    if len(EM) == 0:
        return MC
    '''
    基于覆盖度排序
    '''
    EM = del_zerocover_e(EM)
    EM.sort(key=functools.cmp_to_key(compare), reverse=True)

    for i in range(0, len(EM)):
        pre_new = EM[i][0]
        '''
        根据平凡性剪枝
        '''
        if cut_by_triviality(pres_curr, pre_new):
            continue
        '''
        查看覆盖可能性
        '''
        if EM[i][-1] * (5 - len(pres_curr)) < t_uncover - t_aim:
            break
        '''
        将当前谓词加入已选谓词
        '''
        pres_new = copy.deepcopy(pres_curr)
        pres_new.append(pre_new)
        '''
        计算加入谓词之后的矩阵
        '''
        next_EM, uncover_t_next = update_evis_matrix(EM[i+1:], EM[i], t_uncover)
        evis_matrix_DFS_Covers(next_EM, pres_new, MC, uncover_t_next, t_aim)
    return MC


def update_evis_matrix(EM, evi_new, uncover_t):
    """
    计算加入谓词evi_new后的证据矩阵
    :param evis_matrix_curr: 原证据矩阵
    :param evi_new: 挑选谓词的证据行
    :return: evis_matrix_new: 新证据矩阵
    :param uncover_t: 未覆盖元组数
    """
    next_EM = []
    for i in range(0, len(EM)):
        next_e = [EM[i][0]]
        next_count = EM[i][-1]
        for j in range(1, len(evi_new) - 1):
            if evi_new[j] > 0:
                if EM[i][j] > 0:
                    next_count = next_count - EM[i][j]
            else:
                next_e.append(EM[i][j])
        next_e.append(next_count)
        next_EM.append(next_e)

    uncover_t = uncover_t - evi_new[-1]
    return next_EM, uncover_t


def del_zerocover_e(EM):
    no_zero_EM = []
    for e in EM:
        if e[-1] != 0:
            no_zero_EM.append(e)
    return no_zero_EM


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


def compare(a, b):
    if a[-1] > b[-1]:
        return 1
    elif a[-1] == b[-1]:
        return 0
    else:
        return -1