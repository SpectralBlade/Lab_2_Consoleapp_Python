from unittest.mock import Mock
from commands.tar import execute

class TestTarCommand:
    def test_tar_directory_default_name(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)
        mock_tarfile = mocker.patch('tarfile.open')
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['docs', 'backup'])

        assert result is None
        mock_print.assert_called_once_with("Successfully created archive 'backup' from 'docs'")
        shell.handle_error.assert_not_called()

    def test_tar_directory_with_gz_extension(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)
        mock_tarfile = mocker.patch('tarfile.open')
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['docs', 'backup.tar.gz'])

        assert result is None
        mock_print.assert_called_once_with("Successfully created archive 'backup.tar.gz' from 'docs'")
        shell.handle_error.assert_not_called()

    def test_tar_nonexistent_directory(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=False)

        result = execute(shell, ['nonexistent', 'archive'])
        assert result is None
        shell.handle_error.assert_called_once_with("tar: cannot access 'nonexistent': No such file or directory")

    def test_tar_file_instead_of_directory(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=False)

        result = execute(shell, ['file.txt', 'archive'])
        assert result is None
        shell.handle_error.assert_called_once_with("tar: 'file.txt': Not a directory")

    def test_tar_permission_error(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)
        mock_tarfile = mocker.patch('tarfile.open', side_effect=PermissionError("Permission denied"))

        result = execute(shell, ['docs', '/protected/archive.tar'])
        assert result is None
        shell.handle_error.assert_called_once_with("tar: cannot create archive '/protected/archive.tar': Permission denied")