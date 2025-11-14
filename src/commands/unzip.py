import os
import zipfile
from Lab_2_Consoleapp_Python.src.commands.parsing.command_parsers import parse_unzip_args

def execute(self, args: list) -> None:
    """
    :param args: Аргументы: archive - что нужно разархивировать.
    :return: Данная функция ничего не возвращает
    """
    parsed_args = parse_unzip_args(args)
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
        self.handle_error(f"unzip: cannot access '{parsed_args.archive}': No such file or directory")
        return None

    # Ошибка, если путь не является файлом
    if not os.path.isfile(archive_path):
        self.handle_error(f"unzip: '{parsed_args.archive}': Not a file")
        return None

    # Ошибка, если путь не является архивом .zip
    if not zipfile.is_zipfile(archive_path):
        self.handle_error(f"unzip: '{parsed_args.archive}': Not a zip archive")
        return None

    try:
        # Попытка распаковать архив, проверка на наличие пароля
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            if zipf:
                for file_info in zipf.filelist:
                    if file_info.flag_bits & 0x1:
                        # Спросить у пользователя пароль, если ......
                        password = self._ask_for_password(parsed_args.archive)
                        if password is None:
                            print("Operation cancelled.")
                            return None
                        break
                else:
                    password = None

                if password:
                    zipf.setpassword(password.encode('utf-8'))

                zipf.extractall(self.current_dir)
                file_count = len(zipf.filelist)

                self.logger.debug(f"Extracted {file_count} files from '{archive_path}' to '{self.current_dir}'")
                print(f"Successfully extracted {file_count} files from '{parsed_args.archive}'")

    # Ошибка, если архив "плохой" (поврежден) или если пароль неверный
    except zipfile.BadZipFile:
        self.handle_error(f"unzip: '{parsed_args.archive}': Bad zip file")
    except RuntimeError as e:
        if 'password' in str(e).lower():
            self.handle_error(f"unzip: '{parsed_args.archive}': Incorrect password")
        else:
            self.handle_error(f"unzip: '{parsed_args.archive}': {e}")
    except PermissionError:
        self.handle_error(f"unzip: cannot extract '{parsed_args.archive}': Permission denied")
    except OSError as e:
        self.handle_error(f"unzip: cannot extract '{parsed_args.archive}': {e}")
    except Exception as e:
        self.handle_error(f"unzip: unexpected error: {e}")


def _ask_for_password(archive_name: str) -> str:
    """
    Вспомогательная функция для спроса пароля у пользователя.
    :param archive_name: Аргумент: archive_name - имя архива.
    :return: password.strip() если пользователь его ввел, или None
    при ошибке ввода/прерывании программы
    """
    try:
        password = input(f"Enter password for '{archive_name}': ")
        return password.strip()
    except (KeyboardInterrupt, EOFError):
        return None