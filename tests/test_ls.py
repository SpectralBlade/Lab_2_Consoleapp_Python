from unittest.mock import Mock
from commands.ls import execute

class TestLsCommand:
    def test_ls_current_directory_simple(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path.side_effect = lambda x: x
        shell.logger = Mock()

        mock_print = mocker.patch('builtins.print')
        mocker.patch('os.listdir', return_value=['file1.txt', 'file2.txt', 'folder1'])
        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)
        mocker.patch('os.path.join', side_effect=lambda *args: '/'.join(args))
        mocker.patch('os.path.normpath', side_effect=lambda x: x)

        execute(shell, [])

        assert mock_print.call_count == 3

    def test_ls_specific_directory(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path.side_effect = lambda x: x
        shell.logger = Mock()

        mock_print = mocker.patch('builtins.print')
        mocker.patch('os.path.isabs', return_value=False)
        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)
        mocker.patch('os.listdir', return_value=['file1.txt', 'file2.txt'])
        mocker.patch('os.path.join', side_effect=lambda *args: '/'.join(args))
        mocker.patch('os.path.normpath', side_effect=lambda x: x)

        execute(shell, ['documents'])

        assert mock_print.call_count == 2

    def test_ls_nonexistent_directory(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path.side_effect = lambda x: x
        shell.logger = Mock()

        mocker.patch('os.path.isabs', return_value=False)
        mocker.patch('os.path.exists', return_value=False)

        execute(shell, ['nonexistent'])

        shell.handle_error.assert_called_once()

    def test_ls_file_instead_of_directory(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path.side_effect = lambda x: x
        shell.logger = Mock()

        mocker.patch('os.path.isabs', return_value=False)
        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=False)

        execute(shell, ['file.txt'])

        shell.handle_error.assert_called_once()

    def test_ls_permission_error(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path.side_effect = lambda x: x
        shell.logger = Mock()

        mocker.patch('os.path.isabs', return_value=False)
        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)
        mocker.patch('os.listdir', side_effect=PermissionError("Permission denied"))

        execute(shell, ['protected'])
        shell.handle_error.assert_called_once()

    def test_ls_absolute_path(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path.side_effect = lambda x: x
        shell.logger = Mock()

        mock_print = mocker.patch('builtins.print')
        mocker.patch('os.path.isabs', return_value=True)
        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)
        mocker.patch('os.listdir', return_value=['file1.txt'])
        mocker.patch('os.path.normpath', side_effect=lambda x: x)

        execute(shell, ['/etc'])

        assert mock_print.call_count == 1

    def test_ls_with_file_not_found_error(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path.side_effect = lambda x: x
        shell.logger = Mock()

        mocker.patch('os.path.isabs', return_value=False)
        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)
        mocker.patch('os.listdir', side_effect=FileNotFoundError("Directory not found"))

        execute(shell, ['missing'])
        shell.handle_error.assert_called_once()

    def test_ls_empty_directory(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path.side_effect = lambda x: x
        shell.logger = Mock()

        mock_print = mocker.patch('builtins.print')
        mocker.patch('os.listdir', return_value=[])
        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)
        mocker.patch('os.path.join', side_effect=lambda *args: '/'.join(args))
        mocker.patch('os.path.normpath', side_effect=lambda x: x)

        execute(shell, [])

        assert mock_print.call_count == 0

    def test_ls_exception_handling(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path.side_effect = Exception("Test error")
        shell.logger = Mock()

        execute(shell, ['test'])
        shell.handle_error.assert_called_once()