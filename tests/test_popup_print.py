from typing import Tuple
import pytest
from unittest.mock import patch, MagicMock
from sqpy.popup_print import PopupPrint


class MockCursesWindow:
    def __init__(self, h: int, w: int, y: int, x: int):
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

    def addstr(self, y: int, x: int, string: str):
        pass

    def getmaxyx(self) -> Tuple[int, int]:
        return 24, 80  # Mocking a standard terminal size


@pytest.fixture
def mock_stdscr() -> MockCursesWindow:
    mock: MockCursesWindow = MagicMock(spec=MockCursesWindow)
    mock.getmaxyx.return_value = (24, 80)  # type: ignore
    return mock


@patch("curses.newwin", return_value=MockCursesWindow(24, 80, 0, 0))
def test_popup_print_init(mock_newwin: MagicMock, mock_stdscr: MagicMock):
    message = "Test Message"
    popup = PopupPrint(mock_stdscr, message)

    # Assert the message is set correctly
    assert popup.message == message

    # Assert the window dimensions and position are calculated correctly
    assert popup.height == 5
    assert popup.width == 60
    assert popup.start_y == (24 - 5) // 2
    assert popup.start_x == (80 - 60) // 2

    # Assert that a new window is created with the calculated dimensions and position
    mock_newwin.assert_called_with(5, 60, (24 - 5) // 2, (80 - 60) // 2)


# @patch("curses.newwin", return_value=MockCursesWindow(24, 80, 0, 0))
# def test_popup_print_add_content(mock_newwin: MagicMock, mock_stdscr: MagicMock):
#     message = "Test Message"
#     popup = PopupPrint(mock_stdscr, message)
#     popup.add_content()

#     # Assert that the message is added to the window at the correct position
#     # Note: This is a simplification as the actual curses addstr behavior is not tested
#     assert popup.win.addstr.call_args == ((2, 2, message[: popup.width - 4]),)
