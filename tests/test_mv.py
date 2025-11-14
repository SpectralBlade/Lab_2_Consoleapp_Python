import os
from unittest.mock import Mock
from commands.mv import execute

class TestMvCommand:
    def test_mv_file_rename(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_user_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('shutil.move')
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['old.txt', 'new.txt'])
        assert result is not None
        mock_print.assert_called_once_with("Moved 'old.txt' to 'new.txt'")
        shell.handle_error.assert_not_called()

    def test_mv_file_to_directory(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', side_effect=lambda x: x != 'dest_dir/file.txt')
        mocker.patch('os.path.isdir', side_effect=lambda x: x == 'dest_dir')
        mocker.patch('shutil.move')
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['file.txt', 'dest_dir'])
        assert result is not None
        mock_print.assert_called_once_with("Moved 'file.txt' to 'dest_dir'")
        shell.handle_error.assert_not_called()

    def test_mv_directory_rename(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_user_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)
        mocker.patch('shutil.move')
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['old_dir', 'new_dir'])
        assert result is not None
        mock_print.assert_called_once_with("Moved 'old_dir' to 'new_dir'")
        shell.handle_error.assert_not_called()

    def test_mv_nonexistent_source(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=False)

        result = execute(shell, ['nonexistent.txt', 'dest.txt'])
        assert result is None
        shell.handle_error.assert_called_once_with("mv: cannot stat 'nonexistent.txt': No such file or directory")

    def test_mv_permission_error(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_user_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('shutil.move', side_effect=PermissionError("Permission denied"))

        result = execute(shell, ['source.txt', '/protected/dest.txt'])
        assert result is None
        shell.handle_error.assert_called_once_with("mv: cannot move 'source.txt': Permission denied")

    def test_mv_os_error_parent_not_exists(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', side_effect=lambda x: x == 'source.txt')
        mocker.patch('shutil.move', side_effect=OSError("Target directory does not exist"))

        result = execute(shell, ['source.txt', '/nonexistent/path/dest.txt'])
        assert result is None
        shell.handle_error.assert_called_once()

    def test_mv_absolute_path_rename(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_user_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('shutil.move')
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['/home/user/source.txt', '/home/user/new.txt'])
        assert result is not None
        mock_print.assert_called_once_with("Moved '/home/user/source.txt' to '/home/user/new.txt'")
        shell.handle_error.assert_not_called()

    def test_mv_relative_paths(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_user_path = Mock(side_effect=lambda x: os.path.join(shell.current_dir, x))
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('shutil.move')
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['docs/source.txt', 'backups/dest.txt'])
        assert result is not None
        mock_print.assert_called_once_with("Moved 'docs/source.txt' to 'backups/dest.txt'")
        shell.handle_error.assert_not_called()

    def test_mv_overwrite_existing_file(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_user_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('shutil.move')
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['source.txt', 'existing.txt'])
        assert result is not None
        mock_print.assert_called_once_with("Moved 'source.txt' to 'existing.txt'")
        shell.handle_error.assert_not_called()