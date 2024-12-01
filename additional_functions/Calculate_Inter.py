def calculate_inter(evis_cover_dict, MC):
    """
    计算兴趣值
    :param evis_cover_dict: 每个证据的覆盖度信息
    :param MC: 所有最小覆盖
    :return: 每个最小覆盖的兴趣值
    """
    inter = {}
    for i in range(0, len(MC)):
        length = len(MC[i])
        cover = 0
        dict = set()
        for pres in MC[i]:
            cover = cover + evis_cover_dict[pres]
            words = pres.split(' ')
            words[0].split('.')
            words[2].split('.')
            dict.add(words[0][0])
            dict.add(words[0][1])
            dict.add(words[1])
            dict.add(words[2][0])
            dict.add(words[2][1])

        succ = 4 / len(dict)
        coverage = cover / (length * evis_cover_dict['max'])

        rank_score = 0.3 * succ + 0.7 * coverage

        inter[i] = rank_score

    return inter


def get_ave_inter(inter):
    if not inter:
        return 0, 0

    inter_list = []
    for i in range(len(inter)):
        inter_list.append(inter[i])
    ave = sum(inter_list) / len(inter_list)

    return ave


def get_inter_distri(inter):
    f9 = f8 = f7 = f6 = f5 = flow = 0
    for i in range(len(inter)):
        if 0.9 <= inter[i]:
            f9 = f9 + 1
        elif 0.8 <= inter[i] < 0.9:
            f8 = f8 + 1
        elif 0.7 <= inter[i] < 0.8:
            f7 = f7 + 1
        elif 0.6 <= inter[i] < 0.7:
            f6 = f6 + 1
        elif 0.5 <= inter[i] < 0.6:
            f5 = f5 + 1
        else:
            flow = flow + 1
    return f9, f8, f7, f6, f5, flow