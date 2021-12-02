import argparse
import cv2 as cv
import numpy as np
import os
from time import time


def simpleMax(input_video, output_image):
    # ref: https://twitter.com/djsnm/status/1464295427939790852?s=11
    capture = cv.VideoCapture(input_video)
    # Read the frame
    # re_val is true if frame successfully read
    # frame_max is the RGB? values for each frame pixel
    read_success, frame_max = capture.read()
    while(capture.isOpened()):
        read_success, frame_n = capture.read()
        if(read_success):
            # element wise maximum of array elements
            frame_max = np.maximum(frame_n, frame_max)
        else:
            break
    cv.imwrite(output_image, frame_max)


def averageMax(input_video, output_image, num_points=30):
    # ref: https://pastebin.com/XUw48A8f
    # Author: Scott Manley / @djsnm
    # code to generate a fake long exposure image using a video
    mImg = []
    idx = 0
    # num_points is the number of bright points to select and average,
    # reduces noise, but makes trails less intense

    # open video file and read each image, assume 8bits/pixel
    cap = cv.VideoCapture(input_video)
    while(cap.isOpened()):
        ret, frame = cap.read()
        if(ret):
            if(idx < num_points):
                mImg.append(frame)
            else:
                mImg[idx % num_points] = np.maximum(
                    frame, mImg[idx % num_points])
        else:
            break
        idx += 1
        # output progress
        if(idx % 100 == 0):
            print(idx)

    print(len(mImg))
    idx = 0
    # now create an average
    avgImg = None
    for img in mImg:
        # cv.imwrite(str(idx) + "_test.png",img)
        if(idx == 0):
            avgImg = img.astype("float32")
        else:
            avgImg = avgImg + img.astype("float32")
        idx += 1

    # average and scale this to 16 bit range
    avgImg = avgImg * 256 / num_points
    avgImg = avgImg.astype(np.uint16)

    cv.imwrite(output_image, avgImg)


# ===== MAIN =====
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('input_video', help='Input video file path and name')
    parser.add_argument('output_image', help='Output path and image name')
    parser.add_argument('--method', help='Simple POINT maximum or AVERAGE')
    parser.add_argument(
        '--avg', help='Number of pixels to average; default of 30')
    args = parser.parse_args()

    input_video = args.input_video
    if not os.path.isfile(input_video):
        print("ERROR {} not found!".format(input_video))
        exit()

    if args.method is not None:
        method = str(args.method)
    else:
        method = 'POINT'

    if args.avg is not None:
        avg = int(args.avg)
    else:
        avg = 30

    tic = time()

    if method == 'POINT':
        description = 'Stacking images using POINT'
        print(description)
        simpleMax(input_video, args.output_image)
    elif method == 'AVERAGE':
        description = 'Stacking images using AVERAGE method ' \
            + f'with {avg} averaging'
        print(description)
        stacked_image = averageMax(input_video, args.output_image, avg)
    else:
        print("ERROR: method {} not found!".format(method))
        exit()

    print(f"Stacked {time()-tic} seconds")
