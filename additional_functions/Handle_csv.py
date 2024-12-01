import csv


def read_csv(filename, line, row):
    """
    :param row: 限制列数
    :param line: 限制行数
    :param filename: 读取的文件名
    :return: header:英文属性名
            f_csv：按行存储的数据
    """
    row = row + 1
    with open(filename) as f:
        read = csv.reader(f)
        header = next(read)[:row]
        f_csv = []
        for i in range(line):
            f_csv.append(next(read)[:row])
        I = []
        string_set = set()
        string_set.add(0)
        for j in range(len(header)):
            if '(String)' in header[j]:
                string_set.add(j)
        for i in range(len(f_csv)):
            temp = []
            for j in range(len(header)):
                if j not in string_set:
                    # print(i)
                    temp.append(float(f_csv[i][j]))
                else:
                    temp.append(f_csv[i][j])
            I.append(temp)
    f.close()
    return header, I


def write_csv(filename, way, row):
    """
    :param filename:写入的文件名
    :param way: 写入方式。'w'为覆盖写入，'at'为追加写入
    :param row: 要写入的行
    :return: 无
    """
    with open(filename, way, newline='') as f:
        writer = csv.writer(f)
        writer.writerow(row)
    f.close()


def read_txt(filename):
    with open(filename) as f:
        DCs = f.readlines()
        new_DCs = []
        for DC in DCs:
            DC = DC[0:-1].split('^')
            new_DCs.append(DC)
        return new_DCs


def write_ans(filename, dabao,  MC, inter):
    with open(filename, "w", newline='') as f:
        f.write(filename[:-4] + "\n")
        f.write("Number of constraints: " + str(dabao[0]) + '\n')
        f.write("The average interestingness level of constraints: " + str(dabao[1]) + '\n')
        f.write("The number of constraints ranging from 0.9 to 1 points: " + str(dabao[2]) + '\n')
        f.write("The number of constraints ranging from 0.8 to 0.9 points: " + str(dabao[3]) + '\n')
        f.write("The number of constraints ranging from 0.7 to 0.8 points: " + str(dabao[4]) + '\n')
        f.write("The number of constraints ranging from 0.6 to 0.7 points: " + str(dabao[5]) + '\n')
        f.write("The number of constraints ranging from 0.5 to 0.6 points: " + str(dabao[6]) + '\n')
        f.write("The number of constraints ranging from 0.0 to 0.5 points: " + str(dabao[7]) + '\n')
        f.write('Time taken to get evidences: ' + str(dabao[8]) + 's\n')
        f.write('Time taken to search constraints: ' + str(dabao[9]) + 's\n')

        for i in range(1, len(dabao[10])):
            f.write('The' + str(i) + '-th threshold: ' + str(dabao[10][i]) + '\n')

    f.close()

    with open(filename, 'a', newline='') as f:
        for i in range(0, len(MC)):
            f.write('' + MC[i][0])
            for j in range(1, len(MC[i])):
                f.write(' ^ ' + MC[i][j])
            f.write('        ' + str(inter[i]))
            f.write('\n')

    f.close()