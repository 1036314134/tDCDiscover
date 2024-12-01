import time
from additional_functions.Calculate_Inter import calculate_inter, get_ave_inter, get_inter_distri
from additional_functions.Get_Predicate import get_pres_space, get_readable_pres
from additional_functions.Get_Threshold import get_threshold
from additional_functions.Handle_csv import read_csv, write_ans
from methods.ADCEnum import ADCEnum
from methods.DC_Finder import dc_finder, DC_Finder_minimal_covers_search
from methods.FDCD import ects_function_thr, negative_covers_search
from methods.FastDC import fast_dc, FastDC_minimal_covers_search
from methods.tDCDiscover import get_evis_matrix, evis_matrix_DFS_Covers


def test_function(function, threshold_flag, I, header, filename, line, row):
    new_filename = filename[:-4] + "(" + str(line) + "row" + str(row) + "col)"
    if function == 1:
        new_filename = new_filename + '_FastDC'
    elif function == 2:
        new_filename = new_filename + '_DC_Finder'
    elif function == 3:
        new_filename = new_filename + '_FDCD'
    elif function == 4:
        new_filename = new_filename + '_tDCDiscover'
    elif function == 5:
        new_filename = new_filename + '_A-FastDC'
    elif function == 6:
        new_filename = new_filename + '_ADC-Finder'
    elif function == 7:
        new_filename = new_filename + '_tADCDiscover'
    elif function == 8:
        new_filename = new_filename + '_ADCEnum'

    print("running " + new_filename)
    print("Start building predicate space")
    pres_space, j = get_pres_space(header)
    print("size of P_all： " + str(len(pres_space)))

    readable_pres_space = get_readable_pres(header, pres_space)

    if threshold_flag:
        new_filename = new_filename + '_tDC'
        threshold = get_threshold(I, pres_space, 1)
    else:
        new_filename = new_filename + '_DC'
        threshold = [[0, 0]]
        for i in range(j):
            threshold.append([0, 0])

    start1 = time.time()
    t_num = len(I) * (len(I) - 1) / 2
    c = 0.05
    t_aim = t_num * c

    if function == 1:
        print("use FastDC")
        print("start getting evidences")
        evis_set, evis_cover_dict = fast_dc(pres_space, I, threshold, readable_pres_space)
        end1 = time.time()
        print('time taken to get evidences', end1 - start1, 's')

        start2 = time.time()
        print("start searching tDCs")
        MC = FastDC_minimal_covers_search(evis_set, [], readable_pres_space, [], t_num, 0)
        end2 = time.time()
        print('time taken to search tDCs', end2 - start2, 's')

    elif function == 2:
        print("use DC_Finder")
        print("start getting evidences")
        evis_set, evis_cover_dict = dc_finder(I, header, pres_space, readable_pres_space)
        end1 = time.time()
        print('time taken to get evidences', end1 - start1, 's')

        start2 = time.time()
        print("start searching tDCs")
        MC = DC_Finder_minimal_covers_search(evis_set, [], readable_pres_space, [], t_num, 0)
        end2 = time.time()
        print('time taken to search tDCs', end2 - start2, 's')

    elif function == 3:
        print("use FDCD")
        print("start getting evidences")
        evis_set, evis_cover_dict = ects_function_thr(header, I, pres_space, readable_pres_space, threshold)
        end1 = time.time()
        print('time taken to get evidences', end1 - start1, 's')

        start2 = time.time()
        print("start searching tDCs")
        MC = negative_covers_search([], readable_pres_space, evis_set, [], t_num, 0)
        end2 = time.time()
        print('time taken to search tDCs', end2 - start2, 's')

    elif function == 4:
        print("use tDCDiscover")
        print("start getting evidences")
        evis_matrix, evis_cover_dict = get_evis_matrix(pres_space, I, threshold, readable_pres_space)
        end1 = time.time()
        print('time taken to get evidences', end1 - start1, 's')

        start2 = time.time()
        print("start searching tDCs")
        MC = evis_matrix_DFS_Covers(evis_matrix, [], [], t_num, 0)
        end2 = time.time()
        print('time taken to search tDCs', end2 - start2, 's')

    elif function == 5:
        print("use AFastDC")
        print("start getting evidences")
        evis_set, evis_cover_dict = fast_dc(pres_space, I, threshold, readable_pres_space)
        end1 = time.time()
        print('time taken to get evidences', end1 - start1, 's')

        start2 = time.time()
        print("start searching tADCs")
        MC = FastDC_minimal_covers_search(evis_set, [], readable_pres_space, [], t_num, t_aim)
        end2 = time.time()
        print('time taken to search tADCs', end2 - start2, 's')

    elif function == 6:
        print("use ADC_Finder")
        print("start getting evidences")
        evis_set, evis_cover_dict = dc_finder(I, header, pres_space, readable_pres_space)
        end1 = time.time()
        print('time taken to get evidences', end1 - start1, 's')

        start2 = time.time()
        print("start searching T=tADCs")
        MC = DC_Finder_minimal_covers_search(evis_set, [], readable_pres_space, [], t_num, t_aim)
        end2 = time.time()
        print('time taken to search tADCs', end2 - start2, 's')

    elif function == 7:
        print("use tADCDiscover")
        print("start getting evidences")
        evis_matrix, evis_cover_dict = get_evis_matrix(pres_space, I, threshold, readable_pres_space)
        end1 = time.time()
        print('time taken to get evidences', end1 - start1, 's')

        start2 = time.time()
        print("start searching tADCs")
        MC = evis_matrix_DFS_Covers(evis_matrix, [], [], t_num, t_aim)
        end2 = time.time()
        print('time taken to search tADCs', end2 - start2, 's')

    elif function == 8:
        print("use ADCEnum")
        print("start getting evidences")
        evis_set, evis_cover_dict = ects_function_thr(header, I, pres_space, readable_pres_space, threshold)
        end1 = time.time()
        print('time taken to get evidences', end1 - start1, 's')

        start2 = time.time()
        print("start searching tADCs")
        MC = ADCEnum([], readable_pres_space, evis_set, [], t_num, t_aim)
        end2 = time.time()
        print('time taken to search tADCs', end2 - start2, 's')

    else:
        print("error: no method was used")

    print("Start calculating interestingness")
    inter = calculate_inter(evis_cover_dict, MC)

    ave = get_ave_inter(inter)
    f9, f8, f7, f6, f5, flow = get_inter_distri(inter)

    dabao = [len(inter), ave, f9, f8, f7, f6, f5, flow, end1 - start1, end2 - start2, threshold]

    write_ans(new_filename + '.txt', dabao, MC, inter)

    print("finish\n")


