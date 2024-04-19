import pytesseract, pyautogui, subprocess, argparse
from contextlib import redirect_stdout as redirect
from io import StringIO

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

image = pyautogui.screenshot()
def find_storage_capacity_bbox(image):
    boxes = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    results = []

    for i in range(len(boxes['text'])):
        if 'Storage' in boxes['text'][i] and 'Capacity' in boxes['text'][i+1]:
            x, y, w, h = boxes['left'][i] - 10, boxes['top'][i], 275, boxes['height'][i]
            results.append((x, y, w, h))
    
    return results

def crop_below_bbox(image, bbox, offset=0):
    if bbox:
        x, y, w, h = bbox
        crop_area = (x, y + h + offset, x + w, y + h + 50 + offset)
        return image.crop(crop_area)
    return None

def numeric_ocr(image):
    custom_config = r'--oem 3 --psm 6 outputbase digits'
    return pytesseract.image_to_string(image, config=custom_config)[:5]

def preprocess_image(image, threshold=225):
    for x in range(image.width):
        for y in range(image.height):
            r, g, b = image.getpixel((x, y))
            if r > threshold and g > threshold and b > threshold:
                image.putpixel((x, y), (0, 0, 0))
            else:
                image.putpixel((x, y), (255, 255, 255))
    return image

bbox = find_storage_capacity_bbox(image)
if not bbox:
    print("Error: couldn't find the storage capacity.")
    exit(1)

# If the length of bbox is 3, then we only want the first two. 
# The third is dark elixir, we can't use that. 

gold_weight = None
elixir_weight = None

for i in range(len(bbox)):
    if i == 2: break

    cropped_image = crop_below_bbox(image, bbox[i], offset=0)
    preprocessed_image = cropped_image.copy()
    preprocessed_image = preprocess_image(preprocessed_image)
    weight = numeric_ocr(preprocessed_image)

    preprocessed_image.show()

    if args.force_valid:
        thresholds = [225, 200, 175, 150, 125, 100, 75, 50, 25, 0]
        while not is_valid_weight(weight): 
            print(f"Invalid weight: {weight}")
            threshold = thresholds.pop(0)
            weight = numeric_ocr(preprocess_image(cropped_image, threshold=threshold))

    if i == 0: gold_weight = weight
    if i == 1: elixir_weight = weight

if gold_weight and elixir_weight:
    if gold_weight == elixir_weight: 
        weight = gold_weight

    else: 
        # Ask user which weight is valid, if any
        print("Which weight is valid?")
        print(f"1. Gold: {gold_weight}")
        print(f"2. Elixir: {elixir_weight}")
        print("3. Neither")
        choice = input("Enter the number: ")

        if choice == '1': weight = gold_weight
        elif choice == '2': weight = elixir_weight
        else: 
            print("Please enter what it was supposed to be.")
            weight = input("Enter the weight: ")

if weight: 
    with open('weights.txt', 'r', encoding='utf-8') as file:
       num_lines = len(file.readlines())

    print(f"{num_lines + 1}: {weight}")

    with open('weights.txt', 'a', encoding='utf-8') as file:
        file.write(f'{weight}\n')