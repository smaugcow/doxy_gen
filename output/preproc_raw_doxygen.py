import re
import os
import shutil
import logging

class pretty_tex:
    # Конструктор класса pretty_tex
    def __init__(self, doxy_input_dir, doxy_output_dir, files_to_keep):
        self.doxy_input_dir = doxy_input_dir
        self.doxy_output_dir = doxy_output_dir
        self.files_to_keep = files_to_keep
        self.logger = self.setup_logger()


    # Настройка логгера
    def setup_logger(self): 
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Получение пути к папке, где находится исполняемый файл
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Создание обработчика для записи логов в файл в текущей папке
        log_file_path = os.path.join(current_dir, 'pretty_tex.log')
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
    

    # Очистка выходного каталога
    def clear_doxy_output_dir(self):
        if os.path.exists(self.doxy_output_dir):
            shutil.rmtree(self.doxy_output_dir)
        os.makedirs(self.doxy_output_dir)


    # Предобработка файла: поиск ключевого слова keyword и выделение текста после него
    def preprocess_file(self, file_path, keyword):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                raw_input = content
                keyword_position = content.find(keyword)
                if keyword_position != -1:
                    trimmed_content = content[keyword_position:]
                    return raw_input, trimmed_content
                else:
                    return raw_input, ""
        except FileNotFoundError:
            self.logger.error(f"File not found: {file_path}")
            return raw_input, None


    # Извлечение информации о структурах из текста
    def extract_structures(self, text):
        pattern = r'\\doxysubsection\*\{Классы\}\n\\begin\{DoxyCompactItemize\}(.*?)\\end\{DoxyCompactItemize\}'
        match = re.search(pattern, text, flags=re.DOTALL)

        extracted_text = "\subsection{Структуры}\n\n\\begin{itemize}\n\n"

        if match:
            extracted_text += match.group(1).strip()
        else:
            # print("Совпадение \subsection{Структуры} не найдено.")
            return ""

        extracted_text = self.remove_substrings_after_keyword(extracted_text)

        pattern = r'\\item\s+(struct\s+\w+)\s+\\begin\{DoxyCompactList\}\\small\\item\\em\s+(.*?)\\end\{DoxyCompactList\}'
        extracted_text = re.sub(pattern, r'\\item \\texttt{\1} - \2\n', extracted_text, flags=re.DOTALL)
    
        return extracted_text + "\n\n\\end{itemize}\n"


    # Обработка и извлечение информации о файле
    def process_and_extract_info_class(self, input_file_path, keyword):
        # Предварительная обработка файла и извлечение необработанного текста
        raw_input, raw_input_after_keyword = self.preprocess_file(input_file_path, keyword)

        # Если ключевое слово не найдено, выводим предупреждение и ищем секцию \doxysection{}
        if raw_input_after_keyword == "":
            self.logger.warning(f"Keyword {keyword} not found in the file {input_file_path}.")

            # Извлекаем текст из секции \doxysection{}
            extracted_text = re.search(r'\\doxysection\{([^}]*)\}', raw_input).group(1)
        
            # Определяем секции для перечислений и переменных
            doxy_subsection_enum = "\doxysubsection{Перечисления}"
            doxy_subsection_var = "\doxysubsection{Переменные}"
        
            # Поиск позиции ключевого слова "Перечисления"
            keyword_pos_enum = raw_input.find(doxy_subsection_enum)
            if keyword_pos_enum == -1:
                # Если "Перечисления" не найдены, ищем "Переменные"
                keyword_pos_var = raw_input.find(doxy_subsection_var)
                if keyword_pos_var == -1:
                    return "", ""
                else:
                    # Заменяем найденную секцию на \section с извлеченным текстом
                    raw_input_after_keyword = "\section{" + extracted_text + "}" + raw_input[keyword_pos_var:]
            else:
                # Заменяем найденную секцию на \section с извлеченным текстом
                raw_input_after_keyword = "\section{" + extracted_text + "}" + raw_input[keyword_pos_enum:]
    
        # Паттерн для поиска названия класса
        pattern_name_class = r"\\doxysection\{(.+?)\}"
        match_name_class = re.search(pattern_name_class, raw_input)
        class_name = ""
    
        # Если найдено название класса, сохраняем его
        if match_name_class:
            class_name = match_name_class.group(1)
        else:
            self.logger.warning(f"Class name not found.")
    
        # Извлекаем структуры из текста
        structures = self.extract_structures(raw_input)
    
        # Заменяем ключевое слово на \section с названием класса
        raw_input_after_keyword = raw_input_after_keyword.replace(keyword, f"\\section{{{class_name}}}\n")
    
        return raw_input_after_keyword, structures


    # Удаление определенных подстрок из текста
    def remove_substrings_after_keyword(self, text):
        text = text.replace('\+', '')
        # text = text.replace('-', '')

        pattern = re.compile(r"(См\. определение в файле.*?строка \d+|Переопределяет метод предка .*?\.|Замещается в .*?\.|Замещает.*?\.|Переопределяется в .*?\.|\.\.\.)")
        cleaned_text = re.sub(pattern, "", text)

        pattern = r'Объявления и описания членов.*?\\end{DoxyCompactItemize}'
        cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.DOTALL)

        # Удаление \mbox{\Hypertarget{...}\label{...}}
        cleaned_text = re.sub(r"\\mbox\{\\Hypertarget\{.*?\}\\label\{.*?\}\}", "", cleaned_text)

        # Удаление \index{A1140@{A1140}!...@{...}}
        cleaned_text = re.sub(r"\\index\{.*?\!.*?\}\}", "", cleaned_text)
    
        # Удаление \doxysubsubsection{...{...}}
        cleaned_text = re.sub(r"\\doxysubsubsection.*?\}\}", "", cleaned_text)

        pattern = r'\\begin\{DoxyEnumFields\}\{Элементы перечислений\}(.*?)\\end\{DoxyEnumFields\}'
        cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.DOTALL)

        # Удаление \begin{DoxyParamCaption} и \end{DoxyParamCaption}
        cleaned_text = re.sub(r'\\begin{DoxyParamCaption}', '', cleaned_text)
        cleaned_text = re.sub(r'\\end{DoxyParamCaption}', '', cleaned_text)

        # Удаление \begin{DoxyVerb} и \end{DoxyVerb}
        cleaned_text = re.sub(r'\\begin{DoxyVerb}', '', cleaned_text)
        cleaned_text = re.sub(r'\\end{DoxyVerb}', '', cleaned_text)

        cleaned_text = re.sub(r'{\\bfseries Инициализатор}\s+\\begin{DoxyCode}{0}(.*?)\\end{DoxyCode}', '', cleaned_text, flags=re.DOTALL)

        # Удаляем лишние символы {\ttfamily и \hspace{0.3cm}
        cleaned_text = re.sub(r'\\hspace\{0.3cm\}', '', cleaned_text)
        cleaned_text = re.sub(r'\{\\ttfamily(.*?)\}', r'\1', cleaned_text)

        # Замена \mbox{\hyperlink{classDevice}{Device}} на Device
        cleaned_text = re.sub(r"\\mbox\{\\hyperlink\{(.*?)\}\{(.*?)\}\}", r"\2", cleaned_text)

        # Замена \doxysubsection{Методы} на \subsection{Методы}
        cleaned_text = re.sub(r"\\doxysubsection\{(.*?)\}", r"\\subsection{\1}", cleaned_text)

        # Замена форматирования и преобразование в нужный формат
        cleaned_text = re.sub(r'{\\footnotesize\\ttfamily (.*?)}', r'\\texttt{\1}', cleaned_text, flags=re.DOTALL)
    
        # Заменяем \item[{...}] на содержимое внутри [...]
        cleaned_text = re.sub(r'\\item\[\{(.*?)\}\]\{(.*?)\}', r'\1 \2', cleaned_text)

        # pattern = r'\\begin\{DoxyParams\}\{Аргументы\}\s*\n.*?\\hline\s*\\end\{DoxyParams\}'
        # cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.DOTALL)

        # Заменяем формат параметров метода
        cleaned_text = re.sub(r'\\begin{DoxyParams}{Аргументы}\n', r'\\begin{center}\n\\begin{tabularx}{\\textwidth}{ |X|X| }\n\\hline\n\\textbf{Аргумент} & \\textbf{Описание} \\\\\n\\hline\n', cleaned_text)
        cleaned_text = re.sub(r'{\\em (\w+)} & (.+?)\\\\\n', r'\1 & \2 \\\\\n', cleaned_text)
        cleaned_text = re.sub(r'\\hline\n\\end{DoxyParams}', r'\\hline\n\\end{tabularx}\n\\end{center}', cleaned_text)

        # Заменяем формат возвращаемого значения
        pattern = r'\\begin\{DoxyReturn\}\{Возвращает\}\n(.*?)\n\\end\{DoxyReturn\}'
        cleaned_text = re.sub(pattern, r'\n\\textbf{Возвращаемое значение:} \1', cleaned_text, flags=re.DOTALL)

        cleaned_text = re.sub(r'\\mbox{(.*?)}', r'\1', cleaned_text)

        # # Удаляем лишние символы {} и пробелы вокруг них
        cleaned_text = re.sub(r'\(\{ \}\)', '()', cleaned_text)
        cleaned_text = re.sub(r' \)', ')', cleaned_text)
        cleaned_text = re.sub(r'\$>\$\)', '$>$()', cleaned_text)
        cleaned_text = re.sub(r'  ', ' ', cleaned_text)

        # cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)

        # Замена начала строки на \item
        cleaned_text = re.sub(r'\\texttt{(.*?)}', r'\\item \\texttt{\1}', cleaned_text, flags=re.DOTALL)

        # Замена пустых строки на " - "
        pattern = r'\\item (\\texttt{.*?})\s*\n+(.*?)'
        replacement = r'\\item \1 - \2'
        cleaned_text = re.sub(pattern, replacement, cleaned_text, flags=re.MULTILINE|re.DOTALL)

        # # Удаляем лишние символы пробела в конструкции <text>
        # cleaned_text = re.sub(r'\$<\$\s*(\w+)\s*\$>\$', r'$<$\1$>$', cleaned_text)

        # cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)

        return cleaned_text

    
    # Форматирование текста
    # Добавление строк перед и после определенных подстрок
    def format_pretty_text(self, text):
        # Добавление строк перед и после определенных подстрок
        enum_subsection = "\\subsection{Перечисления}"
        constructors_subsection = "\\subsection{Конструктор(ы)}"
        methods_subsection = "\\subsection{Методы}"
        data_subsection = "\\subsection{Данные класса}"
        variables_subsection = "\\subsection{Переменные}"
    
        # scructures_subsection = "\\subsection{Структуры}"

        pretty_text = text

        if (enum_subsection in pretty_text):
            # Добавляем строку после \subsection{Перечисления}
            pretty_text = pretty_text.replace(enum_subsection, "\n\n" + enum_subsection + "\n\n\n\\begin{itemize}")

            if (variables_subsection not in pretty_text):
                if (constructors_subsection not in pretty_text):
                    if (methods_subsection not in pretty_text):
                        if (data_subsection not in pretty_text):
                            pretty_text += "\\end{itemize}\n\n\n"
                        else:
                            # Добавляем строку перед \subsection{Данные класса}
                            pretty_text = pretty_text.replace(data_subsection, "\\end{itemize}\n\n\n" + data_subsection) 
                    else:
                        # Добавляем строку перед \subsection{Методы}
                        pretty_text = pretty_text.replace(methods_subsection, "\\end{itemize}\n\n\n" + methods_subsection)
                else:
                    # Добавляем строку перед \subsection{Конструктор(ы)}
                    pretty_text = pretty_text.replace(constructors_subsection, "\\end{itemize}\n\n\n" + constructors_subsection)
            else:
                # Добавляем строку перед \subsection{Переменные}
                pretty_text = pretty_text.replace(variables_subsection, "\\end{itemize}\n\n\n" + variables_subsection)

        if (variables_subsection in pretty_text):
            # Добавляем строку после \subsection{Переменные}
            pretty_text = pretty_text.replace(variables_subsection, "\n\n" + variables_subsection + "\n\n\n\\begin{itemize}")

            pretty_text += "\\end{itemize}\n\n\n"
    
        if (constructors_subsection in pretty_text):
            # Добавляем строку после \subsection{Конструктор(ы)}
            pretty_text = pretty_text.replace(constructors_subsection, "\n\n" + constructors_subsection + "\n\n\n\\begin{itemize}")
        
            if (methods_subsection not in pretty_text):
                if (data_subsection not in pretty_text):
                    pretty_text += "\\end{itemize}\n\n\n"
                else:
                    # Добавляем строку перед \subsection{Данные класса}
                    pretty_text = pretty_text.replace(data_subsection, "\\end{itemize}\n\n\n" + data_subsection) 
            else:
                # Добавляем строку перед \subsection{Методы}
                pretty_text = pretty_text.replace(methods_subsection, "\\end{itemize}\n\n\n" + methods_subsection)


        if (methods_subsection in pretty_text):
            # Добавляем строку после \subsection{Методы}
            pretty_text = pretty_text.replace(methods_subsection, "\n\n" + methods_subsection + "\n\n\n\\begin{itemize}")

            if (data_subsection not in pretty_text):
                pretty_text += "\\end{itemize}\n\n\n"
            else:
                # Добавляем строку перед \subsection{Данные класса}
                pretty_text = pretty_text.replace(data_subsection, "\\end{itemize}\n\n\n" + data_subsection)

        if (data_subsection in pretty_text):
            # Добавляем строку после \subsection{Данные класса}
            pretty_text = pretty_text.replace(data_subsection, "\n\n" + data_subsection + "\n\n\n\\begin{itemize}")

            pretty_text += "\\end{itemize}\n\n\n"

        return pretty_text


    # Конвертация файла в pretty-формат
    def pretty_convert_class(self, input_file_path, keyword, is_namespace):
        raw_input_after_keyword, structures = self.process_and_extract_info_class(input_file_path, keyword)
        result = self.remove_substrings_after_keyword(raw_input_after_keyword)
        if is_namespace:
            result = self.format_pretty_text(result)
        else:
            result = self.format_pretty_text(result) + structures
        result = re.sub(r'\n\s*\n', '\n\n', result)
        return result


    # Запись контента в файл
    def write_to_file(self, file_path, content):
        with open(file_path, 'w') as file:
            file.write(content)


    # Переименование файлов и удаление файлов, кроме определенных
    def rename_files_and_delete_files_except_specific(self):
        for root, dirs, files in os.walk(self.doxy_output_dir):
            for folder_name, files_to_keep in self.files_to_keep.items():
                if folder_name in dirs:
                    folder_path = os.path.join(root, folder_name)
                    folder_files = os.listdir(folder_path)
                    for file in folder_files:
                        if os.path.isfile(os.path.join(root, folder_name, file)):
                            file_path = os.path.join(folder_path, file)
                            if file not in files_to_keep:
                                os.remove(file_path)

            for file in files:
                if "_1_1" in file:
                    # Формируем старое и новое имя файла
                    old_file_path = os.path.join(root, file)
                    new_file_path = os.path.join(root, file.replace("_1_1", ""))
                
                    # Переименовываем файл
                    os.rename(old_file_path, new_file_path)


    def work_with_entries(self):
        for root, dirs, files in os.walk(self.doxy_input_dir):
            for file_name in files:
                if "class" in file_name or "namespace" in file_name and "namespaces" not in file_name:
                    keyword = '\doxysubsection{Подробное описание}'
                    file_path = os.path.join(root, file_name)
                    self.logger.info(f"Форматирование файла: {file_path}")
                    is_namespace = False
                    if "namespace" in file_name and "namespaces" not in file_name:
                        is_namespace = True
                    result = self.pretty_convert_class(file_path, keyword, is_namespace)
                    target_file_path = os.path.join(self.doxy_output_dir, os.path.relpath(file_path, self.doxy_input_dir))
                    os.makedirs(os.path.dirname(target_file_path.replace('/latex', '')), exist_ok=True)
                    self.write_to_file(target_file_path.replace('/latex', ''), result)


    # Основной метод, запускающий процесс форматирования файлов
    def run(self):
        self.clear_doxy_output_dir()
        self.work_with_entries()
        self.rename_files_and_delete_files_except_specific()
                    

    # # Метод для отладки
    # def run_with_debug(self):
    #     keyword = '\doxysubsection{Подробное описание}'
    #     # keyword = '\doxysubsection{Перечисления}'
    #     result = self.pretty_convert_class(self.doxy_input_dir, keyword, True)
    #     self.write_to_file(self.doxy_output_dir, result)
