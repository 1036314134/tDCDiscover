def get_threshold(I, pres_space, step):
    thresholds = {0: [0, 0]}

    for pres in pres_space:
        first = pres[0]
        # equ = pres[1]
        second = pres[2]
        threshold = pres[3]

        if threshold in thresholds:
            continue

        up = []
        down = []
        zero = []

        for i in range(0, len(I) - step):
            delta = I[i][first] - I[i + step][second]
            if delta > 0:
                up.append(delta)
            elif delta < 0:
                down.append(delta)
            else:
                zero.append(delta)

        up_ave = sum(up) / (len(up) + len(zero))
        down_ave = sum(down) / (len(down) + len(zero))

        thresholds[threshold] = [down_ave, up_ave]

    return thresholds
