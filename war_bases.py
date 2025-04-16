import os, pyautogui, cv2, numpy as np, pytesseract, argparse

if not os.path.exists("./screenshots/war"): os.makedirs("./screenshots/war")
if not os.path.exists("./screenshots/fwa"): os.makedirs("./screenshots/fwa")

parser = argparse.ArgumentParser()
parser.add_argument("--war", "-w", action="store_true")
parser.add_argument("--auto", "-a", action="store_true")
args = parser.parse_args()

war_base = args.war
path = "./screenshots/war/" if war_base else "./screenshots/fwa/"

right_arrow_button = (2020, 1300)
base_number = (1600, 1950, 1175, 1250) # left, right, up, down

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

def create_stitched_image():
    pyautogui.moveTo(3440/2, 1440/2)
    pyautogui.click()
    pyautogui.click()

    for _ in range(5): 
        pyautogui.scroll(-1000)
    pyautogui.mouseDown()
    pyautogui.moveRel(0, 1000, 0.125)
    pyautogui.moveRel(-1000, 0, 0.125)
    pyautogui.mouseUp()
    pyautogui.moveRel(0, -1000, 0.125)
    pyautogui.mouseDown()
    pyautogui.moveRel(0, 1000, 0.125)
    pyautogui.mouseUp()

    bottom_edge = 250

    image_a = pyautogui.screenshot()
    image_a = image_a.crop((0, 0, 3440, 1440-bottom_edge))

    pyautogui.moveTo(3440/2, 1440/3)
    pyautogui.mouseDown()
    pyautogui.moveTo(3440/2, 0, 0.125)
    pyautogui.mouseUp()

    image_b = pyautogui.screenshot()
    image_b = image_b.crop((0, 0, 3440, 1440-bottom_edge))

    pyautogui.moveTo(3440/2, 1440/3)
    pyautogui.mouseDown()
    pyautogui.moveTo(3440/2, 0, 0.125)
    pyautogui.mouseUp()

    image_c = pyautogui.screenshot()
    custom_config = r'--oem 3 --psm 6 tessedit_char_whitelist=0123456789/'
    base = pytesseract.image_to_string(image_c.crop((base_number[0], base_number[2], base_number[1], base_number[3])), config=custom_config).strip()
    image_c = image_c.crop((0, 0, 3440, 1440-bottom_edge))

    # Convert images to OpenCV format
    image_a = cv2.cvtColor(np.array(image_a), cv2.COLOR_RGB2BGR)
    image_b = cv2.cvtColor(np.array(image_b), cv2.COLOR_RGB2BGR)
    image_c = cv2.cvtColor(np.array(image_c), cv2.COLOR_RGB2BGR)

    # Stitch images
    # stitched_ab = stitch_images(image_a, image_b)
    # stitched_abc = stitch_images(stitched_ab, image_c)

    stitched_bc = stitch_images(image_b, image_c)
    stitched_abc = stitch_images(image_a, stitched_bc)

    return base, stitched_abc

base, image = create_stitched_image()
cv2.imwrite(path + f"{base.replace('/', '_')}.png", image)