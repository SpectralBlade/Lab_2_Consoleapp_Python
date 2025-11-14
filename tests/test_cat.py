from unittest.mock import Mock, MagicMock
from commands.cat import execute

class TestCatCommand:
    def test_cat_successful_file_read(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(return_value='/home/user/test.txt')
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()
        shell.logger = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=False)
        mocker.patch('os.path.isfile', return_value=True)

        mock_stdout_write = mocker.patch('sys.stdout.write')

        mock_file_content = ["line1\n", "line2\n", "line3\n"]
        mock_file = MagicMock()
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=None)
        mock_file.__iter__ = Mock(return_value=iter(mock_file_content))

        mocker.patch('builtins.open', return_value=mock_file)

        execute(shell, ['test.txt'])

        assert mock_stdout_write.call_count == 3
        mock_stdout_write.assert_any_call("line1\n")
        mock_stdout_write.assert_any_call("line2\n")
        mock_stdout_write.assert_any_call("line3\n")
        shell.handle_error.assert_not_called()

    def test_cat_empty_file(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(return_value='/home/user/empty.txt')
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()
        shell.logger = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=False)
        mocker.patch('os.path.isfile', return_value=True)

        mock_stdout_write = mocker.patch('sys.stdout.write')

        mock_file = MagicMock()
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=None)
        mock_file.__iter__ = Mock(return_value=iter([]))

        mocker.patch('builtins.open', return_value=mock_file)

        execute(shell, ['empty.txt'])

        mock_stdout_write.assert_not_called()
        shell.handle_error.assert_not_called()

    def test_cat_single_line_file(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(return_value='/home/user/single.txt')
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()
        shell.logger = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=False)
        mocker.patch('os.path.isfile', return_value=True)

        mock_stdout_write = mocker.patch('sys.stdout.write')

        mock_file_content = ["single line content\n"]
        mock_file = MagicMock()
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=None)
        mock_file.__iter__ = Mock(return_value=iter(mock_file_content))

        mocker.patch('builtins.open', return_value=mock_file)

        execute(shell, ['single.txt'])

        mock_stdout_write.assert_called_once_with("single line content\n")
        shell.handle_error.assert_not_called()

    def test_cat_nonexistent_file(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(return_value='/home/user/nonexistent.txt')
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()
        shell.logger = Mock()

        mocker.patch('os.path.exists', return_value=False)

        execute(shell, ['nonexistent.txt'])

        shell.handle_error.assert_called_once()
        call_args = shell.handle_error.call_args[0][0]
        assert "no such file or directory" in call_args

    def test_cat_directory_instead_of_file(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(return_value='/home/user/documents')
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()
        shell.logger = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)

        execute(shell, ['documents'])

        shell.handle_error.assert_called_once()
        call_args = shell.handle_error.call_args[0][0]
        assert "given file is a directory" in call_args

    def test_cat_permission_error(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(return_value='/home/user/protected.txt')
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()
        shell.logger = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=False)
        mocker.patch('os.path.isfile', return_value=True)
        mocker.patch('builtins.open', side_effect=PermissionError("Permission denied"))

        execute(shell, ['protected.txt'])

        shell.handle_error.assert_called_once()
        call_args = shell.handle_error.call_args[0][0]
        assert "Permission denied" in call_args

    def test_cat_unicode_error_with_fallback(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(return_value='/home/user/binary.file')
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()
        shell.logger = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=False)
        mocker.patch('os.path.isfile', return_value=True)

        mock_stdout_write = mocker.patch('sys.stdout.write')

        mock_file_content = "binary content"

        def open_side_effect(*args, **kwargs):
            if 'utf-8' in kwargs.get('encoding', ''):
                raise UnicodeDecodeError('utf-8', b'\x00', 0, 1, 'invalid start byte')
            else:
                mock_file = MagicMock()
                mock_file.__enter__ = Mock(return_value=mock_file)
                mock_file.__exit__ = Mock(return_value=None)
                mock_file.read = Mock(return_value=mock_file_content)
                return mock_file

        mocker.patch('builtins.open', side_effect=open_side_effect)

        execute(shell, ['binary.file'])

        mock_stdout_write.assert_called_once_with("binary content")
        shell.handle_error.assert_not_called()

    def test_cat_unicode_error_with_fallback_failure(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(return_value='/home/user/binary.file')
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()
        shell.logger = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=False)
        mocker.patch('os.path.isfile', return_value=True)

        def open_side_effect(*args, **kwargs):
            raise UnicodeDecodeError('utf-8', b'\x00', 0, 1, 'invalid start byte')

        mocker.patch('builtins.open', side_effect=open_side_effect)

        execute(shell, ['binary.file'])

        shell.handle_error.assert_called_once()
        call_args = shell.handle_error.call_args[0][0]
        assert "Cannot read file" in call_args

    def test_cat_no_arguments(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(return_value='/home/user')
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()
        shell.logger = Mock()

        execute(shell, [])

        shell.handle_error.assert_called_once()
        call_args = shell.handle_error.call_args[0][0]
        assert "no file operands were given" in call_args

    def test_cat_relative_path_success(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(return_value='/home/user/documents/file.txt')
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()
        shell.logger = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=False)
        mocker.patch('os.path.isfile', return_value=True)

        mock_stdout_write = mocker.patch('sys.stdout.write')

        mock_file_content = ["relative path content\n"]
        mock_file = MagicMock()
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=None)
        mock_file.__iter__ = Mock(return_value=iter(mock_file_content))

        mocker.patch('builtins.open', return_value=mock_file)

        execute(shell, ['documents/file.txt'])

        mock_stdout_write.assert_called_once_with("relative path content\n")
        shell.handle_error.assert_not_called()

    def test_cat_absolute_path_success(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(return_value='/etc/config.txt')
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()
        shell.logger = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=False)
        mocker.patch('os.path.isfile', return_value=True)

        mock_stdout_write = mocker.patch('sys.stdout.write')

        mock_file_content = ["absolute path content\n"]
        mock_file = MagicMock()
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=None)
        mock_file.__iter__ = Mock(return_value=iter(mock_file_content))

        mocker.patch('builtins.open', return_value=mock_file)

        execute(shell, ['/etc/config.txt'])

        mock_stdout_write.assert_called_once_with("absolute path content\n")
        shell.handle_error.assert_not_called()