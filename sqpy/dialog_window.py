import curses


class DialogWindow:
    """Base class for dialog windows in curses."""

    def __init__(
        self, stdscr: curses.window, height: int, width: int, start_y: int, start_x: int
    ) -> None:
        """Initialize a new dialog window.

        Args:
            stdscr (curses.window): The curses window object.
            height (int): The height of the window.
            width (int): The width of the window.
            start_y (int): The starting y-coordinate of the window.
            start_x (int): The starting x-coordinate of the window.
        """
        self.stdscr = stdscr
        self.height = height
        self.width = width
        self.start_y = start_y
        self.start_x = start_x
        self.win = curses.newwin(height, width, start_y, start_x)
        self.win.box()

    def add_content(self) -> None:
        """Add content to the window. This method should be overridden."""
        raise NotImplementedError(
            "Method 'add_content' must be implemented in a subclass."
        )

    def show(self) -> None:
        """Display the window and wait for user input."""
        self.add_content()
        self.win.refresh()
        self.win.getch()
        del self.win
