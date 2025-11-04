import os
from unittest.mock import Mock
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))
from commands.zip import execute


class TestZipCommand:

    def test_zip_directory_default_name(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)
        mock_zipfile = mocker.patch('zipfile.ZipFile')
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['docs', 'backup'])
        assert result is None
        mock_print.assert_called_once_with("Successfully created archive 'backup' from 'docs'")
        shell.handle_error.assert_not_called()

    def test_zip_directory_with_zip_extension(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)
        mock_zipfile = mocker.patch('zipfile.ZipFile')
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['docs', 'backup.zip'])
        assert result is None
        mock_print.assert_called_once_with("Successfully created archive 'backup.zip' from 'docs'")
        shell.handle_error.assert_not_called()

    def test_zip_nonexistent_directory(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=False)

        result = execute(shell, ['nonexistent', 'archive'])
        assert result is None
        shell.handle_error.assert_called_once_with("zip: cannot access 'nonexistent': No such file or directory")

    def test_zip_file_instead_of_directory(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=False)

        result = execute(shell, ['file.txt', 'archive'])
        assert result is None
        shell.handle_error.assert_called_once_with("zip: 'file.txt': Not a directory")

    def test_zip_permission_error(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)
        mock_zipfile = mocker.patch('zipfile.ZipFile', side_effect=PermissionError("Permission denied"))

        result = execute(shell, ['docs', '/protected/archive.zip'])
        assert result is None
        shell.handle_error.assert_called_once_with("zip: cannot create archive '/protected/archive.zip': Permission denied")

    def test_zip_os_error(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)
        mock_zipfile = mocker.patch('zipfile.ZipFile', side_effect=OSError("Disk full"))

        result = execute(shell, ['docs', 'archive'])
        assert result is None
        shell.handle_error.assert_called_once_with("zip: cannot create archive 'archive': Disk full")

    def test_zip_relative_path(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: os.path.join(shell.current_dir, x))
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)
        mock_zipfile = mocker.patch('zipfile.ZipFile')
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['projects/docs', 'backup'])

        assert result is None
        mock_print.assert_called_once_with("Successfully created archive 'backup' from 'projects/docs'")
        shell.handle_error.assert_not_called()

    def test_zip_absolute_path(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)
        mock_zipfile = mocker.patch('zipfile.ZipFile')
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['/var/www', 'webbackup'])

        assert result is None
        mock_print.assert_called_once_with("Successfully created archive 'webbackup' from '/var/www'")
        shell.handle_error.assert_not_called()