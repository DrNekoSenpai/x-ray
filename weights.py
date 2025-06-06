import argparse
import pytesseract
import pyautogui
import numpy as np
import cv2
from strikes import up_to_date

# Define screen regions (left, top, width, height)
LEFT, TOP, WIDTH, HEIGHT = 2338, 300, 363, 55  # storage capacity
# Argument parsing
def parse_args():
    parser = argparse.ArgumentParser(description='A tool to calculate war weights.')
    parser.add_argument('-f', '--force-valid', action='store_false',
                        help='Allow any weight, not just multiples of 200 <= 34000.')
    parser.add_argument('-s', '--sheet', action='store_true',
                        help='Multiply final weight by 5 for Google Sheet.')
    return parser.parse_args()

# Check repository up-to-date
def ensure_up_to_date():
    if not up_to_date():
        print("Error: the local repository is not up to date. Please pull the latest changes before running this script.")
        print("To pull the latest changes, simply run the command 'git pull' in this terminal.")
        exit(1)

# Validate weight string
def is_valid_weight(w, force_valid):
    if not force_valid:
        return True
    try:
        n = int(w)
        return n % 200 == 0 and n <= 34000
    except ValueError:
        return False

# Preprocess image for OCR: grayscale, threshold, invert
def preprocess(img_pil):
    # 1) Convert to gray and threshold
    gray = cv2.cvtColor(np.array(img_pil), cv2.COLOR_BGR2GRAY)
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # 2) Upscale by 3×
    h, w = bw.shape
    big = cv2.resize(bw, (w*3, h*3), interpolation=cv2.INTER_CUBIC)

    # 3) Morphological opening to smooth corners
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    clean = cv2.morphologyEx(big, cv2.MORPH_OPEN, kernel)

    return clean

# OCR digits only with Tesseract psm 7
def ocr_digits(img):
    config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789/'
    return pytesseract.image_to_string(img, config=config).strip()[:5]

# OCR arbitrary text (with optional whitelist)
def ocr_text(img, whitelist=None):
    cfg = r'--oem 3 --psm 7'
    if whitelist:
        cfg += f' -c tessedit_char_whitelist={whitelist}'
    return pytesseract.image_to_string(img, config=cfg).strip()

# Apply odd corrections based on last weight
def apply_odd_cases(weight, last_weight_str):
    try:
        last = int(last_weight_str) if last_weight_str else None
    except ValueError:
        last = None

    if weight.startswith('23') and last is not None:
        if abs(last - 29000) < 1500 or abs(last/5 - 29000) < 1500:
            weight = '29' + weight[2:]
    if weight == '13280':
        weight = '32800'
    return weight

# Main processing
def main():
    args = parse_args()
    ensure_up_to_date()

    # Take a screenshot of just the storage region
    crop = pyautogui.screenshot(region=(LEFT, TOP, WIDTH, HEIGHT))
    # Preprocess and OCR
    proc = preprocess(crop)
    weight = ocr_digits(proc)
    # Fallback to raw if invalid
    if not is_valid_weight(weight, args.force_valid):
        weight = ocr_digits(crop)
    if not is_valid_weight(weight, args.force_valid):
        print(f"Error: OCR result '{weight}' is not valid.")
        # Show both images for debugging
        cv2.imshow('Processed', proc)
        cv2.imshow('Original', np.array(crop))
        cv2.waitKey(0)
        exit(1)

    # Read last weight
    with open('./outputs/weights.txt', 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
        last_weight = lines[-1].strip() if lines else ''

    # Apply odd-case fixes
    weight = apply_odd_cases(weight, last_weight)

    # Convert for sheet if needed
    final = int(weight) * (5 if args.sheet else 1)

    print(f"{len(lines) + 1}: {final}")

    # Append only weight to file
    with open('./outputs/weights.txt', 'a', encoding='utf-8') as f:
        if lines:
            f.write('\n')
        f.write(str(final))

if __name__ == '__main__':
    main()
