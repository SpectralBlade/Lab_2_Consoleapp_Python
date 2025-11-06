import pytest
import sys
import os
from unittest.mock import Mock

from Lab_2_Consoleapp_Python.src.ruletka_shell import RuletkaShell

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))


@pytest.fixture
def mock_commands():
    mock_commands = {}
    command_names = ['cd', 'ls', 'cat', 'cp', 'mv', 'rm', 'zip', 'unzip', 'tar', 'untar', 'grep', 'history', 'undo']

    for cmd in command_names:
        mock_commands[cmd] = Mock(return_value=None)

    return mock_commands

@pytest.fixture
def mock_logging_config():
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "test_shell.log",
                "level": "DEBUG",
            },
        },
        "loggers": {
            "RuletkaShell": {
                "handlers": ["file"],
                "level": "DEBUG",
            }
        },
    }


@pytest.fixture
def shell_instance(mocker, mock_commands):
    for cmd_name, mock_cmd in mock_commands.items():
        mocker.patch(f'ruletka_shell.{cmd_name}', mock_cmd)

    mocker.patch('ruletka_shell.logging.config.dictConfig')
    mocker.patch('ruletka_shell.logging.getLogger')

    mocker.patch('ruletka_shell.os.path.exists', return_value=True)
    mocker.patch('ruletka_shell.os.makedirs')


    shell = RuletkaShell()

    shell.commands = mock_commands
    shell.logger = Mock()
    shell.command_history = []

    return shell