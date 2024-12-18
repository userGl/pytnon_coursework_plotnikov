import pytesseract
from PIL import Image

#C:\Users\Gleb\AppData\Local\Programs\Tesseract-OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\plotnikov.gleb\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

image = Image.open("test1.png")
string = pytesseract.image_to_string(image, lang='rus')
print(string)