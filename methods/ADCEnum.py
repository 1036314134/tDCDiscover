import copy
import functools


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


def ADCEnum(path, preds, E, MC, t_uncover, t_aim):
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
            MC = ADCEnum(next_path, next_preds, next_E, MC, next_t_uncover, t_aim)

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