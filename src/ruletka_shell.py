import os
import datetime
import logging, logging.config
import json
import shlex
from Lab_2_Consoleapp_Python.src.source.config import LOGGING_CONFIG
from Lab_2_Consoleapp_Python.src.commands import cd, ls, cat, mv, rm, cp, zip, unzip, tar, untar, grep, history, undo

class RuletkaShell:
    def __init__(self):
        """
        Основная функция инициализации класса оболочки. Задает параметры, подгружает
        историю при запуске, инициализирует логирование и проверяет наличие .history и .trash
        """
        # Основные параметры: начальная директория, путь до файла истории и каталога "корзины"
        self.current_dir = os.path.expanduser("~")
        self.history_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.history.json')
        self.trash_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.trash')
        # Словарь с поддерживаемыми командами и привязанными к ним импротированными функциями
        self.commands = {
            "cd": lambda args: cd(self, args),
            "ls": lambda args: ls(self, args),
            "cat": lambda args: cat(self, args),
            "cp": lambda args: cp(self, args),
            "mv": lambda args: mv(self, args),
            "rm": lambda args: rm(self, args),
            "zip": lambda args: zip(self, args),
            "unzip": lambda args: unzip(self, args),
            "tar": lambda args: tar(self, args),
            "untar": lambda args: untar(self, args),
            "grep": lambda args: grep(self, args),
            "history": lambda args: history(self, args),
            "undo": lambda args: undo(self, args),
            "exit": self.exit
        }
        # Инициализация логирования, подгрузка истории и проверка наличия .history и .trash
        self.logging_stat()
        self.command_history = self._load_history()
        self._ensure_directories()

    def _ensure_directories(self):
        """
        Функция, проверяющая наличие файла истории и директории корзины. В случае их отсутствии
        (not os.path.exists) пытается создать их в директории src, при неудаче показывает пользователю
        сообщение об ошибке при запуске консоли.
        """
        if not os.path.exists(self.trash_dir):
            try:
                os.makedirs(self.trash_dir, exist_ok=True)
                self._log(f"Created trash directory: {self.trash_dir}")
            except Exception as e:
                self._log(f"Failed to create trash directory: {e}")

        if not os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
                self._log(f"Created history file: {self.history_file}")
            except Exception as e:
                self._log(f"Failed to create history file: {e}")

    def _log(self, message):
        """
        Функция для вывода пользователю debug-сообщений о корзине/истории.
        """
        print(f"Shell init: {message}")

    def _load_history(self):
        """
        Функция для подгрузки истории. Запускается во время первой инициализации.
        Возвращаемое значение: history_data (list) - история команд, сохраняющаяся
        между запусками и загружаемая из файла .history.json. Ошибка в случае
        невозможности прочитать файл.
        """
        history_data = []
        try:
            if os.path.exists(self.history_file) and os.path.getsize(self.history_file) > 0:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
                self._log(f"Loaded {len(history_data)} history entries")
            else:
                self._log("History file is empty or doesn't exist")
        except (json.JSONDecodeError, IOError) as e:
            self._log(f"Error loading history: {e}")
            try:
                with open(self.history_file, 'w', encoding='utf-8') as f:
                    json.dump([], f)
            except:
                pass
        return history_data

    def _save_history(self):
        """
        Функция для сохранения истории. После выполнения каждой команды делает дамп в файл
        .history.json с данными о выполненной командой и добавляет запись в shell.log о том,
        сколько записей в истории сохранено на данный момент. Если историю сохранить не получилось,
        пользователю показывается ошибка.
        """
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.command_history, f, ensure_ascii=False, indent=2)
            if hasattr(self, 'logger'):
                self.logger.debug(f"Saved {len(self.command_history)} history entries")
        except IOError as e:
            error_msg = f"Failed to save history: {e}"
            self.handle_error(error_msg)

    def add_to_history(self, command, args, success=True, undo_data=None):
        """
        Функция для непосредственного добавления команды в список и затем сохранение этого списка
        в .history.json. Аргументы: выполненная команда, ее аргументы, успех (True/False), дата
        для отмены (для команд rm, cp, mv). После добавления информации о выполненной команде
        вызывает функцию _save_history.
        """
        # Данные о команде для добавления в историю
        history_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'command': command,
            'args': args,
            'success': success,
            'undo_data': undo_data
        }
        # Сохранение команды в историю, затем сохранение самой истории
        self.command_history.append(history_entry)
        self._save_history()

    def logging_stat(self):
        """
        Функция для настройки логирования. Запускается при инициализации консоли.
        """
        logging.config.dictConfig(LOGGING_CONFIG)
        self.logger = logging.getLogger("RuletkaShell")

    def handle_error(self, message):
        """
        Базовая функция для логирования ошибок и вывода их пользователю. Аргумент: message (str) -
        добавляется как запись в файл логов и выводится пользователю в print.
        """
        self.logger.error(message)
        print(message)

    def get_prompt(self):
        """
        Функция для вывода текущей директории, в которой находится пользователь. Возвращаемое значение -
        путь и значок $, как в терминалах MacOS/Linux.
        """
        return f"{self.current_dir} $ "

    def parse_input(self, input_string):
        """
        Парсинг команды и ее аргументов. shlex.split нужен для правильного разбиения
        аргументов (поможет, если, например, в названии папки есть пробел. cd 'My Documents'
        """
        try:
            parts = shlex.split(input_string.strip())
        except ValueError:
            parts = input_string.strip().split()

        if not parts:
            return None, []

        command = parts[0]
        args = parts[1:]
        return command, args

    def is_windows_drive(self, path):
        """
        Функция, определяющая, является ли путь диском (для Windows, для нормализации
        пути и корректности отображения). Возвращаемое значение - bool.
        """
        return len(path) == 2 and path[1] == ':' and path[0].isalpha()

    def resolve_path(self, path):
        """
        Функция для разрешения проблем с путями (для дисков Windows, была проблема - что
        вместо корневого каталога на диске программа цепляла путь, где лежит файл консоли
        (ruletka_shell.py), как основной.
        """
        if self.is_windows_drive(path) or self.is_windows_drive(path.upper()):
            return path.upper() + "\\"
        else:
            return os.path.normpath(path)

    def exit(self, args = None):
        """
        Выход из консоли.
        """
        print("Goodbye!")
        exit(0)

    def run(self):
        """
        Функция, выполняемая при инициализации консоли. Выводит пользователю приветственное
        сообщение и постоянно парсит ввод пользователя, определяя его как существующую/нет
        команду. Возвращает результат для команды, если она есть в списке поддерживаемых и вызывает
        функцию для добавления ее в историю. Для команд cp, mv, rm также добавляет значение
        успех-неуспех и данные для отмены. При ошибках - выводит их текст пользователю.
        """
        print("Welcome to RuletkaShell. \nAvailable commands: cd, ls, cat, mv, rm, "
              "cp, zip, unzip, tar, untar, grep, history, undo.")

        while True:
            try:
                user_input = input(self.get_prompt()).strip()
                if not user_input:
                    continue

                command, args = self.parse_input(user_input)
                self.logger.debug(user_input)

                if command in self.commands:
                    result = self.commands[command](args)

                    success = True
                    undo_data = None

                    if command in ['cp', 'mv', 'rm']:
                        success = result is not None
                        undo_data = result if success else None
                    else:
                        success = True
                        undo_data = None

                    self.add_to_history(command, args, success=success, undo_data=undo_data)
                else:
                    self.handle_error(f"{command}: command not found")
                    self.add_to_history(command, args, success=False)

            except KeyboardInterrupt:
                self.logger.info("KeyboardInterrupt received")
                print("\nUse 'exit' to quit")
            except EOFError:
                self.logger.info("EOF received - exiting")
                print("\nGoodbye!")
                break
            except Exception as e:
                self.handle_error(f"Unexpected error: {e}")