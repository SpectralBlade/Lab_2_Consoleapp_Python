import os
import shutil
from Lab_2_Consoleapp_Python.src.commands.parsing.command_parsers import parse_cp_args

def execute(self, args: list[str]) -> dict | None:
    """
    :param args: Аргументы: флаг -r - для рекурсивного копирования директорий;
    source - что копировать; destination - куда копировать.
    :return: Данная функция ничего не возвращает
    """
    parsed_args = parse_cp_args(args)
    if parsed_args is None:
        return None

    # Определение абсолютных/относительных путей для корректного выполнения команды
    source_path = self.resolve_user_path(parsed_args.source)
    dest_path = self.resolve_user_path(parsed_args.destination)

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