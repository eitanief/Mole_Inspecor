import numpy as np
import cv2

global diff1
global max_cnt1


def mostCommon(lst):
    flatList = lst.flatten()
    return np.bincount(flatList).argmax()


def is_symetric(image_path):
    global diff1, max_cnt1
    image = cv2.imread("static/captures/"+ image_path)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    darkest = int(min(blur.flatten()))
    brightest = int(max(blur.flatten()))
    middle = round((darkest + brightest) / 2)
    ret, thresh = cv2.threshold(blur, middle, 255, cv2.THRESH_BINARY_INV)

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    max_cnt1 = max(contours, key=cv2.contourArea)
    cv2.drawContours(image, max_cnt1, -1, (0, 255, 0), 3)
    ellipse = cv2.fitEllipse(max_cnt1)
    cv2.ellipse(image, ellipse, (0, 255, 0), 2)

    ellipse_pnts = cv2.ellipse2Poly((int(ellipse[0][0]), int(ellipse[0][1])), (int(ellipse[1][0]), int(ellipse[1][1])),
                                    int(ellipse[2]), 0, 360, 1)
    diff1 = cv2.matchShapes(max_cnt1, ellipse_pnts, 1, 0.0)
    if diff1 > 0.025:
        return False
    else:
        return True


def is_border_clear(image_path):
    global diff1
    image = cv2.imread("static/captures/"+image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    darkest = int(min(blur.flatten()))
    brightest = mostCommon(blur)
    middle = round((darkest + brightest) / 2)
    ret, thresh = cv2.threshold(blur, middle, 255, cv2.THRESH_BINARY_INV)

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    max_cnt = max(contours, key=cv2.contourArea)
    cv2.drawContours(image, max_cnt, -1, (0, 255, 0), 3)

    ellipse = cv2.fitEllipse(max_cnt)

    ellipse_pnts = cv2.ellipse2Poly((int(ellipse[0][0]), int(ellipse[0][1])), (int(ellipse[1][0]), int(ellipse[1][1])),
                                    int(ellipse[2]), 0, 360, 1)
    diff2 = cv2.matchShapes(max_cnt, ellipse_pnts, 1, 0.0)

    if np.abs(diff1 - diff2) > 0.03:
        return False
    return True

def is_colored(image_path):
    global max_cnt1
    image = cv2.imread("static/captures/" + image_path)
    blur = cv2.GaussianBlur(image, (13, 13), 0)

    #### remove the background of the mole ####
    mask = np.zeros_like(image)
    cv2.drawContours(mask, [max_cnt1], 0, (255, 255, 255), -1)
    # First create the image with alpha channel
    bgraimage = cv2.cvtColor(blur, cv2.COLOR_BGR2BGRA)
    # Then assign the mask to the last channel of the image
    bgraimage[:, :, 3] = mask[:, :, 0]

    B, G, R, A = cv2.split(bgraimage)
    alpha = A / 255
    R = (255 * (1 - alpha) + R * alpha).astype(np.uint8)
    G = (255 * (1 - alpha) + G * alpha).astype(np.uint8)
    B = (255 * (1 - alpha) + B * alpha).astype(np.uint8)

    bgrimage = cv2.merge((B, G, R))

    #### create color histogram of the mole ####
    im = cv2.cvtColor(bgrimage, cv2.COLOR_BGR2RGB)
    # Make into Numpy array
    na = np.array(im)

    # Arrange all pixels into a tall column of 3 RGB values and find unique rows (colours)
    colors, counts = np.unique(na.reshape(-1, 3), axis=0, return_counts=1)
    # remove the white background
    colors = colors[:-1]
    counts = counts[:-1]
    zipped_colors_counts = zip(colors, counts)
    avg_count = np.average(counts)

    main_colors_counts = [((round(r / 255, 1), round(g / 255, 1), round(b / 255, 1)), count) for ((r, g, b), count) in
                          zipped_colors_counts if count > avg_count * 2]
    main_colors_no_dups = []
    counted_colors = {}
    for (color, count) in main_colors_counts:
        if counted_colors.get(color):
            continue
        all_count = 0
        same_color = [(col, cot) for (col, cot) in main_colors_counts if col == color]
        all_count = sum(cot for (col, cot) in same_color)
        counted_colors[color] = all_count
        main_colors_no_dups.append((color, all_count))

    counts_no_dups = [cot for (col, cot) in main_colors_no_dups]
    avg_count = np.average(counts_no_dups)
    final_colors_counts = [(color, count) for (color, count) in main_colors_no_dups if count > avg_count]
    # final_colors_counts = main_colors_no_dups

    main_colors = [color for (color, count) in final_colors_counts]
    main_counts = [count for (color, count) in final_colors_counts]
    if len(main_counts) > 6:
        return False
    else:
        return True