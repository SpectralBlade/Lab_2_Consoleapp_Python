import os
import tarfile
from Lab_2_Consoleapp_Python.src.commands.parsing.command_parsers import parse_untar_args


def execute(self, args: list) -> None:
    """
    :param args: Аргументы: archive - что нужно разархивировать.
    :return: Данная функция ничего не возвращает
    """
    parsed_args = parse_untar_args(args)
    if parsed_args is None:
        return None

    # Определение абсолютных/относительных путей для корректного выполнения команды
    if os.path.isabs(parsed_args.archive):
        archive_path = self.resolve_path(parsed_args.archive)
    else:
        archive_path = os.path.join(self.current_dir, parsed_args.archive)

    # Определение, является ли путь диском (для Windows)
    if not self.is_windows_drive(archive_path) and not archive_path.endswith("\\"):
        archive_path = os.path.normpath(archive_path)

    # Ошибка, если путь не существует
    if not os.path.exists(archive_path):
        self.handle_error(f"untar: cannot access '{parsed_args.archive}': No such file or directory")
        return None

    # Ошибка, если переданный файл является каталогом
    if not os.path.isfile(archive_path):
        self.handle_error(f"untar: '{parsed_args.archive}': Not a file")
        return None

    try:
        # Распаковка архива с записью в логи
        with tarfile.open(archive_path, 'r') as tar:
            members = tar.getmembers()
            tar.extractall(self.current_dir)
            file_count = len(members)

            self.logger.debug(f"Extracted {file_count} files from '{archive_path}' to '{self.current_dir}'")
            print(f"Successfully extracted {file_count} files from '{parsed_args.archive}'")

    # Ошибка, если архив не удалось прочитать или он поврежден
    except tarfile.ReadError:
        self.handle_error(f"untar: '{parsed_args.archive}': Not a tar archive or corrupted")
    except PermissionError:
        self.handle_error(f"untar: cannot extract '{parsed_args.archive}': Permission denied")
    except OSError as e:
        self.handle_error(f"untar: cannot extract '{parsed_args.archive}': {e}")
    except Exception as e:
        self.handle_error(f"untar: unexpected error: {e}")