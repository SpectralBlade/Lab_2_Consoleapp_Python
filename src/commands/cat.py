import os
import sys

def execute(self, args):
    if not args:
        self.handle_error(f"cat: no file operands were given")
        return None

    filename = args[0]

    if os.path.isabs(filename):
        file_path = self.resolve_path(filename)
    else:
        file_path = os.path.join(self.current_dir, filename)

    if not self.is_windows_drive(file_path) and not file_path.endswith("\\"):
        file_path = os.path.normpath(file_path)

    try:
        if not os.path.exists(file_path):
            self.handle_error(f"cat: {filename}: no such file or directory")
            return None

        if os.path.isdir(file_path):
            self.handle_error(f"cat: {filename}: can't read content - given file is a directory")
            return None

        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    for line in file:
                        print(f"DEBUG: Writing line: {repr(line)}")  # Отладочный вывод
                        sys.stdout.write(line)

            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='latin-1') as file:
                        content = file.read()
                        sys.stdout.write(content)

                except Exception:
                    self.handle_error(f"cat: {filename}: Cannot read file (binary or unsupported encoding)")

            except PermissionError:
                self.handle_error(f"cat: {filename}: Permission denied")

    except Exception as e:
        self.handle_error(f"cat: {filename}: unexpected error: {e}")