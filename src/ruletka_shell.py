import os
import datetime
import logging, logging.config
import json
import shlex
from abc import ABC, abstractmethod
from Lab_2_Consoleapp_Python.src.source.config import LOGGING_CONFIG
from Lab_2_Consoleapp_Python.src.commands import cd, ls, cat, mv, rm, cp, zip, unzip, tar, untar, grep, history, undo, help


class Shell(ABC):
    """
    Абстрактный базовый класс для оболочек командной строки.
    Определяет общий интерфейс для всех реализаций оболочек.
    """
    @abstractmethod
    def __init__(self) -> None:
        """Инициализация оболочки."""
        pass

    @abstractmethod
    def run(self) -> None:
        """Основной цикл выполнения оболочки."""
        pass

    @abstractmethod
    def get_prompt(self) -> str:
        """Возвращает строку приглашения."""
        pass

    @abstractmethod
    def parse_input(self, input_string: str) -> tuple:
        """Парсит введенную пользователем строку."""
        pass

    @abstractmethod
    def handle_error(self, message: str) -> None:
        """Обрабатывает и отображает ошибки."""
        pass

    @abstractmethod
    def is_windows_drive(self, path: str) -> bool:
        """Проверяет, является ли путь диском Windows."""
        pass

    @abstractmethod
    def resolve_path(self, path: str) -> str:
        """Нормализует и разрешает путь."""
        pass

    @abstractmethod
    def exit(self, args=None) -> None:
        """Завершает работу оболочки."""
        pass

    @abstractmethod
    def add_to_history(self, command: str, args: list, success: bool = True, undo_data=None) -> None:
        """Добавляет команду в историю."""
        pass

    @abstractmethod
    def logging_stat(self) -> None:
        """Настраивает логирование."""
        pass

