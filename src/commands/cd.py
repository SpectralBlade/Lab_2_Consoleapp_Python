import os

def execute(self, args):
    if not args:
        new_path = os.path.expanduser("~")
    else:
        path = args[0]

        if path == "~":
            new_path = os.path.expanduser("~")
        elif path == "..":
            if self.is_windows_drive(self.current_dir) or self.current_dir.endswith("\\"):
                new_path = self.current_dir
            else:
                new_path = os.path.dirname(self.current_dir)
        else:
            if self.is_windows_drive(path) or self.is_windows_drive(path.upper()):
                new_path = self.resolve_path(path)
            elif os.path.isabs(path):
                new_path = self.resolve_path(path)
            else:
                new_path = os.path.join(self.current_dir, path)

    if not self.is_windows_drive(new_path) and not new_path.endswith("\\"):
        new_path = os.path.normpath(new_path)

    if os.path.exists(new_path) and os.path.isdir(new_path):
        self.current_dir = new_path
        if self.is_windows_drive(new_path.rstrip("\\")):
            self.current_dir = new_path.rstrip("\\") + "\\"
    else:
        self.handle_error(f"cd: {new_path}: No such directory\n")
