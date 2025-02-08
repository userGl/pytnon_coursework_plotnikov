import pytesseract
import PIL
from PIL import Image
import os
from pydantic import BaseModel, constr, ValidationError, Field, validator
from typing import Optional
import re


#Задаём путь к бинарнику tesseract.exe
#tesseract_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Tesseract-OCR', 'tesseract.exe')) - если папка Tesseract-OCR в папке app
tesseract_path = os.path.abspath(os.path.join(os.path.abspath('.'), 'Tesseract-OCR', 'tesseract.exe'))
pytesseract.pytesseract.tesseract_cmd = tesseract_path

#Модель для валидации распознанного текста
class OCRResult(BaseModel):
    text: str
    status: bool = True

class Tesseract:    
    def __init__(self):
        self.available_languages = self._get_available_languages()

    def _get_available_languages(self):
        """Получает список установленных языков tesseract"""
        try:
            langs = pytesseract.get_languages()
            # Создаем словарь языков, исключая служебный osd
            return {lang: lang for lang in langs if lang != 'osd'}
        except Exception as e:
            print(f"Ошибка при получении списка языков: {e}")
            return {}

    def get_languages(self):
        """Возвращает словарь доступных языков"""
        return self.available_languages

    def ocr_recognize2(self, image_path: str, lang: str = 'rus+eng') -> dict:
        """Распознает текст на изображении"""
        # Проверяем каждый язык из составного ключа
        selected_langs = lang.split('+')
        for single_lang in selected_langs:
            if single_lang not in self.available_languages:
                return {"status": False, "text": f"Язык {single_lang} не установлен"}
            
        try:
            img = PIL.Image.open(image_path)
            recognized_text = pytesseract.image_to_string(img, lang=lang)
            
            # Проверяем текст перед созданием модели
            if not recognized_text or len(recognized_text.strip()) < 3 or not re.search('[a-zA-Zа-яА-Я]', recognized_text):
                return {"status": False, "text": "Ошибка: Текст слишком короткий или не содержит букв"}
            
            # Создаем и валидируем результат через Pydantic модель
            try:
                result = OCRResult(text=recognized_text)
                return {"status": True, "text": result.text}
            except ValidationError as e:
                print(f"Ошибка валидации: {e}")
                return {"status": False, "text": "Ошибка: Текст слишком короткий или не содержит букв"}
            
        except PIL.UnidentifiedImageError as e:        
            print(f"Ошибка {e}")
            return {"status": False, "text": "Ошибка: Неправильный формат файла"}
            
        except Exception as e:
            print(f"Непредвиденная ошибка: {e}")
            return {"status": False, "text": str(e)}
    
    def print_hello(self): # Использовалась для тестирования
        return "Hello"

