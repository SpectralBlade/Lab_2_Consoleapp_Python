import os

def execute(self, args: list) -> None:
    """
    :param args: Аргументы (обрабатывает только первый в списке - путь,
    куда нужно перейти)
    :return: Данная функция ничего не возвращает
    """
    # Если путь не указан - переход в корневую директорию
    if not args:
        new_path = os.path.expanduser("~")
    else:
        path = args[0]

        # Обработка корневого/родительского каталога как пути
        if path == "~":
            new_path = os.path.expanduser("~")
        elif path == "..":
            if self.is_windows_drive(self.current_dir) or self.current_dir.endswith(r"\\"):
                new_path = self.current_dir
            else:
                new_path = os.path.dirname(self.current_dir)
        else:
            if self.is_windows_drive(path) or self.is_windows_drive(path.upper()):
                new_path = self.resolve_path(path)
            else:
                new_path = self.resolve_user_path(path)

    if os.path.exists(new_path) and os.path.isdir(new_path):
        self.current_dir = new_path
        if self.is_windows_drive(new_path.rstrip(r"\\")):
            self.current_dir = new_path.rstrip(r"\\") + r"\\"
    else:
        self.handle_error(f"cd: {new_path}: No such directory\n")