class RuletkaShell(Shell):
    @staticmethod
    def create():
        """
        Фабричный метод для создания экземпляра RuletkaShell с отложенной инициализацией.
        :return: Экземпляр класса RuletkaShell
        """
        instance = RuletkaShell()
        instance._opers_init()
        return instance

    def __init__(self) -> None:
        """
        Функция-инициализатор оболочки.
        :return: Данная функция ничего не возвращает
        """
        # Основные параметры: начальная директория, путь до файла истории и каталога "корзины"
        self.current_dir = os.path.expanduser("~")
        self.history_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.history.json')
        self.trash_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.trash')
        # Словарь с поддерживаемыми командами и привязанными к ним импортированными функциями
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
            "help": lambda args: help(self, args),
            "exit": self.exit
        }
        self._initialized = False

    def _opers_init(self) -> None:
        """
        Выполняет дорогостоящие операции инициализации.
        :return: Данная функция ничего не возвращает
        """
        if not self._initialized:
            self.logging_stat()
            self.command_history = self._load_history()
            self._ensure_directories()
            self._initialized = True

    def _ensure_directories(self) -> None:
        """
        Создает .history и .trash при их отсутствии.
        :return: Данная функция ничего не возвращает
        """
        if not os.path.exists(self.trash_dir):
            try:
                os.makedirs(self.trash_dir, exist_ok=True)
                self._log(f"Created trash directory: {self.trash_dir}")
            except PermissionError:
                self._log(f"Failed to create trash directory at {self.trash_dir}: Permission denied")
            except OSError as e:
                self._log(f"Failed to create trash directory: {e}")
            except Exception as e:
                self._log(f"Unexpected error occured while trying to"
                          f" create trash directory: {e}")

        if not os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
                self._log(f"Created history file: {self.history_file}")
            except PermissionError:
                self._log(f"Failed to create history file at {self.history_file}: Permission denied")
            except OSError as e:
                self._log(f"Failed to create trash directory: {e}")
            except Exception as e:
                self._log(f"Unexpected error occured while trying to "
                          f"create history file: {e}")

    def _log(self, message) -> None:
        """
        Функция для вывода пользователю debug-сообщений о корзине/истории через print.
        :param message: Текст сообщения
        :return: Данная функция ничего не возвращает
        """
        print(f"Shell init: {message}")

    def _load_history(self) -> list:
        """
        Загружает историю команд из файла.
        :return: Список записей истории команд
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
            self._log(f"Error loading history: {e}. Try 'rm {os.path.abspath(self.history_file)}' and then relaunch the shell.")
        return history_data

    def _save_history(self) -> None:
        """
        Функция для сохранения истории в файл .history.
        :return: Данная функция ничего не возвращает
        """
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.command_history, f, ensure_ascii=False, indent=2)
            if hasattr(self, 'logger'):
                self.logger.debug(f"Saved {len(self.command_history)} history entries")
        except IOError as e:
            error_msg = f"Failed to save history: {e}"
            self.handle_error(error_msg)

    def add_to_history(self, command: str, args: list[str], success: bool = True, undo_data = None) -> None:
        """
        Функция для добавления выполненной команды в историю.
        :param command: какая команда была отправлена пользователем в консоль
        :param args: аргументы отправленной команды
        :param success: выполнилась команда или нет (bool)
        :param undo_data: данные для отмены (по умолчанию None)
        :return: Данная функция ничего не возвращает
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

    def logging_stat(self) -> None:
        """
        Функция для настройки логирования. Запускается при инициализации консоли.
        :return: Данная функция ничего не возвращает
        """
        logging.config.dictConfig(LOGGING_CONFIG)
        self.logger = logging.getLogger("RuletkaShell")

    def handle_error(self, message: str) -> None:
        """
        Базовая функция для логирования ошибок и вывода их пользователю.
        :param message:
        :return: Данная функция ничего не возвращает
        """
        self.logger.error(message)
        print(message)

    def get_prompt(self) -> str:
        """
        Функция для вывода текущей директории, в которой находится пользователь.
        :return: Текущий каталог (с символом $)
        """
        return f"{self.current_dir} $ "

    def parse_input(self, input_string: str) -> tuple:
        """
        Парсинг пользовательского ввода.
        :param input_string: введенная пользователем строка
        :return: кортеж с командой и аргументами
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

    def is_windows_drive(self, path: str) -> bool:
        """
        Функция для разрешения проблем с путями (для дисков Windows).
        :param path: текущий путь
        :return: является диском или нет (bool)
        """
        return len(path) == 2 and path[1] == ':' and path[0].isalpha()

    def resolve_path(self, path: str) -> str:
        """
        Функция для разрешения проблем с путями (для дисков Windows).
        :param path: текущий путь
        :return: исправленный путь (если каталог является диском Windows)
        """
        if self.is_windows_drive(path) or self.is_windows_drive(path.upper()):
            return path.upper() + r"\\"
        else:
            return os.path.normpath(path)

    def resolve_user_path(self, path: str) -> str:
        """
        Функция для разрешения пользовательского пути, обрабатывает
        абсолютные и относительные, нормализует их.
        :param path: путь, введенный пользователем
        :return: абсолютный нормализованный путь
        """
        if os.path.isabs(path):
            final_path = self.resolve_path(path)
        else:
            final_path = os.path.join(self.current_dir, path)

        if not self.is_windows_drive(final_path) and not final_path.endswith(r"\\"):
            final_path = os.path.normpath(final_path)

        return final_path

    def exit(self, args = None) -> None:
        """
        :param args: None (нет аргументов)
        :return: Данная функция ничего не возвращает
        """
        print("Goodbye!")
        exit(0)

    def run(self) -> None:
        """
        Функция для вывода приветственного сообщения и запуска работы программы (парсинга команд).
        :return: Данная функция ничего не возвращает
        """

        print("Welcome to RuletkaShell. \nType 'help' for available commands.")

        while (user_input := input(self.get_prompt()).strip()) != "exit":
            try:
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

        # Обработка команды "exit"
        self.exit()