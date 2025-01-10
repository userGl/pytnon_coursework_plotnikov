import pytesseract
from PIL import Image
import os


tesseract_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Tesseract-OCR', 'tesseract.exe'))
pytesseract.pytesseract.tesseract_cmd = tesseract_path


def ocr_recognize(image="test.jpg", lang='rus'):
    image = Image.open(image)
    string = pytesseract.image_to_string(image, lang)
    print(string)
    return(string)

