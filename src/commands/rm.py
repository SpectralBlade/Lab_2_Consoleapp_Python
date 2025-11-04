import os
import argparse
import shutil
import datetime


def execute(self, args):
    """
    Функция для выполнения команды rm (remove) - удаление файла/каталога.
    """
    # Аргументы через argparse: флаг -r - для удаления каталога;
    # path - путь до объекта, который нужно удалить
    parser = argparse.ArgumentParser(prog='rm', add_help=False)
    parser.add_argument('-r', action='store_true', help='remove directories recursively')
    parser.add_argument('path', help='file or directory path to remove')

    try:
        parsed_args = parser.parse_args(args)
    except SystemExit:
        return None

    # Определение абсолютных/относительных путей для корректного выполнения команды
    if os.path.isabs(parsed_args.path):
        target_path = self.resolve_path(parsed_args.path)
    else:
        target_path = os.path.join(self.current_dir, parsed_args.path)

    # Определение, является ли путь диском (для Windows)
    if not self.is_windows_drive(target_path) and not target_path.endswith("\\"):
        target_path = os.path.normpath(target_path)

    # Ошибка, если путь не существует
    if not os.path.exists(target_path):
        self.handle_error("rm: cannot remove '{parsed_args.path}': No such file or directory")
        return None

    # Ошибка, если путь защищен от удаления
    if _is_protected_path(self, target_path):
        self.handle_error("rm: cannot remove '{parsed_args.path}': Operation not permitted")
        return None

    # Сбор информации (для добавления в конец имени файла, чтобы было проще
    # отменить удаление при выполнении undo)
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        basename = os.path.basename(target_path)
        trash_path = os.path.join(self.trash_dir, f"{basename}_{timestamp}")

        # Без флага -r каталог удалить не получится
        if os.path.isdir(target_path):
            if not parsed_args.r:
                self.handle_error(f"rm: cannot remove '{parsed_args.path}': Is a directory")
                return None

            # Прекращение операции, если ее не подтвердили (удаление каталога)
            if not _confirm_deletion(parsed_args.path):
                print("Operation cancelled.")
                return None

            # Перемещение файла во временный каталог .trash, запись в логи,
            # возврат словаря значений для undo
            shutil.move(target_path, trash_path)
            self.logger.debug(f"Moved directory '{target_path}' to trash at '{trash_path}'")
            print(f"Moved directory '{parsed_args.path}' to trash")

        else:
            shutil.move(target_path, trash_path)
            self.logger.debug(f"Moved file '{target_path}' to trash at '{trash_path}'")
            print(f"Moved file '{parsed_args.path}' to trash")

        return {
            'original_path': target_path,
            'trash_path': trash_path
        }

    except PermissionError as e:
        self.handle_error(f"rm: cannot remove '{parsed_args.path}': Permission denied")
        return None
    except OSError as e:
        self.handle_error(f"rm: cannot remove '{parsed_args.path}': {e}")
        return None
    except Exception as e:
        self.handle_error(f"rm: unexpected error: {e}")
        return None


def _is_protected_path(shell, path):
    normalized_path = os.path.normpath(path)
    if (path == ".." or
            normalized_path == ".." or
            path.endswith("/..") or
            path.endswith("\\..") or
            any(part == ".." for part in normalized_path.split(os.sep))):
        return True
    if (path == "." or
            normalized_path == "." or
            path.endswith("/.") or
            path.endswith("\\.") or
            any(part == "." for part in normalized_path.split(os.sep))):
        return True
    if shell.is_windows_drive(path.rstrip("\\")) or path in ["/", "\\"]:
        return True
    if os.name == 'nt':
        drive, tail = os.path.splitdrive(path)
        if drive and (not tail or tail in ['\\', '/']):
            return True
    if os.name != 'nt' and path == '/':
        return True

    try:
        current_normalized = os.path.normpath(shell.current_dir)
        target_normalized = os.path.normpath(path)
        if (current_normalized != target_normalized and
                current_normalized.startswith(target_normalized) and
                os.path.dirname(current_normalized) == target_normalized):
            return True
    except:
        pass

    return False


def _confirm_deletion(path):
    response = input(f"rm: remove directory '{path}'? (y/n): ").strip().lower()
    return response in ['y', 'yes']