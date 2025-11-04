import os
import datetime
import argparse

def execute(self, args):
    """Функция команды ls (list)."""
    # Аргументы через argparse: флаг -l - для детального вывода; path - путь до директории,
    # о какой выводить информацию (если надо конкретную, а не текущую)
    parser = argparse.ArgumentParser(prog='ls', add_help=False)
    parser.add_argument('-l', action='store_true', help='detailed listing')
    parser.add_argument('path', nargs='?', help='path to list')

    try:
        parsed_args = parser.parse_args(args)
    except SystemExit:
        return None

    # Определение абсолютных/относительных путей для корректного выполнения команды
    if parsed_args.path:
        if os.path.isabs(parsed_args.path):
            target_dir = self.resolve_path(parsed_args.path)
        else:
            target_dir = os.path.join(self.current_dir, parsed_args.path)

        # Определение, является ли путь диском (для Windows)
        if not self.is_windows_drive(target_dir) and not target_dir.endswith("\\"):
            target_dir = os.path.normpath(target_dir)
    else:
        target_dir = self.current_dir

    # Ошибка, если путь не существует или не является директорией
    if not os.path.exists(target_dir):
        self.handle_error(
            f"ls: cannot access '{parsed_args.path if parsed_args.path else target_dir}': No such file or directory")
        return None

    if not os.path.isdir(target_dir):
        self.handle_error(f"ls: '{parsed_args.path if parsed_args.path else target_dir}': Not a directory")
        return None

    try:
        # Ошибка, если нет прав для вывода информации о директории
        items = os.listdir(target_dir)
    except PermissionError:
        self.handle_error(
            f"ls: cannot open directory '{parsed_args.path if parsed_args.path else target_dir}': Permission denied")
        return None
    except FileNotFoundError:
        self.handle_error(
            f"ls: cannot access '{parsed_args.path if parsed_args.path else target_dir}': No such file or directory")
        return None

    items.sort(key=lambda x: (not os.path.isdir(os.path.join(target_dir, x)), x.lower()))

    if parsed_args.l:
        _ls_detailed(items, target_dir)
    else:
        _ls_simple(items, target_dir)

    return None

def _ls_simple(items, target_dir):
    """
    Вспомогательная функция для простого вывода.
    Аргументы: items - файлы внутри; target_dir - директория, в которой лежат эти файлы.
    Возвращаемое значение: None (информация выводится через print)
    """
    for item in items:
        if os.path.isdir(os.path.join(target_dir, item)):
            print(f"\033[94m{item}\033[0m")
        else:
            print(item)

def _ls_detailed(self, items, target_dir):
    """
    Вспомогательная функция для детального вывода.
    """
    for item in items:
        full_path = os.path.join(target_dir, item)
        try:
            stat = os.stat(full_path)

            # Считывание типа файла, разрешений для трех групп пользователей,
            # последнего времени изменения и развера
            file_type = 'd' if os.path.isdir(full_path) else '-'
            permissions = file_type + 'rw-r--r--'
            size = stat.st_size
            mod_time = datetime.datetime.fromtimestamp(stat.st_mtime)
            mod_time_str = mod_time.strftime('%Y-%m-%d %H:%M:%S')

            if os.path.isdir(full_path):
                item_display = f"\033[94m{item}\033[0m"
            else:
                item_display = item

            print(f"{permissions} {size:8} {mod_time_str} {item_display}")

        except (OSError, PermissionError) as e:
            self.handle_error(f"ls: cannot access '{item}': {e}")

