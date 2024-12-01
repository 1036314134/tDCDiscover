def get_pres_space(header):
    """
    构造编号格式的谓词空间
    :param header: 数据库属性信息
    :return: pres_space: 谓词格式为列表[属性1编号 运算符 属性2编号 阈值编号]的谓词空间
             j: 需要的阈值数量
    """
    B1 = ['=', '≠']
    B2 = ['=', '≠', '<', '>', '≤', '≥']
    S_Attrs = []
    N_Attrs = []
    pres_space = []
    j = 0
    for i in range(1, len(header)):
        if '(String)' in header[i]:
            S_Attrs.append(i)
        else:
            N_Attrs.append(i)
    for attr in S_Attrs:
        for equ in B1:
            pres_space.append([attr, equ, attr, 0])
    for attr in N_Attrs:
        j = j + 1
        for equ in B2:
            pres_space.append([attr, equ, attr, j])

    return pres_space, j


def get_readable_pres(header, pres_space):
    """
    构造字符格式的谓词空间
    :param header: 数据库属性信息
    :param pres_space: 编号格式谓词空间
    :return: readable_pres_space: 谓词格式为字符串[属性1字符 运算符 属性2字符 阈值编号]的谓词空间
    """
    attrs = []
    for attr in header:
        if '(String)' in attr:
            attrs.append(attr[0:-8])
        elif '(Double)' in attr:
            attrs.append(attr[0:-8])
        else:
            attrs.append(attr)

    readable_pres_space = []
    for pres in pres_space:
        first = attrs[pres[0]]
        equ = pres[1]
        second = attrs[pres[2]]
        threshold = str(pres[3])
        rever_equ = ""
        if equ == '=':
            rever_equ = '≠'
        elif equ == '≠':
            rever_equ = '='
        elif equ == '<':
            rever_equ = '≥'
        elif equ == '>':
            rever_equ = '≤'
        elif equ == '≤':
            rever_equ = '>'
        elif equ == '≥':
            rever_equ = '<'

        readable_pres_space.append('t1.' + first + ' ' + rever_equ + ' t2.' + second + ' ' + threshold)

    return readable_pres_space
