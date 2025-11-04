from unittest.mock import Mock
from commands.undo import execute

class TestUndoCommand:
    def test_undo_cp_command(self, mocker):
        shell = Mock()
        shell.command_history = [
            {'command': 'ls', 'args': ['-l'], 'success': True, 'timestamp': '2024-01-01T10:00:00'},
            {'command': 'cp', 'args': ['src.txt', 'dest.txt'], 'success': True, 'undo_data': {
                'source': '/home/user/src.txt',
                'destination': '/home/user/dest.txt'
            }, 'timestamp': '2024-01-01T10:01:00'}
        ]
        shell._save_history = Mock()
        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=False)
        mocker.patch('os.remove')
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, [])
        assert result is not None
        mock_print.assert_called_once_with("Undo cp: removed /home/user/dest.txt")
        shell._save_history.assert_called_once()

    def test_undo_mv_command(self, mocker):
        shell = Mock()
        shell.command_history = [
            {'command': 'mv', 'args': ['old.txt', 'new.txt'], 'success': True, 'undo_data': {
                'source': '/home/user/old.txt',
                'destination': '/home/user/new.txt'
            }, 'timestamp': '2024-01-01T10:01:00'}
        ]
        shell._save_history = Mock()
        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('shutil.move')
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, [])
        assert result is not None
        mock_print.assert_called_once_with("Undo mv: moved /home/user/new.txt back to /home/user/old.txt")
        shell._save_history.assert_called_once()

    def test_undo_rm_command(self, mocker):
        shell = Mock()
        shell.command_history = [
            {'command': 'rm', 'args': ['file.txt'], 'success': True, 'undo_data': {
                'original_path': '/home/user/file.txt',
                'trash_path': '/home/user/.trash/file.txt_20240101_100000_123456'
            }, 'timestamp': '2024-01-01T10:01:00'}
        ]
        shell._save_history = Mock()
        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.makedirs')
        mocker.patch('shutil.move')
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, [])
        assert result is not None
        mock_print.assert_called_once_with("Undo rm: restored /home/user/file.txt from trash")
        shell._save_history.assert_called_once()

    def test_undo_no_undoable_commands(self, mocker):
        shell = Mock()
        shell.command_history = [
            {'command': 'ls', 'args': ['-l'], 'success': True, 'timestamp': '2024-01-01T10:00:00'},
            {'command': 'cd', 'args': ['..'], 'success': True, 'timestamp': '2024-01-01T10:01:00'}
        ]
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, [])

        assert result is None
        mock_print.assert_called_once_with("No undoable commands found in history")

    def test_undo_only_failed_commands(self, mocker):
        shell = Mock()
        shell.command_history = [
            {'command': 'cp', 'args': ['src.txt', 'dest.txt'], 'success': False, 'timestamp': '2024-01-01T10:00:00'},
            {'command': 'rm', 'args': ['file.txt'], 'success': False, 'timestamp': '2024-01-01T10:01:00'}
        ]
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, [])
        assert result is None
        mock_print.assert_called_once_with("No undoable commands found in history")

    def test_undo_cp_destination_not_exists(self, mocker):
        shell = Mock()
        shell.command_history = [
            {'command': 'cp', 'args': ['src.txt', 'dest.txt'], 'success': True, 'undo_data': {
                'source': '/home/user/src.txt',
                'destination': '/home/user/dest.txt'
            }, 'timestamp': '2024-01-01T10:01:00'}
        ]
        shell._save_history = Mock()
        mocker.patch('os.path.exists', return_value=False)
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, [])

        assert result is not None
        mock_print.assert_called_once_with("Undo cp: destination /home/user/dest.txt no longer exists")
        shell._save_history.assert_called_once()

    def test_undo_rm_trash_not_exists(self, mocker):
        shell = Mock()
        shell.command_history = [
            {'command': 'rm', 'args': ['file.txt'], 'success': True, 'undo_data': {
                'original_path': '/home/user/file.txt',
                'trash_path': '/home/user/.trash/file.txt_20240101_100000_123456'
            }, 'timestamp': '2024-01-01T10:01:00'}
        ]
        shell._save_history = Mock()
        mocker.patch('os.path.exists', return_value=False)
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, [])

        assert result is not None
        mock_print.assert_called_once_with(
            "Undo rm: file not found in trash: /home/user/.trash/file.txt_20240101_100000_123456")
        shell._save_history.assert_called_once()

    def test_undo_exception_handling(self, mocker):
        shell = Mock()
        shell.command_history = [
            {'command': 'cp', 'args': ['src.txt', 'dest.txt'], 'success': True, 'undo_data': {
                'source': '/home/user/src.txt',
                'destination': '/home/user/dest.txt'
            }, 'timestamp': '2024-01-01T10:01:00'}
        ]
        shell._save_history = Mock()
        mocker.patch('os.path.exists', side_effect=Exception("Test error"))

        result = execute(shell, [])
        assert result is None
        shell.handle_error.assert_called_once_with("Failed to undo cp: Test error")