def use_test_fuction(filename, line, row):
    print("start reading data")
    header, I = read_csv(filename, line, row)
    test_function(1, True, I, header, filename, line, row)
    test_function(2, True, I, header, filename, line, row)
    test_function(3, True, I, header, filename, line, row)
    test_function(4, True, I, header, filename, line, row)
    test_function(5, True, I, header, filename, line, row)
    test_function(6, True, I, header, filename, line, row)
    test_function(7, True, I, header, filename, line, row)
    test_function(8, True, I, header, filename, line, row)


def test_different_line(filename, row):
    for i in range(200, 2200, 200):
        use_test_fuction(filename, i, row)


def test_different_row(filename, line):
    for i in range(6, 16, 1):
        use_test_fuction(filename, line, i)


def test_all_data(filename_all):
    # use_test_fuction(filename_all[1], 1048570, 40)
    use_test_fuction(filename_all[1], 1000, 10)
    # use_test_fuction(filename_all[2], 295719, 19)
    use_test_fuction(filename_all[2], 1000, 10)
    # use_test_fuction(filename_all[3], 1462, 4)
    use_test_fuction(filename_all[3], 1000, 4)
    # use_test_fuction(filename_all[4], 1511, 5)
    use_test_fuction(filename_all[4], 1000, 5)
    # use_test_fuction(filename_all[5], 405184, 8)
    use_test_fuction(filename_all[5], 1000, 8)
    # use_test_fuction(filename_all[6], 3182, 5)
    use_test_fuction(filename_all[6], 1000, 5)
    # use_test_fuction(filename_all[7], 20560, 6)
    use_test_fuction(filename_all[7], 1000, 6)
    # use_test_fuction(filename_all[8], 220320, 53)
    use_test_fuction(filename_all[8], 1000, 10)


if __name__ == '__main__':
    filename_all = [r'./dataset/None',
                    r'./dataset/1_IDF/IDF.csv',
                    r'./dataset/2_CO/CO.csv',
                    r'./dataset/3_Climate/Climate.csv',
                    r'./dataset/4_Stock/Stock.csv',
                    r'./dataset/5_Telemetry/Telemetry.csv',
                    r'./dataset/6_Weather/Weather.csv',
                    r'./dataset/7_Occupancy/Occupancy.csv',
                    r'./dataset/8_Pump/Pump.csv',
                    ]

    test_all_data(filename_all)