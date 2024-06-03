import cv2
import os
import numpy as np
from time import sleep
# from picamera import PiCamera

def find_correction():
    # Read image.
    thresh_pixel = 1
    resolution = (622, 350)
    # camera = PiCamera()
    # camera.resolution = resolution
    # camera.rotation = 270
    # # camera.start_preview()
    # camera.capture('./imgs/sun.jpg')
    img = cv2.imread('./Mark_IV/Sintering/imgs/sun_middle.jpg', cv2.IMREAD_COLOR)

    # Convert to hsv for color filtering
    # hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Convert to grayscale.
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, resolution, interpolation=cv2.INTER_LINEAR)
    gray = gray[:,130:492]
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    (_, maxVal, _, _) = cv2.minMaxLoc(gray)
    gray = cv2.GaussianBlur(gray, (61, 61), 0)
    (_, _, _, maxLoc) = cv2.minMaxLoc(gray)
 
    # brightness_file_name = "brightness_val.txt"
    # with open(brightness_file_name, "w") as f:
    #     f.write(str(maxVal))

    height, width = gray.shape
    mid_width = int(width / 2)
    mid_height = int(height / 2) 
    elev_offset = -31
    azim_offset = 70

    img = cv2.resize(img, resolution, interpolation=cv2.INTER_LINEAR)
    img = img[:,130:492]

    # # Mask for orange light (the sun)
    # lower_orange = np.array([5,50,50])
    # upper_orange = np.array([10,255,255])
    # color_mask = cv2.inRange(hsv, lower_orange, upper_orange)
    # cv2.imshow("mask", color_mask)
    # cv2.waitKey(0)

    # # Bitwise-AND mask and original image
    # res = cv2.bitwise_and(img, img, mask=color_mask)

    cv2.circle(img, maxLoc, 1, 0, 2)
    cv2.circle(img, (mid_width - thresh_pixel + azim_offset, resolution[1] // 2 - thresh_pixel + elev_offset), 1, 0, 2)
    cv2.circle(img, (mid_width + thresh_pixel + azim_offset, resolution[1] // 2 + thresh_pixel + elev_offset), 1, 0, 2)
    cv2.circle(img, (resolution[0] // 2 + thresh_pixel + azim_offset, mid_height + elev_offset - thresh_pixel), 1, 0, 2)
    cv2.circle(img, (resolution[0] // 2 - thresh_pixel + azim_offset, mid_height + elev_offset + thresh_pixel), 1, 0, 2)
    cv2.imshow("Image", img)
    cv2.waitKey(0)
    
    pic_info = ["stay", "stay", maxVal, abs(mid_width + azim_offset - maxLoc[0]), abs(mid_height + elev_offset - maxLoc[1])]
    if mid_width + thresh_pixel + azim_offset < maxLoc[0]:
        pic_info[0] = "right"
    elif mid_width - thresh_pixel + azim_offset > maxLoc[0]:
        pic_info[0] = "left"
    if mid_height + thresh_pixel + elev_offset < maxLoc[1]:
        pic_info[1] = "down"
    elif mid_height - thresh_pixel + elev_offset > maxLoc[1]:
        pic_info[1] = "up"
    print(pic_info)
    return pic_info

def main():
    find_correction()

if __name__ == "__main__":
    main()