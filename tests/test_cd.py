from unittest.mock import Mock
from commands.cd import execute

class TestCdCommand:
    def test_cd_home_directory(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.is_windows_drive.return_value = False
        shell.resolve_path.side_effect = lambda x: x
        shell.resolve_user_path.side_effect = lambda x: x  # Добавлен мок для resolve_user_path
        shell.logger = Mock()

        mocker.patch('os.path.expanduser', return_value='/home/user')
        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)
        mocker.patch('os.path.normpath', side_effect=lambda x: x)

        execute(shell, [])
        assert shell.current_dir == '/home/user'

    def test_cd_relative_path(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.is_windows_drive.return_value = False
        shell.resolve_path.side_effect = lambda x: x
        shell.resolve_user_path.return_value = '/home/user/documents'  # Явно возвращаем путь
        shell.logger = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)
        mocker.patch('os.path.normpath', side_effect=lambda x: x)

        execute(shell, ['documents'])
        assert shell.current_dir == '/home/user/documents'

    def test_cd_absolute_path(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.is_windows_drive.return_value = False
        shell.resolve_path.side_effect = lambda x: x
        shell.resolve_user_path.return_value = '/etc'  # Явно возвращаем путь
        shell.logger = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)
        mocker.patch('os.path.normpath', side_effect=lambda x: x)

        execute(shell, ['/etc'])
        assert shell.current_dir == '/etc'

    def test_cd_parent_directory(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user/documents'
        shell.is_windows_drive.return_value = False
        shell.resolve_path.side_effect = lambda x: x
        shell.resolve_user_path.side_effect = lambda x: x  # Для '..' возвращаем как есть
        shell.logger = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)
        mocker.patch('os.path.normpath', side_effect=lambda x: x)
        mocker.patch('os.path.dirname', return_value='/home/user')

        execute(shell, ['..'])
        assert shell.current_dir == '/home/user'

    def test_cd_tilde_home(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.is_windows_drive.return_value = False
        shell.resolve_path.side_effect = lambda x: x
        shell.resolve_user_path.side_effect = lambda x: x  # Для '~' возвращаем как есть
        shell.logger = Mock()

        mocker.patch('os.path.expanduser', return_value='/home/user')
        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)
        mocker.patch('os.path.normpath', side_effect=lambda x: x)

        execute(shell, ['~'])
        assert shell.current_dir == '/home/user'

    def test_cd_nonexistent_directory(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.is_windows_drive.return_value = False
        shell.resolve_path.side_effect = lambda x: x
        shell.resolve_user_path.return_value = '/home/user/nonexistent'  # Возвращаем путь
        shell.logger = Mock()
        shell.handle_error = Mock()  # Добавляем мок для handle_error

        mocker.patch('os.path.exists', return_value=False)
        mocker.patch('os.path.normpath', side_effect=lambda x: x)

        execute(shell, ['nonexistent'])
        assert shell.current_dir == '/home/user'
        shell.handle_error.assert_called_once()

    def test_cd_file_instead_of_directory(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.is_windows_drive.return_value = False
        shell.resolve_path.side_effect = lambda x: x
        shell.resolve_user_path.return_value = '/home/user/file.txt'  # Возвращаем путь к файлу
        shell.logger = Mock()
        shell.handle_error = Mock()  # Добавляем мок для handle_error

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=False)
        mocker.patch('os.path.normpath', side_effect=lambda x: x)

        execute(shell, ['file.txt'])
        assert shell.current_dir == '/home/user'
        shell.handle_error.assert_called_once()

    def test_cd_windows_drive(self, mocker):
        shell = Mock()
        shell.current_dir = r'C:\\Users\\user'
        shell.is_windows_drive.return_value = True
        shell.resolve_path.return_value = r'D:\\'
        shell.resolve_user_path.return_value = r'D:\\'  # Возвращаем путь к диску
        shell.logger = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)

        execute(shell, ['D:'])
        assert shell.current_dir == r'D:\\'

    def test_cd_with_spaces_in_path(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.is_windows_drive.return_value = False
        shell.resolve_path.side_effect = lambda x: x
        shell.resolve_user_path.return_value = '/home/user/my documents'  # Возвращаем путь с пробелами
        shell.logger = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)
        mocker.patch('os.path.normpath', side_effect=lambda x: x)

        execute(shell, ['my documents'])
        assert shell.current_dir == '/home/user/my documents'