import pytesseract, pyautogui

image = pyautogui.screenshot()
def find_storage_capacity_bbox(image):
    boxes = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    for i in range(len(boxes['text'])):
        if 'Storage' in boxes['text'][i] and 'Capacity' in boxes['text'][i+1]:
            x, y, w, h = boxes['left'][i] - 10, boxes['top'][i], 275, boxes['height'][i]
            return (x, y, w, h)
    return None

def crop_below_bbox(image, bbox, offset=0):
    if bbox:
        x, y, w, h = bbox
        crop_area = (x, y + h + offset, x + w, y + h + 50 + offset)
        return image.crop(crop_area)
    return None

def numeric_ocr(image):
    custom_config = r'--oem 3 --psm 6 outputbase digits'
    return pytesseract.image_to_string(image, config=custom_config)[:5]

bbox = find_storage_capacity_bbox(image)
cropped_image = crop_below_bbox(image, bbox, offset=0)

preprocessed_image = cropped_image.copy()

# Convert white to red, and everything else to white
for x in range(preprocessed_image.width):
    for y in range(preprocessed_image.height):
        r, g, b = preprocessed_image.getpixel((x, y))
        threshold = 225
        if r > threshold and g > threshold and b > threshold:
            preprocessed_image.putpixel((x, y), (0, 0, 0))
        else:
            preprocessed_image.putpixel((x, y), (255, 255, 255))

weight = numeric_ocr(preprocessed_image)

if weight: 
    with open('weights.txt', 'r', encoding='utf-8') as file:
        num_lines = len(file.readlines())

    print(f"{num_lines + 1}: {weight}")

    with open('weights.txt', 'a', encoding='utf-8') as file:
        file.write(f'{weight}\n')