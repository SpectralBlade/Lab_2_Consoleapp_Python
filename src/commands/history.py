def execute(self, args: list) -> None:
    """
    Функция для вывода команды history для показа пользователю истории команд.
    :param args: Аргументы (обрабатывает только первый в списке -
    число последних команд для вывода)
    :return: Данная функция ничего не возвращает
    """
    n = None
    if args:
        try:
            n = int(args[0])
            if n <= 0:
                self.handle_error("history: argument must be a positive number")
                return None
        except ValueError:
            self.handle_error("history: argument must be a number")
            return None

    # Если был введен номер, показать столько последних команд,
    # если нет - всю историю
    if n is not None:
        n = min(n, len(self.command_history))
        history_to_show = self.command_history[-n:]
    else:
        history_to_show = self.command_history
        n = len(history_to_show)

    if not history_to_show:
        print("No command history")
        return None

    # Форматирование вывода для более удобного чтения его пользователем.
    # Эмодзи, чтобы пользователь знал, если команда выполнена успешно/неуспешно.
    start_index = len(self.command_history) - n + 1
    for i, entry in enumerate(history_to_show, start=start_index):
        status = "✓" if entry['success'] else "✗"
        command_str = f"{entry['command']} {' '.join(entry['args'])}" if entry['args'] else entry['command']
        print(f"{i:4} {status} {entry['timestamp']} {command_str}")

    self.logger.debug(f"Displayed {len(history_to_show)} history entries")
    return None