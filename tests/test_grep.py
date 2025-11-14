from unittest.mock import Mock, mock_open
from commands.grep import execute

class TestGrepCommand:
    def test_grep_file_found_matches(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isfile', return_value=True)
        mock_print = mocker.patch('builtins.print')

        file_content = "hello world\nthis is a test\ngoodbye world"
        mocker.patch('builtins.open', mock_open(read_data=file_content))

        result = execute(shell, ['world', 'file.txt'])
        assert mock_print.call_count == 2
        shell.handle_error.assert_not_called()

    def test_grep_file_no_matches(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isfile', return_value=True)
        mock_print = mocker.patch('builtins.print')

        file_content = "apple banana\ncherry date"
        mocker.patch('builtins.open', mock_open(read_data=file_content))

        result = execute(shell, ['orange', 'file.txt'])
        mock_print.assert_called_once_with("No matches found for pattern 'orange' in 'file.txt'")
        shell.handle_error.assert_not_called()

    def test_grep_case_insensitive(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isfile', return_value=True)
        mock_print = mocker.patch('builtins.print')

        file_content = "Hello WORLD\nhello world\nHELLO"
        mocker.patch('builtins.open', mock_open(read_data=file_content))

        result = execute(shell, ['-i', 'hello', 'file.txt'])
        assert mock_print.call_count == 3
        shell.handle_error.assert_not_called()

    def test_grep_recursive_directory(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_user_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)
        mocker.patch('os.walk')
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['-r', 'pattern', 'directory'])
        mock_print.assert_called_once_with("No matches found for pattern 'pattern' in 'directory'")
        shell.handle_error.assert_not_called()

    def test_grep_directory_non_recursive(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_user_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)
        mocker.patch('os.listdir')
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['pattern', 'directory'])
        mock_print.assert_called_once_with("No matches found for pattern 'pattern' in 'directory'")
        shell.handle_error.assert_not_called()

    def test_grep_nonexistent_path(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=False)
        result = execute(shell, ['pattern', 'nonexistent'])
        shell.handle_error.assert_called_once_with("grep: cannot access 'nonexistent': No such file or directory")

    def test_grep_invalid_pattern(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isfile', return_value=True)
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['[invalid', 'file.txt'])
        shell.handle_error.assert_called_once()

    def test_grep_permission_error(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isfile', return_value=True)
        mocker.patch('builtins.open', side_effect=PermissionError("Permission denied"))
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['pattern', 'protected.txt'])
        mock_print.assert_called_once_with("No matches found for pattern 'pattern' in 'protected.txt'")
        shell.handle_error.assert_not_called()