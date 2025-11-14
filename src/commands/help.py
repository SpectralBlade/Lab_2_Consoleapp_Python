from Lab_2_Consoleapp_Python.src.commands.parsing.command_parsers import parse_help_args


def execute(self, args: list) -> None:
    """
    Display help information about available commands.
    :param args: Arguments: command name (optional)
    :return: None
    """
    parsed_args = parse_help_args(args)

    # If no specific command is requested, show general help
    if not parsed_args or not parsed_args.command:
        _show_general_help()
    else:
        _show_command_help(parsed_args.command)


def _show_general_help() -> None:
    help_text = """
RuletkaShell - Custom Command Line Shell

Available commands:

  cd [directory]     - Change current directory
  ls [path] [-l]     - List directory contents (-l for detailed view)
  cat <file>         - Display file content
  cp <source> <dest> [-r] - Copy files/directories (-r for recursive)
  mv <source> <dest> - Move or rename files/directories
  rm <path> [-r]     - Remove files/directories (-r for recursive, moves to trash)
  zip <dir> <name>   - Create zip archive from directory
  unzip <archive>    - Extract zip archive to current directory
  tar <dir> <name>   - Create tar archive from directory
  untar <archive>    - Extract tar archive to current directory
  grep <pattern> <path> [-r] [-i] - Search for pattern in files
  history [n]        - Show command history (last n entries)
  undo               - Undo last cp, mv, or rm operation
  help [command]     - Show this help or specific command help
  exit               - Exit the shell

Type 'help <command>' for more information about a specific command.
Examples:
  help cd
  help grep
"""
    print(help_text)


def _show_command_help(command: str) -> None:
    command_help = {
        'cd': """
Usage: cd [directory]

Changes the current working directory.

Arguments:
  directory  - Target directory (optional)
              If no directory specified, changes to home directory
              ~  - Home directory
              .. - Parent directory

Examples:
  cd Documents          - Change to Documents directory
  cd ..                 - Go to parent directory  
  cd ~                  - Go to home directory
""",

        'ls': """
Usage: ls [path] [-l]

Lists files and directories in the specified path.

Arguments:
  path  - Directory or file path (optional, defaults to current directory)
  -l    - Detailed listing with file information

Examples:
  ls                    - List current directory
  ls -l                 - Detailed list of current directory
  ls Documents          - List Documents directory
  ls -l /var/log        - Detailed list of /var/log
""",

        'cat': """
Usage: cat <file>

Displays the contents of a file.

Arguments:
  file  - Path to the file to display

Examples:
  cat file.txt          - Display file.txt contents
  cat /etc/hosts.txt    - Display system hosts file
""",

        'cp': """
Usage: cp <source> <destination> [-r]

Copies files and directories.

Arguments:
  source      - Source file or directory
  destination - Destination path or directory
  -r          - Recursive copy (for directories)

Examples:
  cp file.txt backup.txt          - Copy file to backup
  cp -r dir1 dir2                 - Copy directory recursively
""",

        'mv': """
Usage: mv <source> <destination>

Moves or renames files and directories.

Arguments:
  source      - Source file or directory
  destination - Destination path or new name

Examples:
  mv old.txt new.txt              - Rename file
  mv file.txt Documents/          - Move file to Documents
  mv dir1/ dir2/                  - Rename directory
""",

        'rm': """
Usage: rm <path> [-r]

Removes files and directories (moves to trash for undo capability).

Arguments:
  path  - File or directory to remove
  -r    - Recursive removal (for directories)

Examples:
  rm file.txt                     - Remove file (moves to trash)
  rm -r old_directory             - Remove directory recursively
""",

        'grep': """
Usage: grep <pattern> <path> [-r] [-i]

Searches for patterns in files.

Arguments:
  pattern - Search pattern (regular expression)
  path    - File or directory to search in
  -r      - Recursive search in subdirectories
  -i      - Case-insensitive search

Examples:
  grep "error" log.txt            - Search for "error" in log.txt
  grep -r "function" src/         - Recursively search for "function" in src/
  grep -i "warning" err.log         - Case-insensitive search in err.log file
""",

        'history': """
Usage: history [n]

Shows command execution history.

Arguments:
  n  - Number of recent commands to show (optional)

Examples:
  history              - Show all command history
  history 10           - Show last 10 commands
""",

        'undo': """
Usage: undo

Undoes the last cp, mv, or rm operation.
""",
        'zip': """
Usage: zip <directory> <archive_name>

Creates a zip archive from a directory.

Arguments:
    directory    - Source directory to compress
    archive_name - Name of the zip archive (automatically adds .zip if not specified)

Examples:
    zip Documents docs_backup          - Create docs_backup.zip from Documents
    zip /var/log logs_archive.zip      - Create logs_archive.zip from /var/log
    zip "My Files" backup              - Create backup.zip from "My Files" directory
    """,

        'unzip': """
Usage: unzip <archive>

Extracts a zip archive to the current directory.

Arguments:
    archive - Path to the zip archive to extract

Features:
    - Supports password-protected archives (will prompt for password)
    - Preserves directory structure
    - Handles various compression methods

Examples:
    unzip archive.zip                  - Extract archive.zip to current directory
    unzip /downloads/backup.zip        - Extract backup.zip from downloads
    unzip encrypted.zip                - Will prompt for password if encrypted
    """,

        'tar': """
Usage: tar <directory> <archive_name>

Creates a tar archive from a directory. Supports various compression formats.

Arguments:
    directory    - Source directory to archive
    archive_name - Name of the tar archive

Examples:
    tar Documents docs_backup          - Create docs_backup.tar
    tar Projects projects.tar.gz       - Create gzip compressed archive
    """,

        'untar': """
Usage: untar <archive>

Extracts a tar archive to the current directory.

Arguments:
    archive - Path to the tar archive to extract

Features:
    - Supports .tar, .tar.gz, .tar.bz2 formats
    - Automatically detects compression type
    - Preserves file permissions and directory structure

Examples:
    untar archive.tar                  - Extract uncompressed tar archive
    untar backup.tar.gz                - Extract gzip compressed archive
    untar data.tar.bz2                 - Extract bzip2 compressed archive
    """
    }

    if command in command_help:
        print(command_help[command])
    else:
        print(f"help: no help topics found for '{command}'")