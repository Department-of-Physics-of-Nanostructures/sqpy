import pytest
from unittest.mock import patch
from sqpy.dialog_window import DialogWindow
from unittest.mock import MagicMock


class MockCursesWindow:
    def __init__(self):
        pass

    def box(self):
        pass

    def refresh(self):
        pass

    def getch(self):
        return 0


@pytest.fixture
def mock_stdscr():
    return MockCursesWindow()


@pytest.fixture
def mock_newwin():
    with patch("curses.newwin", return_value=MockCursesWindow()) as mock:
        yield mock


@patch("curses.newwin", return_value=MockCursesWindow())
def test_dialog_window_init(mock_newwin: MagicMock, mock_stdscr: MagicMock):
    height, width, start_y, start_x = 10, 20, 5, 5
    window = DialogWindow(mock_stdscr, height, width, start_y, start_x)
    mock_newwin.assert_called_with(height, width, start_y, start_x)
    assert window.height == height
    assert window.width == width
    assert window.start_y == start_y
    assert window.start_x == start_x


@patch("curses.newwin", return_value=MockCursesWindow())
def test_dialog_window_add_content_not_implemented(
    mock_newwin: MagicMock, mock_stdscr: MagicMock
):
    window = DialogWindow(mock_stdscr, 10, 20, 5, 5)
    with pytest.raises(NotImplementedError):
        window.add_content()


def test_dialog_window_show(mock_stdscr: MagicMock, mock_newwin: MagicMock):
    with patch.object(DialogWindow, "add_content") as mock_add_content, patch.object(
        MockCursesWindow, "refresh"
    ) as mock_refresh, patch.object(
        MockCursesWindow, "getch", return_value=ord("q")
    ) as mock_getch:
        window = DialogWindow(mock_stdscr, 10, 20, 5, 5)
        window.show()

        mock_add_content.assert_called_once()
        mock_refresh.assert_called_once()
        mock_getch.assert_called_once()
