import os, pyautogui, cv2, numpy as np
from matplotlib import pyplot as plt
from PIL import Image

if not os.path.exists("./screenshots/war"): os.makedirs("./screenshots/war")
if not os.path.exists("./screenshots/fwa"): os.makedirs("./screenshots/fwa")

war_base = False
path = "./screenshots/war/" if war_base else "./screenshots/fwa/"
num = len(os.listdir(path)) + 1

pyautogui.moveTo(3440/2, 1440/2)
pyautogui.click()
pyautogui.click()

pyautogui.mouseDown() 
pyautogui.moveRel(500, 500)
pyautogui.mouseUp()
image_a = pyautogui.screenshot()

# 3440 x 1440 monitor
left, right, top, bottom = 0, 3440, 0, 1440
# We want to crop the bottom a little bit above the bottom of the screen
bottom -= 300
image_a = image_a.crop((left, top, right, bottom))

pyautogui.mouseDown() 
pyautogui.moveRel(0, -2000)
pyautogui.mouseUp()
image_b = pyautogui.screenshot()

# Convert pyautogui screenshots to OpenCV format
image_a = cv2.cvtColor(np.array(image_a), cv2.COLOR_RGB2BGR)
image_b = cv2.cvtColor(np.array(image_b), cv2.COLOR_RGB2BGR)

def stitch_images(image1, image2):
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    
    sift = cv2.SIFT_create()
    keypoints1, descriptors1 = sift.detectAndCompute(gray1, None)
    keypoints2, descriptors2 = sift.detectAndCompute(gray2, None)
    
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(descriptors1, descriptors2, k=2)
    
    good_matches = [m for m, n in matches if m.distance < 0.75 * n.distance]
    
    points1 = np.zeros((len(good_matches), 2), dtype=np.float32)
    points2 = np.zeros((len(good_matches), 2), dtype=np.float32)
    
    for i, match in enumerate(good_matches):
        points1[i, :] = keypoints1[match.queryIdx].pt
        points2[i, :] = keypoints2[match.trainIdx].pt
    
    H, mask = cv2.findHomography(points2, points1, cv2.RANSAC)
    
    height1, width1 = image1.shape[:2]
    warped_image2 = cv2.warpPerspective(image2, H, (width1, height1 * 2))
    
    stitched_image = np.zeros((height1 * 2, width1, 3), dtype=np.uint8)
    stitched_image[0:height1, 0:width1] = image1
    stitched_image[height1:height1 * 2, 0:width1] = warped_image2[height1:height1 * 2, 0:width1]
    
    return stitched_image

stitched_image = stitch_images(image_a, image_b)

if stitched_image is not None:
    output_path = os.path.join(path, f'{num}.png')
    cv2.imwrite(output_path, stitched_image)
else:
    print("Stitching failed.")
