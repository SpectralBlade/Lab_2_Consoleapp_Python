import os
import argparse
import tarfile


def execute(self, args):
    """
    Функция для выполнения команды tar.
    """
    # Аргументы через argparse: folder - из какого каталога создать архив;
    # name - желаемое имя архива.
    parser = argparse.ArgumentParser(prog='tar', add_help=False)
    parser.add_argument('folder', help='directory to archive')
    parser.add_argument('name', help='name of the tar archive')

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
        self.handle_error(f"tar: cannot access '{parsed_args.folder}': No such file or directory")
        return None

    # Ошибка, если путь не является каталогом
    if not os.path.isdir(folder_path):
        self.handle_error(f"tar: '{parsed_args.folder}': Not a directory")
        return None

    # Добавить tar.gz к названию архива, если пользователь не написал его
    tar_filename = parsed_args.name
    if not tar_filename.endswith(('.tar', '.tar.gz', '.tgz', '.tar.bz2', '.tbz')):
        tar_filename += '.tar.gz'

    # Определение конечного пути и настройка сжатия
    tar_path = os.path.join(self.current_dir, tar_filename)
    compression_mode = 'w'
    if tar_filename.endswith('.tar.gz') or tar_filename.endswith('.tgz'):
        compression_mode = 'w:gz'

    # Открытие каталога через tarfile и добавление его файлов в архив
    try:
        with tarfile.open(tar_path, compression_mode) as tar:
            tar.add(folder_path, arcname=os.path.basename(folder_path))

        self.logger.debug(f"Created tar archive '{tar_path}' from '{folder_path}'")
        print(f"Successfully created archive '{parsed_args.name}' from '{parsed_args.folder}'")

    except PermissionError:
        self.handle_error(f"tar: cannot create archive '{parsed_args.name}': Permission denied")
    except OSError as e:
        self.handle_error(f"tar: cannot create archive '{parsed_args.name}': {e}")
    except Exception as e:
        self.handle_error(f"tar: unexpected error: {e}")