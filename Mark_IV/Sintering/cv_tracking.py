import cv2

def find_correction():
    # Read image.
    thresh_pixel = 10
    img = cv2.imread('./imgs/sun_filter3.jpg', cv2.IMREAD_COLOR)
    
    # Convert to grayscale.
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (540,700), interpolation=cv2.INTER_LINEAR)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    (_, maxVal, _, _) = cv2.minMaxLoc(gray)
    gray = cv2.GaussianBlur(gray, (101, 101), 0)
    (_, _, _, maxLoc) = cv2.minMaxLoc(gray)

    height, width = gray.shape
    mid_width = int(width / 2)
    mid_height = int(height / 2)

    img = cv2.resize(img, (540,700), interpolation=cv2.INTER_LINEAR)
    cv2.circle(img, maxLoc, 1, 0, 2)
    cv2.circle(img, (mid_width - thresh_pixel, 350 - thresh_pixel), 1, 0, 2)
    cv2.circle(img, (mid_width + thresh_pixel, 350 + thresh_pixel), 1, 0, 2)
    cv2.circle(img, (270 + thresh_pixel, mid_height - thresh_pixel), 1, 0, 2)
    cv2.circle(img, (270 - thresh_pixel, mid_height + thresh_pixel), 1, 0, 2)
    cv2.imshow("Image", img)
    cv2.waitKey(0)

    actions = ["stay", "stay", maxVal]
    if mid_width + thresh_pixel < maxLoc[0]:
        actions[0] = "right"
    elif mid_width - thresh_pixel > maxLoc[0]:
        actions[0] = "left"
    if mid_height + thresh_pixel < maxLoc[1]:
        actions[1] = "down"
    elif mid_height - thresh_pixel > maxLoc[1]:
        actions[1] = "up"
    print(actions)
    return actions

def main():
    find_correction()

if __name__ == "__main__":
    main()