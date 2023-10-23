import os
import shutil
import subprocess
import logging

class doxy_gen:
    # Конструктор класса, принимает пути к директориям и файлам
    def __init__(self, input_sources_dir, doxyfile_path, doxygen_output_dir, skip_dir):
        self.input_sources_dir = input_sources_dir  # Задаем путь к входной директории
        self.doxyfile_path = doxyfile_path  # Задаем путь к файлу конфигурации Doxygen
        self.doxygen_output_dir = doxygen_output_dir  # Задаем путь к директории для вывода Doxygen
        self.skip_dir = skip_dir  # Задаем список директорий для пропуска
        self.logger = self.setup_logger()  # Инициализация логгера


    # Настройка логгера
    def setup_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Получение пути к папке, где находится исполняемый файл
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Создание обработчика для записи логов в файл в текущей папке
        log_file_path = os.path.join(current_dir, 'doxy_gen.log')
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Создание обработчика для вывода логов в консоль
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger


    # Метод для создания или очистки директории
    def create_or_clear_directory(self, dir_path):
        if os.path.exists(dir_path):  # Проверяем, существует ли указанная директория
            shutil.rmtree(dir_path)  # Если существует, удаляем её
        os.makedirs(dir_path)  # Создаем новую директорию


    # Метод для перемещения файлов из текущей директории в main_files
    def move_files_to_main_dir(self):
        main_files_dir = os.path.join(self.input_sources_dir, "main_files")
        self.create_or_clear_directory(main_files_dir)

        # Пройдитесь по всем файлам в текущей директории
        for file in os.listdir(self.input_sources_dir):
            file_path = os.path.join(self.input_sources_dir, file)
            # Проверьте, что это файл (а не директория)
            if os.path.isfile(file_path):
                # Копируйте файл в папку "main_files"
                shutil.copy(file_path, os.path.join(main_files_dir, file))
        

    # Метод для получения списка путей ко всем поддиректориям в заданной директории
    def get_subdirectories_paths(self):
        subdirectories = []  # Создаем пустой список поддиректорий
        skip_strings = self.skip_dir  # Получаем список директорий для пропуска

        for root, dirs, files in os.walk(self.input_sources_dir):  # Обходим все директории и файлы в корневой директории
            for dir_name in dirs:  # Перебираем все поддиректории
                full_path = os.path.join(root, dir_name)[self.input_sources_dir.__len__():]  # Формируем полный путь к поддиректории
                if any(skip_str in full_path for skip_str in skip_strings):  # Проверяем, нужно ли пропускать эту директорию
                    continue
                subdir_path = os.path.join(root, dir_name)  # Формируем полный путь к поддиректории
                subdirectories.append(subdir_path)  # Добавляем путь к поддиректории в список

        return subdirectories  # Возвращаем список поддиректорий


    # Метод для обновления файла конфигурации doxygen
    def update_doxyfile(self, input_path, output_path):
        updated_lines = []  # Создаем пустой список для обновленных строк

        with open(self.doxyfile_path, 'r') as file:  # Открываем файл конфигурации Doxygen на чтение
            for line in file:  # Перебираем строки в файле
                if line.startswith("INPUT                  ="):  # Если строка начинается с указанной подстроки
                    updated_lines.append(f"INPUT                  = {input_path}\n")  # Заменяем эту строку новой
                elif line.startswith("OUTPUT_DIRECTORY       ="):  # Если строка начинается с указанной подстроки
                    updated_lines.append(f"OUTPUT_DIRECTORY       = {output_path}\n")  # Заменяем эту строку новой
                else:
                    updated_lines.append(line)  # Иначе оставляем строку без изменений

        with open(self.doxyfile_path, 'w') as file:  # Открываем файл конфигурации Doxygen на запись
            file.writelines(updated_lines)  # Записываем обновленные строки в файл


    def run_doxygen(self, paths):
        for path in paths:  # Перебираем список поддиректорий
            self.logger.info(f"Обработка директории: {path}")  # Записываем информацию о текущей директории в лог
            doxygen_output_dir = self.doxygen_output_dir + path[self.input_sources_dir.__len__():]  # Формируем путь к директории вывода Doxygen
            self.logger.info(f"Директория вывода: {doxygen_output_dir}")  # Записываем информацию о директории вывода в лог
            self.update_doxyfile(path, doxygen_output_dir)  # Обновляем файл конфигурации Doxygen
            process = subprocess.run(["doxygen", self.doxyfile_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # Запускаем Doxygen и получаем результат выполнения

            if process.returncode == 0: # Проверяем результат выполнения
                self.logger.info(f"Директория: {path} успешно обработана")
            else:
                self.logger.error(f"Ошибка при обработке директории: {path}")
                self.logger.error(f"Ошибка:\n{process.stderr.decode('utf-8')}")


    # Метод для запуска процесса doxygen
    def run(self):
        self.move_files_to_main_dir()
        paths = self.get_subdirectories_paths()  # Получаем список поддиректорий входной директории
        self.create_or_clear_directory(self.doxygen_output_dir)  # Создаем или очищаем директорию вывода Doxygen
        self.run_doxygen(paths)
