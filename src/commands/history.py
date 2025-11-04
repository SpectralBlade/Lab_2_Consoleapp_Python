import argparse

def execute(self, args):
    """
    Функция для вывода команды history для показа пользователю истории команд.
    """
    # Аргумент n (число последних команд, которые нужно вывести) через argparse
    parser = argparse.ArgumentParser(prog='history', add_help=False)
    parser.add_argument('n', type=int, nargs='?', help='number of commands to show')

    try:
        parsed_args = parser.parse_args(args)
    except SystemExit:
        return None

    # Если был введен номер, показать столько последних команд,
    # если нет - всю историю
    if parsed_args.n is not None:
        n = min(parsed_args.n, len(self.command_history))
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