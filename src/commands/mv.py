import os
import shutil
from Lab_2_Consoleapp_Python.src.commands.parsing.command_parsers import parse_mv_args

def execute(self, args: list) -> dict | None:
    """
    :param args: Аргументы: source - что копировать; destination - куда копировать.
    :return: Данная функция ничего не возвращает
    """
    parsed_args = parse_mv_args(args)
    if parsed_args is None:
        return None

    source_path = self.resolve_user_path(parsed_args.source)
    dest_path = self.resolve_user_path(parsed_args.destination)

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