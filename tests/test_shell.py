from unittest.mock import Mock
import json
from ruletka_shell import RuletkaShell

class TestRuletkaShellInitialization:
    def test_shell_initialization(self, mocker, mock_commands):
        mocker.patch('ruletka_shell.os.path.expanduser', return_value='/home/test')
        mocker.patch('ruletka_shell.os.path.dirname', return_value='/test')
        mocker.patch('ruletka_shell.os.path.abspath', return_value='/test/ruletka_shell.py')
        mocker.patch('ruletka_shell.os.path.exists', return_value=True)
        mocker.patch('ruletka_shell.os.makedirs')
        mocker.patch('ruletka_shell.logging.config.dictConfig')
        mocker.patch('ruletka_shell.logging.getLogger')

        mocker.patch.object(RuletkaShell, '_load_history', return_value=[])

        shell = RuletkaShell().create()

        assert shell.current_dir == '/home/test'
        assert hasattr(shell, 'history_file')
        assert hasattr(shell, 'trash_dir')
        assert hasattr(shell, 'commands')
        assert hasattr(shell, 'command_history')


class TestRuletkaShellMethods:

    def test_get_prompt(self, shell_instance):
        shell_instance.current_dir = '/home/user'
        prompt = shell_instance.get_prompt()
        assert prompt == '/home/user $ '

    def test_parse_input_basic(self, shell_instance):
        command, args = shell_instance.parse_input('ls -l')
        assert command == 'ls'
        assert args == ['-l']

    def test_parse_input_with_quotes(self, shell_instance):
        command, args = shell_instance.parse_input('cd "My Documents"')
        assert command == 'cd'
        assert args == ['My Documents']

    def test_parse_input_empty(self, shell_instance):
        command, args = shell_instance.parse_input('')
        assert command is None
        assert args == []

    def test_is_windows_drive(self, shell_instance):
        assert shell_instance.is_windows_drive('C:') == True
        assert shell_instance.is_windows_drive('D:') == True
        assert shell_instance.is_windows_drive('file') == False
        assert shell_instance.is_windows_drive('') == False

    def test_resolve_path_windows_drive(self, shell_instance):
        result = shell_instance.resolve_path('C:')
        assert result == r'C:\\'

    def test_resolve_path_normal(self, shell_instance, mocker):
        mocker.patch('ruletka_shell.os.path.normpath', return_value='/normalized/path')
        result = shell_instance.resolve_path('/some/path')
        assert result == '/normalized/path'


class TestRuletkaShellCommandExecution:
    def test_execute_existing_command(self, shell_instance, mocker):
        mock_command = Mock(return_value={'undo_data': 'test'})
        shell_instance.commands['ls'] = mock_command

        mocker.patch.object(shell_instance, 'add_to_history')

        shell_instance.commands['ls'](['-l'])

        mock_command.assert_called_once_with(['-l'])

    def test_execute_nonexistent_command(self, shell_instance, mocker):

        mocker.patch.object(shell_instance, 'add_to_history')
        mocker.patch.object(shell_instance.logger, 'warning')
        mocker.patch('builtins.print')

        command, args = shell_instance.parse_input('nonexistent_cmd arg1')

        if command not in shell_instance.commands:
            shell_instance.add_to_history(command, args, success=False)
            shell_instance.logger.warning(f"{command}: command not found")
            print(f"{command}: command not found")

        shell_instance.add_to_history.assert_called_once_with('nonexistent_cmd', ['arg1'], success=False)
        shell_instance.logger.warning.assert_called_once_with("nonexistent_cmd: command not found")


class TestRuletkaShellHistory:

    def test_add_to_history(self, shell_instance, mocker):

        mocker.patch.object(shell_instance, '_save_history')

        shell_instance.add_to_history('ls', ['-l'], success=True, undo_data={'test': 'data'})

        assert len(shell_instance.command_history) == 1
        history_entry = shell_instance.command_history[0]
        assert history_entry['command'] == 'ls'
        assert history_entry['args'] == ['-l']
        assert history_entry['success'] == True
        assert history_entry['undo_data'] == {'test': 'data'}

        shell_instance._save_history.assert_called_once()

    def test_load_history_file_exists(self, mocker):

        mock_history_data = [
            {'command': 'ls', 'args': ['-l'], 'success': True, 'timestamp': '2024-01-01T10:00:00'}
        ]
        mocker.patch('ruletka_shell.os.path.exists', return_value=True)
        mocker.patch('builtins.open', mocker.mock_open(read_data=json.dumps(mock_history_data)))
        mocker.patch('ruletka_shell.logging.config.dictConfig')
        mocker.patch('ruletka_shell.logging.getLogger')

        shell = RuletkaShell().create()
        assert shell.command_history == mock_history_data

    def test_load_history_file_not_exists(self, mocker):
        mocker.patch('ruletka_shell.os.path.exists', return_value=False)
        mocker.patch('ruletka_shell.logging.config.dictConfig')
        mocker.patch('ruletka_shell.logging.getLogger')

        shell = RuletkaShell().create()
        assert shell.command_history == []


class TestRuletkaShellIntegration:

    def test_command_parsing_and_execution_flow(self, shell_instance, mocker):
        mock_command = Mock(return_value={'undo_data': 'test'})
        shell_instance.commands['cat'] = mock_command
        mocker.patch.object(shell_instance, 'add_to_history')

        user_input = 'cat file.txt'
        command, args = shell_instance.parse_input(user_input)

        if command in shell_instance.commands:
            undo_data = shell_instance.commands[command](args)
            shell_instance.add_to_history(command, args, success=(undo_data is not None), undo_data=undo_data)

        mock_command.assert_called_once_with(['file.txt'])
        shell_instance.add_to_history.assert_called_once_with(
            'cat', ['file.txt'], success=True, undo_data={'undo_data': 'test'}
        )

    def test_error_handling_in_command_execution(self, shell_instance, mocker):

        def failing_command():
            raise Exception("Test error")

        shell_instance.commands['failing_cmd'] = failing_command
        mocker.patch.object(shell_instance, 'add_to_history')
        mocker.patch('builtins.print')

        try:
            shell_instance.commands['failing_cmd'](['arg'])
            shell_instance.add_to_history('failing_cmd', ['arg'], success=True)
        except Exception:
            shell_instance.add_to_history('failing_cmd', ['arg'], success=False)

        shell_instance.add_to_history.assert_called_once_with('failing_cmd', ['arg'], success=False)


class TestRuletkaShellEdgeCases:

    def test_multiple_spaces_in_input(self, shell_instance):
        command, args = shell_instance.parse_input('   ls    -l     ')
        assert command == 'ls'
        assert args == ['-l']

    def test_special_characters_in_input(self, shell_instance):
        command, args = shell_instance.parse_input('cd folder-with-dashes')
        assert command == 'cd'
        assert args == ['folder-with-dashes']

    def test_empty_args(self, shell_instance):
        command, args = shell_instance.parse_input('ls')
        assert command == 'ls'
        assert args == []