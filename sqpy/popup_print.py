import curses

from .dialog_window import DialogWindow


class PopupPrint(DialogWindow):
    """Class for displaying simple popup messages."""

    def __init__(self, stdscr: curses.window, message: str) -> None:
        """Initialize a popup print window with a message.

        Args:
            stdscr (curses.window): The curses window object.
            message (str): The message to be displayed in the popup window.
        """
        height, width = stdscr.getmaxyx()
        msg_width = min(60, width - 4)
        msg_height = 5
        start_y = (height - msg_height) // 2
        start_x = (width - msg_width) // 2
        super().__init__(stdscr, msg_height, msg_width, start_y, start_x)
        self.message = message

    def add_content(self) -> None:
        """Display the message in the window."""
        self.win.addstr(2, 2, self.message[: self.width - 4])
