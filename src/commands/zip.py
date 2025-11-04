import os
import argparse
import zipfile

def execute(self, args):
    """
    Функция для запуска команды zip.
    """
    # Аргументы через аргпарсе: folder - из какого каталога создать архив,
    # name - желаемое имя архива
    parser = argparse.ArgumentParser(prog='zip', add_help=False)
    parser.add_argument('folder', help='directory to zip')
    parser.add_argument('name', help='name of the zip archive')

    try:
        parsed_args = parser.parse_args(args)
    except SystemExit:
        return None

    # Определение абсолютных/относительных путей для корректного выполнения команды
    if os.path.isabs(parsed_args.folder):
        folder_path = self.resolve_path(parsed_args.folder)
    else:
        folder_path = os.path.join(self.current_dir, parsed_args.folder)

    # Определение, является ли путь диском (для Windows)
    if not self.is_windows_drive(folder_path) and not folder_path.endswith("\\"):
        folder_path = os.path.normpath(folder_path)

    # Ошибка, если путь не существует
    if not os.path.exists(folder_path):
        self.handle_error(f"zip: cannot access '{parsed_args.folder}': No such file or directory")
        return None

    # Ошибка, если путь не является каталогом
    if not os.path.isdir(folder_path):
        self.handle_error(f"zip: '{parsed_args.folder}': Not a directory")
        return None

    # Определение итогового пути и добавление .zip к имени файла,
    # если гений-пользователь такого не сделал
    zip_filename = parsed_args.name
    if not zip_filename.endswith('.zip'):
        zip_filename += '.zip'

    zip_path = os.path.join(self.current_dir, zip_filename)

    try:
        # Попытка создания сжатого архива и записи в него файлов из каталога
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(folder_path))
                    zipf.write(file_path, arcname)

        # Сейчас 5:37 утра. Соседи долбят мне по потолку всю ночь, отплясывая чечетку.
        # МАТУШКА ЗЕМЛЯ, БЕЛАЯ БЕРЕЗОНЬКА, ДЛЯ МЕНЯ СВЯТАЯ РУСЬ, ДЛЯ ДРУГИХ ЗАНОЗОНЬКА
        # А еще я не сделал тесты для cat и grep
        self.logger.debug(f"Created zip archive '{zip_path}' from '{folder_path}'")
        print(f"Successfully created archive '{parsed_args.name}' from '{parsed_args.folder}'")

    except PermissionError:
        self.handle_error(f"zip: cannot create archive '{parsed_args.name}': Permission denied")
    except OSError as e:
        self.handle_error(f"zip: cannot create archive '{parsed_args.name}': {e}")
    except Exception as e:
        self.handle_error(f"zip: unexpected error: {e}")