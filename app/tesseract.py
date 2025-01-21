import pytesseract
import PIL
from PIL import Image
import os
from pydantic import BaseModel, constr, ValidationError, Field, validator
from typing import Optional
import re

class Txt(BaseModel): #Для валидации
    txt: str
    txt: constr(min_length=3)


#Задаём путь к бинарнику tesseract.exe
#tesseract_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Tesseract-OCR', 'tesseract.exe')) - если папка Tesseract-OCR в папке app
tesseract_path = os.path.abspath(os.path.join(os.path.abspath('.'), 'Tesseract-OCR', 'tesseract.exe'))
pytesseract.pytesseract.tesseract_cmd = tesseract_path

#Модель для валидации распознанного текста
class OCRResult(BaseModel):
    text: constr(min_length=3) = Field(..., description="Распознанный текст")
    status: bool = Field(default=True, description="Статус выполнения OCR")
    
    @validator('text')
    def text_must_contain_letters(cls, v):
        if not re.search('[a-zA-Zа-яА-Я]', v):
            raise ValueError("Текст должен содержать хотя бы одну букву")
        return v

class Tesseract:
    
    def ocr_recognize2(self, file_path, lang='rus'): 
        try:            
            image1 = Image.open(file_path)
            recognized_text = pytesseract.image_to_string(image1, lang)
            
            # Создаем и валидируем результат через Pydantic модель
            result = OCRResult(text=recognized_text)
            return {"status": True, "text": result.text}
            
        except PIL.UnidentifiedImageError as e:        
            print(f"Ошибка {e}")
            return {"status": False, "text": str(e)}
            
        except ValidationError as e:
            print(f"Ошибка валидации: {e}")
            return {"status": False, "text": "Текст слишком короткий или не содержит букв"}
            
        except Exception as e:
            print(f"Непредвиденная ошибка: {e}")
            return {"status": False, "text": str(e)}
    
    def print_hello(self): # Использовалась для тестирования
        return "Hello"

