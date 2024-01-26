import cv2
import os
from time import sleep
from picamera import PiCamera

def find_correction(camera):
    # Read image.
    thresh_pixel = 9
    resolution = (622, 350)
    # camera = PiCamera()
    camera.resolution = resolution
    camera.rotation = 270
    # camera.start_preview()
    camera.capture('./imgs/sun.jpg')
    img = cv2.imread('./imgs/sun.jpg', cv2.IMREAD_COLOR)


    # Convert to grayscale.
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, resolution, interpolation=cv2.INTER_LINEAR)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    (_, maxVal, _, _) = cv2.minMaxLoc(gray)
    gray = cv2.GaussianBlur(gray, (101, 101), 0)
    (_, _, _, maxLoc) = cv2.minMaxLoc(gray)

    height, width = gray.shape
    mid_width = int(width / 2)
    mid_height = int(height / 2) 

    # img = cv2.resize(img, resolution, interpolation=cv2.INTER_LINEAR)
    # cv2.circle(img, maxLoc, 1, 0, 2)
    # cv2.circle(img, (mid_width - thresh_pixel, resolution[1] // 2 - thresh_pixel), 1, 0, 2)
    # cv2.circle(img, (mid_width + thresh_pixel, resolution[1] // 2 + thresh_pixel), 1, 0, 2)
    # cv2.circle(img, (resolution[0] // 2 + thresh_pixel, mid_height - thresh_pixel), 1, 0, 2)
    # cv2.circle(img, (resolution[0] // 2 - thresh_pixel, mid_height + thresh_pixel), 1, 0, 2)
    # cv2.imshow("Image", img)
    # cv2.waitKey(0)
    
    pic_info = ["stay", "stay", maxVal, abs(mid_width - maxLoc[0]), abs(mid_height - maxLoc[1])]
    if mid_width + thresh_pixel < maxLoc[0]:
        pic_info[0] = "right"
    elif mid_width - thresh_pixel > maxLoc[0]:
        pic_info[0] = "left"
    if mid_height + thresh_pixel < maxLoc[1]:
        pic_info[1] = "down"
    elif mid_height - thresh_pixel > maxLoc[1]:
        pic_info[1] = "up"
    print(pic_info)
    return pic_info

def main():
    camera = PiCamera()
    camera.start_preview()
    sleep(3.0)
    find_correction(camera)
    camera.stop_preview()

if __name__ == "__main__":
    main()