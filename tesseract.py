import pytesseract
from PIL import Image
import os

#pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Gleb\Documents\01.Обучение\01.Python\Python_coursework\pytnon_coursework_plotnikov\Tesseract-OCR\tesseract.exe'
#pytesseract.pytesseract.tesseract_cmd = r'..\..\..\tesseract-ocr\tesseract.exe'
#pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Gleb\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
#pytesseract.pytesseract.tesseract_cmd = r'C:\Users\plotnikov.gleb\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
tesseract_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Tesseract-OCR', 'tesseract.exe'))
pytesseract.pytesseract.tesseract_cmd = tesseract_path


def ocr_recognize(image="test.jpg", lang='rus'):
    image = Image.open(image)
    string = pytesseract.image_to_string(image, lang)
    print(string)
    return(string)

