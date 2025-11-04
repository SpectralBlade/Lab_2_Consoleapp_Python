from unittest.mock import Mock
import tarfile
from commands.untar import execute

class TestUntarCommand:
    def test_untar_file(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isfile', return_value=True)
        mock_tarfile = mocker.patch('tarfile.open')
        mock_members = [Mock(), Mock(), Mock()]
        mock_tarfile.return_value.__enter__.return_value.getmembers.return_value = mock_members
        mock_tarfile.return_value.__enter__.return_value.extractall = Mock()
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['archive.tar'])
        assert result is None
        mock_print.assert_called_once_with("Successfully extracted 3 files from 'archive.tar'")
        shell.handle_error.assert_not_called()

    def test_untar_gz_file(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isfile', return_value=True)
        mock_tarfile = mocker.patch('tarfile.open')
        mock_members = [Mock(), Mock()]
        mock_tarfile.return_value.__enter__.return_value.getmembers.return_value = mock_members
        mock_tarfile.return_value.__enter__.return_value.extractall = Mock()
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['archive.tar.gz'])
        assert result is None
        mock_print.assert_called_once_with("Successfully extracted 2 files from 'archive.tar.gz'")
        shell.handle_error.assert_not_called()

    def test_untar_nonexistent_file(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=False)

        result = execute(shell, ['nonexistent.tar'])
        assert result is None
        shell.handle_error.assert_called_once_with("untar: cannot access 'nonexistent.tar': No such file or directory")

    def test_untar_directory_instead_of_file(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isfile', return_value=False)

        result = execute(shell, ['somedir'])
        assert result is None
        shell.handle_error.assert_called_once_with("untar: 'somedir': Not a file")

    def test_untar_corrupted_file(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isfile', return_value=True)
        mock_tarfile = mocker.patch('tarfile.open', side_effect=tarfile.ReadError("Corrupted file"))

        result = execute(shell, ['corrupted.tar'])
        assert result is None
        shell.handle_error.assert_called_once_with("untar: 'corrupted.tar': Not a tar archive or corrupted")

    def test_untar_permission_error(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isfile', return_value=True)
        mock_tarfile = mocker.patch('tarfile.open', side_effect=PermissionError("Permission denied"))

        result = execute(shell, ['archive.tar'])
        assert result is None
        shell.handle_error.assert_called_once_with("untar: cannot extract 'archive.tar': Permission denied")