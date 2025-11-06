import shutil
import os
from unittest.mock import Mock
from commands.cp import execute

class TestCpCommand:
    def test_cp_file_to_file(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=False)
        mocker.patch('shutil.copy2')
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['source.txt', 'dest.txt'])
        assert result is not None
        mock_print.assert_called_once_with("Copied 'source.txt' to 'dest.txt'")
        shell.handle_error.assert_not_called()

    def test_cp_file_to_directory(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', side_effect=lambda x: x == 'destination_dir')
        mocker.patch('shutil.copy2')
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['source.txt', 'destination_dir'])
        assert result is not None
        mock_print.assert_called_once_with("Copied 'source.txt' to 'destination_dir'")
        shell.handle_error.assert_not_called()

    def test_cp_directory_without_r_flag(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)

        result = execute(shell, ['source_dir', 'dest_dir'])
        assert result is None
        shell.handle_error.assert_called_once_with("cp: -r not specified; omitting directory 'source_dir'")

    def test_cp_directory_with_r_flag(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)
        mocker.patch('shutil.copytree')
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['-r', 'source_dir', 'dest_dir'])
        assert result is not None
        mock_print.assert_called_once_with("Copied 'source_dir' to 'dest_dir'")
        shell.handle_error.assert_not_called()

    def test_cp_directory_to_existing_directory(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)
        mocker.patch('shutil.copytree')
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['-r', 'source_dir', 'existing_dir'])
        assert result is not None
        mock_print.assert_called_once_with("Copied 'source_dir' to 'existing_dir'")
        shell.handle_error.assert_not_called()

    def test_cp_nonexistent_source(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=False)

        result = execute(shell, ['nonexistent.txt', 'dest.txt'])
        assert result is None
        shell.handle_error.assert_called_once_with("cp: cannot stat 'nonexistent.txt': No such file or directory")

    def test_cp_permission_error(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=False)
        mocker.patch('shutil.copy2', side_effect=PermissionError("Permission denied"))

        result = execute(shell, ['source.txt', '/protected/dest.txt'])
        assert result is None
        shell.handle_error.assert_called_once_with("cp: cannot copy 'source.txt': Permission denied")

    def test_cp_same_file_error(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=False)
        mocker.patch('shutil.copy2', side_effect=shutil.SameFileError())

        result = execute(shell, ['file.txt', 'file.txt'])
        assert result is None
        shell.handle_error.assert_called_once_with("cp: 'file.txt' and 'file.txt' are the same file")

    def test_cp_os_error(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=False)
        mocker.patch('shutil.copy2', side_effect=OSError("Disk full"))

        result = execute(shell, ['source.txt', 'dest.txt'])
        assert result is None
        shell.handle_error.assert_called_once_with("cp: cannot copy 'source.txt': Disk full")

    def test_cp_relative_paths(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: os.path.join(shell.current_dir, x))
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=False)
        mocker.patch('shutil.copy2')
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['docs/source.txt', 'backups/dest.txt'])
        assert result is not None
        mock_print.assert_called_once_with("Copied 'docs/source.txt' to 'backups/dest.txt'")
        shell.handle_error.assert_not_called()