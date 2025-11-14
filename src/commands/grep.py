import os
import re
from Lab_2_Consoleapp_Python.src.commands.parsing.command_parsers import parse_grep_args

def execute(self, args: list[str]) -> None:
    """
    :param args: Аргументы: флаг -r - поиск в подкаталогах; флаг -i - поиск без учета регистра; pattern -
    что нужно искать; path - где искать.
    :return: Данная функция ничего не возвращает
    """
    parsed_args = parse_grep_args(args)
    if parsed_args is None:
        return None

    search_path = self.resolve_user_path(parsed_args.path)

    # Ошибка, если путь не существует
    if not os.path.exists(search_path):
        self.handle_error(f"grep: cannot access '{parsed_args.path}': No such file or directory")
        return None

    try:
        # Поиск по файлам/директориям
        # Игнорирование регистра, если есть флаг -i
        flags = re.IGNORECASE if parsed_args.i else 0
        pattern = re.compile(parsed_args.pattern, flags)

        results = []

        # Поиск в директории. Рекурсивно во всех директориях внутри, если есть флаг -r
        if os.path.isfile(search_path):
            results = _search_in_file(search_path, pattern, parsed_args.path)
        elif os.path.isdir(search_path):
            if parsed_args.r:
                results = _search_in_directory_recursive(search_path, pattern, parsed_args.path)
            else:
                results = _search_in_directory(search_path, pattern, parsed_args.path)

        # Выводим результат, если что-то нашли, или же сообщение,
        # что ничего не найдено/ошибку
        if results:
            for result in results:
                print(result)
            self.logger.debug(
                f"Found {len(results)} matches for pattern '{parsed_args.pattern}' in '{parsed_args.path}'")
        else:
            print(f"No matches found for pattern '{parsed_args.pattern}' in '{parsed_args.path}'")
            self.logger.debug(f"No matches found for pattern '{parsed_args.pattern}' in '{parsed_args.path}'")

    except re.error as e:
        self.handle_error(f"grep: invalid pattern '{parsed_args.pattern}': {e}")
    except Exception as e:
        self.handle_error(f"grep: unexpected error: {e}")


def _search_in_file(file_path: str, pattern: re.Pattern, display_path: str) -> list:
    """
    Вспомогательная функция для поиска в файле.
    Аргументы: file_path - абсолютный путь до файла; pattern - что искать,
    display_path - путь для вывода пользователю.
    Возвращаемое значение: results - найденные результаты.
    """
    results = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            for line_num, line in enumerate(file, 1):
                if pattern.search(line):
                    clean_line = line.rstrip('\n\r')
                    highlighted_line = _highlight_match(clean_line, pattern)
                    results.append(f"{display_path}:{line_num}:{highlighted_line}")
    except (PermissionError, UnicodeDecodeError, OSError):
        pass
    return results


def _search_in_directory(dir_path: str, pattern: re.Pattern, display_path: str) -> list:
    """
    Вспомогательная функция для поиска в директории.
    Аргументы: dir_path - абсолютный путь до директории, pattern - что искать;
    display_path - путь для вывода пользователю.
    """
    results = []
    try:
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            if os.path.isfile(item_path):
                file_results = _search_in_file(item_path, pattern, os.path.join(display_path, item))
                results.extend(file_results)
    except (PermissionError, OSError):
        pass
    return results


def _search_in_directory_recursive(dir_path: str, pattern: re.Pattern, display_path: str) -> list:
    """
    Вспомогательная функция для рекурсивного поиска внутри директорий.
    Аргументы и возвращаемое значение те же, как в прошлых двух.
    """
    results = []
    try:
        for root, dirs, files in os.walk(dir_path):
            rel_root = os.path.relpath(root, os.path.dirname(dir_path)) if dir_path != root else os.path.basename(root)
            display_root = os.path.join(display_path, rel_root) if rel_root != '.' else display_path

            for file in files:
                file_path = os.path.join(root, file)
                display_file_path = os.path.join(display_root, file)
                file_results = _search_in_file(file_path, pattern, display_file_path)
                results.extend(file_results)
    except (PermissionError, OSError):
        pass
    return results


def _highlight_match(line: str, pattern: str) -> str:
    """
    Функция для красивого цветного вывода.
    """
    try:
        highlighted = pattern.sub(lambda m: f"\033[91m{m.group()}\033[0m", line)
        return highlighted
    except:
        return line