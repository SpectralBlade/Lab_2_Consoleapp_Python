from unittest.mock import Mock
import zipfile
from commands.unzip import execute

class TestUnzipCommand:
    def test_unzip_encrypted_file_with_password(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isfile', return_value=True)

        mock_zip = Mock()
        mock_fileinfo = Mock()
        mock_fileinfo.flag_bits = 1
        mock_zip.filelist = [mock_fileinfo]
        mock_zip.extractall = Mock()
        mock_zip.setpassword = Mock()

        mock_zipfile_class = mocker.patch('zipfile.ZipFile')
        mock_zipfile_class.return_value.__enter__.return_value = mock_zip
        mocker.patch('zipfile.is_zipfile', return_value=True)
        mocker.patch.object(shell, '_ask_for_password', return_value='mypassword')

        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['encrypted.zip'])

        assert result is None
        mock_print.assert_called_once_with("Successfully extracted 1 files from 'encrypted.zip'")
        mock_zip.setpassword.assert_called_once_with(b'mypassword')
        shell.handle_error.assert_not_called()

    def test_unzip_encrypted_file_cancelled(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isfile', return_value=True)

        mock_zip = Mock()
        mock_fileinfo = Mock()
        mock_fileinfo.flag_bits = 1
        mock_zip.filelist = [mock_fileinfo]

        mock_zipfile_class = mocker.patch('zipfile.ZipFile')
        mock_zipfile_class.return_value.__enter__.return_value = mock_zip
        mocker.patch('zipfile.is_zipfile', return_value=True)

        mocker.patch.object(shell, '_ask_for_password', return_value=None)

        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['encrypted.zip'])
        assert result is None
        mock_print.assert_called_once_with("Operation cancelled.")
        shell.handle_error.assert_not_called()

    def test_unzip_wrong_password(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isfile', return_value=True)

        mock_zip = Mock()
        mock_fileinfo = Mock()
        mock_fileinfo.flag_bits = 1
        mock_zip.filelist = [mock_fileinfo]
        mock_zip.extractall = Mock(side_effect=RuntimeError("Bad password"))
        mock_zip.setpassword = Mock()

        mock_zipfile_class = mocker.patch('zipfile.ZipFile')
        mock_zipfile_class.return_value.__enter__.return_value = mock_zip
        mocker.patch('zipfile.is_zipfile', return_value=True)

        mocker.patch.object(shell, '_ask_for_password', return_value='wrongpass')

        result = execute(shell, ['encrypted.zip'])
        assert result is None
        shell.handle_error.assert_called_once_with("unzip: 'encrypted.zip': Incorrect password")

    def test_unzip_file(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isfile', return_value=True)

        mock_zip = Mock()
        mock_fileinfo = Mock()
        mock_fileinfo.flag_bits = 0
        mock_zip.filelist = [mock_fileinfo, mock_fileinfo, mock_fileinfo]
        mock_zip.extractall = Mock()

        mock_zipfile_class = mocker.patch('zipfile.ZipFile')
        mock_zipfile_class.return_value.__enter__.return_value = mock_zip
        mocker.patch('zipfile.is_zipfile', return_value=True)
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['archive.zip'])

        assert result is None
        mock_print.assert_called_once_with("Successfully extracted 3 files from 'archive.zip'")
        shell.handle_error.assert_not_called()

    def test_unzip_nonexistent_file(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=False)

        result = execute(shell, ['nonexistent.zip'])
        assert result is None
        shell.handle_error.assert_called_once_with("unzip: cannot access 'nonexistent.zip': No such file or directory")

    def test_unzip_directory_instead_of_file(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isfile', return_value=False)

        result = execute(shell, ['somedir'])
        assert result is None
        shell.handle_error.assert_called_once_with("unzip: 'somedir': Not a file")

    def test_unzip_not_zip_file(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isfile', return_value=True)
        mocker.patch('zipfile.is_zipfile', return_value=False)

        result = execute(shell, ['document.pdf'])
        assert result is None
        shell.handle_error.assert_called_once_with("unzip: 'document.pdf': Not a zip archive")

    def test_unzip_bad_zip_file(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isfile', return_value=True)
        mocker.patch('zipfile.is_zipfile', return_value=True)
        mock_zipfile = mocker.patch('zipfile.ZipFile', side_effect=zipfile.BadZipFile("Bad zip file"))

        result = execute(shell, ['corrupted.zip'])
        assert result is None
        shell.handle_error.assert_called_once_with("unzip: 'corrupted.zip': Bad zip file")

    def test_unzip_permission_error(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isfile', return_value=True)
        mocker.patch('zipfile.is_zipfile', return_value=True)
        mock_zipfile = mocker.patch('zipfile.ZipFile', side_effect=PermissionError("Permission denied"))

        result = execute(shell, ['archive.zip'])
        assert result is None
        shell.handle_error.assert_called_once_with("unzip: cannot extract 'archive.zip': Permission denied")

    def test_unzip_empty_archive(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isfile', return_value=True)

        mock_zip = Mock()
        mock_zip.filelist = []
        mock_zip.extractall = Mock()

        mock_zipfile_class = mocker.patch('zipfile.ZipFile')
        mock_zipfile_class.return_value.__enter__.return_value = mock_zip
        mocker.patch('zipfile.is_zipfile', return_value=True)
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['empty.zip'])
        assert result is None
        mock_print.assert_called_once_with("Successfully extracted 0 files from 'empty.zip'")
        shell.handle_error.assert_not_called()