import cv2
import re
import easyocr
from ultralytics import YOLO

# ---------------- LOAD MODELS ----------------

# Official YOLOv8 model (auto-downloads safely)
model = YOLO("yolov8n.pt")

# OCR (CPU mode for stability in Flask)
reader = easyocr.Reader(['en'], gpu=False)

# ---------------- INDIAN STATE CODES ----------------

INDIAN_STATE_CODES = {
    "AN","AP","AR","AS","BR","CH","CG","DD","DL","DN","GA","GJ",
    "HP","HR","JH","JK","KA","KL","LA","LD","MH","ML","MN","MP",
    "MZ","NL","OD","PB","PY","RJ","SK","TN","TR","TS","UK","UP",
    "WB","BH"
}

# ---------------- OCR CONFUSION MAPS ----------------

LETTER_MAP = {
    '0': 'O', '1': 'I', '2': 'Z', '5': 'S', '8': 'B'
}

DIGIT_MAP = {
    'O': '0', 'I': '1', 'Z': '2', 'S': '5', 'B': '8'
}

# ---------------- VALIDATION ----------------

def valid_indian_plate(text):
    patterns = [
        r'^[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}$',   # MH20DV2366
        r'^[A-Z]{2}[0-9]{1}[A-Z]{1,2}[0-9]{4}$', # DL8CAF5030
        r'^BH[0-9]{2}[A-Z]{2}[0-9]{4}$'          # BH12AB1234
    ]
    return any(re.match(p, text) for p in patterns)

# ---------------- STATE CODE CORRECTION ----------------

def fix_state_code(text):
    if len(text) < 2:
        return text

    state = text[:2]
    if state in INDIAN_STATE_CODES:
        return text

    # Common OCR confusions in state code
    replacements = {
        'H': ['M'],
        'M': ['H'],
        'N': ['M'],
        'W': ['M']
    }

    for i in range(2):
        if state[i] in replacements:
            for r in replacements[state[i]]:
                new_state = list(state)
                new_state[i] = r
                new_state = ''.join(new_state)
                if new_state in INDIAN_STATE_CODES:
                    return new_state + text[2:]

    return text

# ---------------- SMART OCR CORRECTION ----------------

def smart_correct(text):
    text = text.upper()
    text = re.sub(r'[^A-Z0-9]', '', text)

    if len(text) < 6:
        return None

    # Patterns: (letter_positions, digit_positions)
    patterns = [
        ([0,1,4,5], [2,3,6,7,8,9]),  # MH20DV2366
        ([0,1], [2,3,4,5,6,7]),      # DL8CAF5030
        ([0,1], [2,3,6,7,8,9])       # BH12AB1234
    ]

    for letters, digits in patterns:
        temp = list(text)

        for i in letters:
            if i < len(temp) and temp[i] in LETTER_MAP:
                temp[i] = LETTER_MAP[temp[i]]

        for i in digits:
            if i < len(temp) and temp[i] in DIGIT_MAP:
                temp[i] = DIGIT_MAP[temp[i]]

        candidate = ''.join(temp)
        candidate = fix_state_code(candidate)

        if valid_indian_plate(candidate):
            return candidate

    return None

# ---------------- MAIN PROCESS ----------------

def process_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return None

    results = model(img, conf=0.35)

    for r in results:
        for box, cls in zip(r.boxes.xyxy, r.boxes.cls):
            class_id = int(cls)

            # Vehicle classes (COCO)
            if class_id in [2, 3, 5, 7]:  # car, motorcycle, bus, truck
                x1, y1, x2, y2 = map(int, box)
                vehicle = img[y1:y2, x1:x2]

                if vehicle.size == 0:
                    continue

                gray = cv2.cvtColor(vehicle, cv2.COLOR_BGR2GRAY)
                gray = cv2.resize(
                    gray, None, fx=2, fy=2,
                    interpolation=cv2.INTER_CUBIC
                )

                ocr_results = reader.readtext(gray, detail=0)

                for res in ocr_results:
                    corrected = smart_correct(res)
                    if corrected:
                        return corrected

    return None
