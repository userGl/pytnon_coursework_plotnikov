import pytest
import sys
import os

def run_tests():
    """Запуск всех тестов проекта"""
    # Добавляем текущую директорию в PYTHONPATH
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(project_root)
    
    # Запускаем все тесты с параметрами
    args = [
        "tests",  # директория с тестами
        "-v",     # подробный вывод
        "--tb=short",  # сокращенный traceback
    ]
    
    # Запускаем тесты и получаем код возврата
    return_code = pytest.main(args)
    
    # Выводим итоговое сообщение
    if return_code == 0:
        print("\nВсе тесты успешно пройдены!")
    else:
        print("\nНекоторые тесты не прошли.")
    
    return return_code

if __name__ == "__main__":
    sys.exit(run_tests()) 