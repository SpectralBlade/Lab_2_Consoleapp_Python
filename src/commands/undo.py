import os
import shutil

def execute(self, args = None) -> dict:
    """
    :param args: None (нет аргументов)
    :return: Отмененная команда (или None)
    """
    # Возможно отменить только cp, mv, rm
    undoable_commands = ['cp', 'mv', 'rm']

    for entry in reversed(self.command_history):
        if entry['command'] in undoable_commands and entry['success'] and entry.get('undo_data'):
            return _undo_command(self, entry)

    print("No undoable commands found in history")
    return None


def _undo_command(self, history_entry: dict) -> dict:
    """
    Вспомогательная функция. Отменяет последнюю команду из списка в истории.
    :param history_entry: последняя найденная команда и ее данные.
    :return: cловарь с данными об отмене, если она успешна, или None в случае ошибки
    """
    command = history_entry['command']
    undo_data = history_entry['undo_data']

    try:
        # Удаление скопированного
        if command == 'cp':
            destination = undo_data.get('destination')
            if os.path.exists(destination):
                if os.path.isdir(destination):
                    shutil.rmtree(destination)
                else:
                    os.remove(destination)
                print(f"Undo cp: removed {destination}")
                self.logger.debug(f"Undid cp command: removed {destination}")
            else:
                print(f"Undo cp: destination {destination} no longer exists")

        # Перемещение файла/каталога в обратное место
        elif command == 'mv':
            source = undo_data.get('source')
            destination = undo_data.get('destination')
            if os.path.exists(destination):
                shutil.move(destination, source)
                print(f"Undo mv: moved {destination} back to {source}")
                self.logger.debug(f"Undid mv command: moved {destination} back to {source}")
            else:
                print(f"Undo mv: destination {destination} no longer exists")

        # Перемещение файла из каталога корзины и восстановление его нормального имени
        elif command == 'rm':
            original_path = undo_data.get('original_path')
            trash_path = undo_data.get('trash_path')
            if os.path.exists(trash_path):
                os.makedirs(os.path.dirname(original_path), exist_ok=True)
                shutil.move(trash_path, original_path)
                print(f"Undo rm: restored {original_path} from trash")
                self.logger.debug(f"Undid rm command: restored {original_path} from trash")
            else:
                print(f"Undo rm: file not found in trash: {trash_path}")

        # Сохранение истории и очистка данных для отмены команды
        history_entry['undo_data'] = None
        self._save_history()

        return {'undo': True, 'command': command}

    except Exception as e:
        self.handle_error(f"Failed to undo {command}: {e}")
        return None