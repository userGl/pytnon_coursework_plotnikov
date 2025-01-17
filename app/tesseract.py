import pytesseract
import PIL
from PIL import Image
import os
from pydantic import BaseModel, constr, ValidationError

class Txt(BaseModel): #Для валидации
    txt: str
    txt: constr(min_length=3)


#Задаём путь к бинарнику tesseract.exe
#tesseract_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Tesseract-OCR', 'tesseract.exe')) - если папка Tesseract-OCR в папке app
tesseract_path = os.path.abspath(os.path.join(os.path.abspath('.'), 'Tesseract-OCR', 'tesseract.exe'))
pytesseract.pytesseract.tesseract_cmd = tesseract_path


class Tesseract:
    
    def ocr_recognize2(self, file_path, lang='rus'): 
        try:            
            # text = Txt()
            # self.text = text            
            image1 = Image.open(file_path)
            self.text = pytesseract.image_to_string(image1, lang)
            txt = Txt(txt=self.text)        
        except PIL.UnidentifiedImageError as e:        
            print(f"Ошибка {e}")
            err = str(e)            
            return {"status":False, "text":err}
        except ValidationError as e:
            print(f"Ошибка {e}")
            err = str(e)
            return {"status":False, "text":err}
        else:            
            return {"status":True, "text": self.text }
    
    def print_hello(self): # Использовалась для тестирования
        return "Hello"
    

