import pytesseract, pyautogui, subprocess, argparse, numpy as np, cv2
from contextlib import redirect_stdout as redirect
from io import StringIO
from PIL import Image

# Argument parser
parser = argparse.ArgumentParser(description='A tool to calculate war weights.')
parser.add_argument('-f', '--force-valid', action='store_false', help='Force the script to disregard values that are not divisible by 200.')
args = parser.parse_args()

def up_to_date(): 
    # Return FALSE if there is a new version available.
    # Return TRUE if the version is up to date.
    try:
        # Fetch the latest changes from the remote repository without merging or pulling
        # Redirect output, because we don't want to see it.
        with redirect(StringIO()):
            subprocess.check_output("git fetch", shell=True)

        # Compare the local HEAD with the remote HEAD
        local_head = subprocess.check_output("git rev-parse HEAD", shell=True).decode().strip()
        remote_head = subprocess.check_output("git rev-parse @{u}", shell=True).decode().strip()

        return local_head == remote_head

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None

if up_to_date() is False:
    print("Error: the local repository is not up to date. Please pull the latest changes before running this script.")
    print("To pull the latest changes, simply run the command 'git pull' in this terminal.")
    exit(1)

def is_valid_weight(weight):
    if not args.force_valid: return True
    try:
        numeric_weight = int(weight)
        return numeric_weight % 200 == 0
    except ValueError:
        return False

def find_storage_capacity_bbox(image):
    boxes = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    results = []

    for i in range(len(boxes['text'])):
        if 'Storage' in boxes['text'][i] and 'Capacity' in boxes['text'][i+1]:
            return True 
        
    return False

def numeric_ocr(image):
    custom_config = r'--oem 3 --psm 6 outputbase digits'
    return pytesseract.image_to_string(image, config=custom_config)[:5]

def color_to_alpha(image, color=(255, 255, 255), transparency_threshold=0.154, opacity_threshold=0.082):
    # Open the image
    img = image.convert("RGBA")
    datas = img.getdata()

    new_data = []
    for item in datas:
        # Calculate the difference between the current pixel and the target color
        diff = (
            abs(item[0] - color[0]) / 255.0,
            abs(item[1] - color[1]) / 255.0,
            abs(item[2] - color[2]) / 255.0,
        )
        # Calculate the overall difference
        overall_diff = sum(diff) / 3.0

        if overall_diff < transparency_threshold:
            # Turn matching pixels red with the specified opacity
            black_pixel = (0, 0, 0, int(255 * (1 - opacity_threshold)))
            new_data.append(black_pixel)
        else:
            white_pixel = (255, 255, 255, 255)
            new_data.append(white_pixel)

    # Update image data
    img.putdata(new_data)

    # Apply adaptive thresholding
    processed_image = cv2.adaptiveThreshold(
        cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY),
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2,
    )
    
    # Invert the image if necessary (depends on the image background)
    processed_image = cv2.bitwise_not(processed_image)

    return img

image = pyautogui.screenshot()

# Verify that the image contains the storage capacity text
if not find_storage_capacity_bbox(image):
    print("Error: the image does not contain the storage capacity text.")
    exit(1)

# Example usage
left, right, top, bottom = 2338, 2701, 300, 355
# show_crop_area(image, left, right, top, bottom)

cropped_image = image.crop((left, top, right, bottom))
weight = numeric_ocr(cropped_image)

if not is_valid_weight(weight):
    print(f"Error: OCR result '{weight}' is not valid. Preprocessing.")
    preprocessed_image = color_to_alpha(cropped_image)
    weight = numeric_ocr(preprocessed_image)

if not is_valid_weight(weight):
    print(f"Error: OCR result '{weight}' is not valid after preprocessing.")
    exit(1)

# Odd case: a weight beginning with "23" should instead be "29", but only if the last recorded value was +/- 1000 from 29000. Otherwise, leave as is.
if weight.startswith('23'): 
    with open('weights.txt', 'r', encoding='utf-8') as file:
        last_weight = file.readlines()[-1].strip()
        if last_weight and abs(int(last_weight) - 29000) < 1000: weight = '29' + weight[2:]

if weight: 
    with open('weights.txt', 'r', encoding='utf-8') as file:
        num_lines = len(file.readlines())

    print(f"{num_lines + 1}: {weight}")

    with open('weights.txt', 'a', encoding='utf-8') as file:
        file.write(f'{weight}')
        if num_lines+1 != 50: 
            file.write('\n')