import cv2
import numpy as np
from time import sleep

"""
Detects the sun using a frame from the camera. returns if and at what scale azimuth and elevation should move.
"""

def find_correction(camera):
    # Set threshold determining how many pixels the detected point
    # can be off from the desired location before correcting.
    thresh_pixel = 1
    resolution = (622, 350) # Frame resolution

    # Take a picture, save it, and read it.
    # The file is saved so it is viewable after running.
    camera.capture('./imgs/sun.jpg')
    img = cv2.imread('./imgs/sun.jpg', cv2.IMREAD_COLOR)

    # Convert to hsv for color masking.
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hsv = cv2.GaussianBlur(hsv, (3, 3), 0)

     # Mask for orange light (the sun).
    lower_orange = np.array([5,50,50])
    upper_orange = np.array([10,255,255])
    color_mask = cv2.inRange(hsv, lower_orange, upper_orange)

    # Find contours in masked image.
    contours,_= cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours=sorted(contours,key=lambda x:cv2.contourArea(x),reverse=True)

    # Iterate through contours and filter for relevant objects
    for cnt in contours:
        area=cv2.contourArea(cnt)
        (x,y,w,h)=cv2.boundingRect(cnt)
        
        # Filter contours with area.
        if area>300:
            cv2.rectangle(color_mask,(x,y),(x+w,y+h),255,-1)

    # Bitwise-AND mask and original image.
    res = cv2.bitwise_and(img, img, mask=color_mask)

    # Convert original image to grayscale.
    gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)

    # Blur image and find brightest pixel.
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    (_, maxVal, _, _) = cv2.minMaxLoc(gray)

    # Blur more and find the location of the brightest pixel.
    gray = cv2.GaussianBlur(gray, (31, 31), 0)
    (_, _, _, maxLoc) = cv2.minMaxLoc(gray)
    
    # Save brightness val in file so other files can react to low or high brightness.
    brightness_file_name = "./txtfiles/brightness_val.txt"
    with open(brightness_file_name, "w") as f:
        f.write(str(maxVal))

    # Find middle of the image.
    height, width = gray.shape
    mid_width = int(width / 2)
    mid_height = int(height / 2) 

    # Initialize tested pixel offsets for sun position in frame.
    # This accounts for the fact that the camera is not perfectly alined with the lens.
    elev_offset = -31
    azim_offset = 70

    # Visualization
    cv2.circle(img, maxLoc, 1, 0, 2)
    cv2.circle(img, (mid_width - thresh_pixel + azim_offset, resolution[1] // 2 - thresh_pixel + elev_offset), 1, 0, 2)
    cv2.circle(img, (mid_width + thresh_pixel + azim_offset, resolution[1] // 2 + thresh_pixel + elev_offset), 1, 0, 2)
    cv2.circle(img, (resolution[0] // 2 + thresh_pixel + azim_offset, mid_height + elev_offset - thresh_pixel), 1, 0, 2)
    cv2.circle(img, (resolution[0] // 2 - thresh_pixel + azim_offset, mid_height + elev_offset + thresh_pixel), 1, 0, 2)
    
    # Determine desired correction direction and magnitude and return.
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