import pytest
from unittest.mock import patch, MagicMock

from sympy import im
from sqpy.scancel_dialog import ScancelDialog
import subprocess


class MockCursesWindow:
    def __init__(self, h, w, y, x):
        self.h = h
        self.w = w
        self.y = y
        self.x = x
        self.addstr = MagicMock()  # Making addstr a mock method

    def box(self):
        pass

    def refresh(self):
        pass

    def getch(self):
        return 0

    def addstr(self, y, x, string):
        pass

    def getmaxyx(self):
        return 24, 80  # Mocking a standard terminal size


@pytest.fixture
def mock_stdscr():
    mock = MagicMock(spec=MockCursesWindow)
    mock.getmaxyx.return_value = (24, 80)
    return mock


@patch("sqpy.scancel_dialog.PopupPrint")
@patch("curses.newwin", return_value=MockCursesWindow(24, 80, 0, 0))
def test_scancel_dialog_init(mock_newwin, mock_popupprint, mock_stdscr):
    jobid = "123"
    jobname = "TestJob"
    dialog = ScancelDialog(mock_stdscr, jobid, jobname)

    # Assert job details are set correctly
    assert dialog.jobid == jobid
    assert dialog.jobname == jobname

    # Assert the window dimensions and position are calculated correctly
    assert dialog.height == 5
    assert dialog.width <= 60
    assert dialog.start_y == (24 - 5) // 2
    assert dialog.start_x >= (80 - 60) // 2

    # Assert that options are set correctly
    assert dialog.options == ["Yes", "No"]


@patch("curses.initscr", return_value=MagicMock())
@patch("curses.newwin", return_value=MockCursesWindow(24, 80, 0, 0))
@patch("sqpy.scancel_dialog.PopupPrint")
@patch("sqpy.scancel_dialog.subprocess.run")
def test_execute_scancel(
    mock_run, mock_popupprint, mock_newwin, mock_initscr, mock_stdscr
):
    jobid = "123"
    jobname = "TestJob"
    dialog = ScancelDialog(mock_stdscr, jobid, jobname)

    # Mock subprocess to simulate successful command execution
    mock_run.return_value = True
    assert dialog.execute_scancel() == True
    mock_run.assert_called_with(["scancel", jobid], check=True)

    # Mock subprocess to simulate failed command execution
    mock_run.side_effect = subprocess.CalledProcessError(1, ["scancel", jobid])
    assert dialog.execute_scancel() == False
