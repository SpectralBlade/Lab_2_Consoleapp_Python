import os
import argparse
import shutil

def execute(self, args):
    """
    Функция для вызова команды mv для перемещения/переименовывания файла.
    """
    # Аргументы через argparse: source - что копировать; destination - куда копировать.
    parser = argparse.ArgumentParser(prog='mv', add_help=False)
    parser.add_argument('source', help='source file or directory')
    parser.add_argument('destination', help='destination path or new name')

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
        self.handle_error(f"mv: cannot stat '{parsed_args.source}': No such file or directory")
        return None

    try:

        # Составление пути, куда скопировать файл/директорию
        # (проверка на новое имя/на существование конечного пути)
        if os.path.isdir(dest_path):
            final_dest = os.path.join(dest_path, os.path.basename(source_path))

        elif not os.path.exists(dest_path):
            parent_dir = os.path.dirname(dest_path)
            if parent_dir and parent_dir != '.':
                if not os.path.exists(parent_dir):
                    self.handle_error(f"Target directory '{parent_dir}' does not exist")
                if not os.path.isdir(parent_dir):
                    self.handle_error(f"'{parent_dir}' is not a directory")
            final_dest = dest_path

        else:
            final_dest = dest_path

        # Копирование с записью в логи и возврат словаря значений для undo
        shutil.move(source_path, final_dest)
        self.logger.debug(f"Moved '{source_path}' to '{final_dest}'")
        print(f"Moved '{parsed_args.source}' to '{parsed_args.destination}'")
        return {
            'source': source_path,
            'destination': final_dest
        }

    except PermissionError:
        self.handle_error(f"mv: cannot move '{parsed_args.source}': Permission denied")
    except OSError as e:
        self.handle_error(f"mv: cannot move '{parsed_args.source}': {e}")
    except Exception as e:
        self.handle_error(f"mv: unexpected error: {e}")