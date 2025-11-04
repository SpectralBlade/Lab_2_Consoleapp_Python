from unittest.mock import Mock
from commands.rm import execute, _is_protected_path, _confirm_deletion

class TestRmCommand:
    def test_rm_file(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(return_value='/home/user/file.txt')
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()
        shell.trash_dir = '/home/user/.trash'

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=False)
        mocker.patch('commands.rm._is_protected_path', return_value=False)
        mocker.patch('shutil.move')
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['file.txt'])

        assert result is not None
        shell.handle_error.assert_not_called()

    def test_rm_directory_with_r_flag(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(return_value='/home/user/directory')
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()
        shell.trash_dir = '/home/user/.trash'

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)
        mocker.patch('commands.rm._is_protected_path', return_value=False)
        mocker.patch('commands.rm._confirm_deletion', return_value=True)
        mocker.patch('shutil.move')
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['-r', 'directory'])

        assert result is not None
        shell.handle_error.assert_not_called()

    def test_rm_directory_without_r_flag(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(return_value='/home/user/directory')
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)
        mocker.patch('commands.rm._is_protected_path', return_value=False)

        result = execute(shell, ['directory'])

        assert result is None
        shell.handle_error.assert_called_once()

    def test_rm_directory_confirmation_cancelled(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(side_effect=lambda x: x)
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=True)
        mocker.patch('commands.rm._is_protected_path', return_value=False)
        mocker.patch('commands.rm._confirm_deletion', return_value=False)

        result = execute(shell, ['-r', 'directory'])
        assert result is None

    def test_rm_nonexistent_file(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(return_value='/home/user/nonexistent.txt')
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=False)
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['nonexistent.txt'])

        assert result is None
        shell.handle_error.assert_called_once()
        error_msg = shell.handle_error.call_args[0][0]
        assert "cannot remove" in error_msg
        assert "No such file or directory" in error_msg

    def test_rm_protected_path_parent(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(return_value='..')
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('commands.rm._is_protected_path', return_value=True)
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['..'])

        assert result is None
        shell.handle_error.assert_called_once()
        error_msg = shell.handle_error.call_args[0][0]
        assert "cannot remove" in error_msg
        assert "Operation not permitted" in error_msg

    def test_rm_protected_path_root(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(return_value='/')
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('commands.rm._is_protected_path', return_value=True)
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['/'])

        assert result is None
        shell.handle_error.assert_called_once()
        error_msg = shell.handle_error.call_args[0][0]
        assert "cannot remove" in error_msg
        assert "Operation not permitted" in error_msg

    def test_rm_permission_error(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(return_value='/home/user/protected.txt')
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()
        shell.trash_dir = '/home/user/.trash'

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=False)
        mocker.patch('commands.rm._is_protected_path', return_value=False)
        mocker.patch('shutil.move', side_effect=PermissionError("Permission denied"))
        mock_print = mocker.patch('builtins.print')

        result = execute(shell, ['protected.txt'])

        assert result is None
        shell.handle_error.assert_called_once()
        error_msg = shell.handle_error.call_args[0][0]
        assert "cannot remove" in error_msg
        assert "Permission denied" in error_msg

    def test_rm_os_error(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(return_value='/home/user/file.txt')
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()
        shell.trash_dir = '/home/user/.trash'

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=False)
        mocker.patch('commands.rm._is_protected_path', return_value=False)
        mocker.patch('shutil.move', side_effect=OSError("Disk error"))

        result = execute(shell, ['file.txt'])

        assert result is None
        shell.handle_error.assert_called_once()
        error_msg = shell.handle_error.call_args[0][0]
        assert "cannot remove" in error_msg
        assert "Disk error" in error_msg

    def test_rm_relative_path(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(return_value='/home/user/docs/file.txt')
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()
        shell.trash_dir = '/home/user/.trash'

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=False)
        mocker.patch('commands.rm._is_protected_path', return_value=False)
        mocker.patch('shutil.move')

        result = execute(shell, ['docs/file.txt'])

        assert result is not None
        shell.handle_error.assert_not_called()

    def test_rm_absolute_path(self, mocker):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.resolve_path = Mock(return_value='/etc/config.txt')
        shell.is_windows_drive = Mock(return_value=False)
        shell.handle_error = Mock()
        shell.trash_dir = '/home/user/.trash'

        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.isdir', return_value=False)
        mocker.patch('commands.rm._is_protected_path', return_value=False)
        mocker.patch('shutil.move')

        result = execute(shell, ['/etc/config.txt'])

        assert result is not None
        shell.handle_error.assert_not_called()

    def test_is_protected_path_parent(self):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.is_windows_drive = Mock(return_value=False)

        result = _is_protected_path(shell, '..')
        assert result == True

    def test_is_protected_path_current(self):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.is_windows_drive = Mock(return_value=False)

        result = _is_protected_path(shell, '.')
        assert result == True

    def test_is_protected_path_root(self):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.is_windows_drive = Mock(return_value=False)

        result = _is_protected_path(shell, '/')
        assert result == True

    def test_is_protected_path_windows_drive(self):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.is_windows_drive = Mock(return_value=True)

        result = _is_protected_path(shell, 'C:')
        assert result == True

    def test_is_protected_path_normal_file(self):
        shell = Mock()
        shell.current_dir = '/home/user'
        shell.is_windows_drive = Mock(return_value=False)

        result = _is_protected_path(shell, 'normal_file.txt')
        assert result == False

    def test_confirm_deletion_yes(self, mocker):
        mock_input = mocker.patch('builtins.input', return_value='y')
        result = _confirm_deletion('test_dir')
        assert result == True
        mock_input.assert_called_once_with("rm: remove directory 'test_dir'? (y/n): ")

    def test_confirm_deletion_no(self, mocker):
        mock_input = mocker.patch('builtins.input', return_value='n')
        result = _confirm_deletion('test_dir')
        assert result == False
        mock_input.assert_called_once_with("rm: remove directory 'test_dir'? (y/n): ")

    def test_confirm_deletion_yes_uppercase(self, mocker):
        mock_input = mocker.patch('builtins.input', return_value='Y')
        result = _confirm_deletion('test_dir')
        assert result == True
        mock_input.assert_called_once_with("rm: remove directory 'test_dir'? (y/n): ")

    def test_confirm_deletion_yes_full(self, mocker):
        mock_input = mocker.patch('builtins.input', return_value='yes')
        result = _confirm_deletion('test_dir')
        assert result == True
        mock_input.assert_called_once_with("rm: remove directory 'test_dir'? (y/n): ")