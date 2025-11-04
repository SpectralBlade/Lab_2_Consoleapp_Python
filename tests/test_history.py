from unittest.mock import Mock
from commands.history import execute

class TestHistoryCommand:
    def test_history_show_all(self, mocker):
        shell = Mock()
        shell.command_history = [
            {'command': 'ls', 'args': ['-l'], 'success': True, 'timestamp': '2024-01-01T10:00:00'},
            {'command': 'cd', 'args': ['..'], 'success': True, 'timestamp': '2024-01-01T10:01:00'},
            {'command': 'invalid', 'args': [], 'success': False, 'timestamp': '2024-01-01T10:02:00'}
        ]
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, [])
        assert mock_print.call_count == 3
        assert result is None

    def test_history_show_last_n(self, mocker):
        shell = Mock()
        shell.command_history = [
            {'command': 'ls', 'args': ['-l'], 'success': True, 'timestamp': '2024-01-01T10:00:00'},
            {'command': 'cd', 'args': ['..'], 'success': True, 'timestamp': '2024-01-01T10:01:00'},
            {'command': 'pwd', 'args': [], 'success': True, 'timestamp': '2024-01-01T10:02:00'}
        ]
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['2'])
        assert mock_print.call_count == 2
        assert result is None

    def test_history_empty(self, mocker):
        shell = Mock()
        shell.command_history = []
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, [])
        mock_print.assert_called_once_with("No command history")
        assert result is None

    def test_history_more_than_available(self, mocker):
        shell = Mock()
        shell.command_history = [
            {'command': 'ls', 'args': [], 'success': True, 'timestamp': '2024-01-01T10:00:00'},
            {'command': 'cd', 'args': ['~'], 'success': True, 'timestamp': '2024-01-01T10:01:00'}
        ]
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['5'])
        assert mock_print.call_count == 2
        assert result is None

    def test_history_single_command(self, mocker):
        shell = Mock()
        shell.command_history = [
            {'command': 'ls', 'args': ['-la'], 'success': True, 'timestamp': '2024-01-01T10:00:00'}
        ]
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['1'])
        assert mock_print.call_count == 1
        assert result is None