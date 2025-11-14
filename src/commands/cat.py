import os
import sys

def execute(self, args: list[str]) -> None:
    """
    :param args: Аргументы (обрабатывает только первый в списке -
    путь до файла, который нужно прочитать)
    :return: Данная функция ничего не возвращает
    """
    if not args:
        self.handle_error(f"cat: no file operands were given")
        return None

    filename = args[0]

    file_path = self.resolve_user_path(filename)

    try:
        # Ошибка, если путь не существует
        if not os.path.exists(file_path):
            self.handle_error(f"cat: {filename}: no such file or directory")
            return None

        # Ошибка, если путь до файла - директория
        if os.path.isdir(file_path):
            self.handle_error(f"cat: {filename}: can't read content - given file is a directory")
            return None

        # Чтение файла и вывод его содержимого в кодировке UTF-8.
        # В случае ошибки - попытка чтения и вывода в кодировке latin-1.
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    for line in file:
                        self.logger.debug(f"DEBUG: Writing line: {repr(line)}")
                        sys.stdout.write(line)

            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='latin-1') as file:
                        content = file.read()
                        sys.stdout.write(content)

                except (UnicodeDecodeError, LookupError):
                    self.handle_error(f"cat: {filename}: Cannot read file (binary or unsupported encoding)")

            except PermissionError:
                self.handle_error(f"cat: {filename}: Permission denied")

    except Exception as e:
        self.handle_error(f"cat: {filename}: unexpected error: {e}")