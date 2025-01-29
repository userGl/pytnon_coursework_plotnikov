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
        return "\nВсе тесты успешно пройдены!"
    else:
        return "\nНекоторые тесты не прошли."

if __name__ == "__main__":
    result = run_tests()
    print(result)
    sys.exit(0 if "успешно" in result else 1) 