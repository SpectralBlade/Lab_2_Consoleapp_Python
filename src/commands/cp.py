import os
import argparse
import shutil

def execute(self, args):
    """
    Функция для вызова команды cp (copy).
    """
    # Добавление аргументов через argparse. Аргументы: флаг -r - для рекурсивного копирования директорий;
    # source - что копировать; destination - куда копировать.
    parser = argparse.ArgumentParser(prog='cp', add_help=False)
    parser.add_argument('-r', action='store_true', help='copy directories recursively')
    parser.add_argument('source', help='source file or directory')
    parser.add_argument('destination', help='destination path')

    try:
        parsed_args = parser.parse_args(args)
    except SystemExit:
        return None

    # Определение абсолютных/относительных путей для корректного выполнения команды
    if os.path.isabs(parsed_args.source):
        source_path = self.resolve_path(parsed_args.source)
    else:
        source_path = os.path.join(self.current_dir, parsed_args.source)

    if os.path.isabs(parsed_args.destination):
        dest_path = self.resolve_path(parsed_args.destination)
    else:
        dest_path = os.path.join(self.current_dir, parsed_args.destination)

    # Определение, является ли путь диском (для Windows)
    if not self.is_windows_drive(source_path) and not source_path.endswith("\\"):
        source_path = os.path.normpath(source_path)
    if not self.is_windows_drive(dest_path) and not dest_path.endswith("\\"):
        dest_path = os.path.normpath(dest_path)

    # Ошибка, если путь не существует
    if not os.path.exists(source_path):
        self.handle_error(f"cp: cannot stat '{parsed_args.source}': No such file or directory")
        return None

    try:
        # Ошибка, если копируется директория без флага -r
        if os.path.isdir(source_path):
            if not parsed_args.r:
                self.handle_error(f"cp: -r not specified; omitting directory '{parsed_args.source}'")
                return None

            # Проверка, является ли путь (куда скопировать) директорией
            if os.path.isdir(dest_path):
                dest_dir = os.path.join(dest_path, os.path.basename(source_path))
            else:
                dest_dir = dest_path

            # Копирование директории (ниже - файла)
            shutil.copytree(source_path, dest_dir, dirs_exist_ok=True)
            self.logger.debug(f"Copied directory '{source_path}' to '{dest_dir}'")

        else:
            if os.path.isdir(dest_path):
                dest_file = os.path.join(dest_path, os.path.basename(source_path))
            else:
                dest_file = dest_path

            shutil.copy2(source_path, dest_file)

        print(f"Copied '{parsed_args.source}' to '{parsed_args.destination}'")
        return {
            'source': source_path,
            'destination': dest_file if not os.path.isdir(source_path) else dest_dir
        }

    except PermissionError:
        self.handle_error(f"cp: cannot copy '{parsed_args.source}': Permission denied")
    except shutil.SameFileError:
        self.handle_error(f"cp: '{parsed_args.source}' and '{parsed_args.destination}' are the same file")
    except OSError as e:
        self.handle_error(f"cp: cannot copy '{parsed_args.source}': {e}")
    except Exception as e:
        self.handle_error(f"cp: unexpected error: {e}")