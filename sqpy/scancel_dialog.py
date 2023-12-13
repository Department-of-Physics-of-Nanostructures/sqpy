import curses
import subprocess

from .dialog_window import DialogWindow
from .popup_print import PopupPrint


class ScancelDialog(DialogWindow):
    """Class for displaying a confirmation dialog to cancel a job."""

    def __init__(self, stdscr: curses.window, jobid: str, jobname: str) -> None:
        """Initialize a scancel dialog window.

        Args:
            stdscr (curses.window): The curses window object.
            jobid (str): The ID of the job to be canceled.
            jobname (str): The name of the job to be canceled.
        """
        self.stdscr = stdscr
        height, width = self.stdscr.getmaxyx()
        msg_width = min(60, width - 4)
        msg_height = 5
        start_y = (height - msg_height) // 2
        start_x = (width - msg_width) // 2

        super().__init__(self.stdscr, msg_height, msg_width, start_y, start_x)
        self.jobid = jobid
        self.jobname = jobname

        self.options = ["Yes", "No"]
        self.selected_option = 0

    def add_content(self) -> None:
        """Add confirmation question to the window."""
        question = f"Are you sure to cancel {self.jobid} - {self.jobname}?"
        self.win.addstr(2, 2, question[: self.width - 4])
        self._draw_options()

    def _draw_options(self) -> None:
        """Draw options inside the window."""
        y, x = 3, 2
        for i, option in enumerate(self.options):
            mode = curses.A_REVERSE if i == self.selected_option else 0
            self.win.addstr(y, x, option, mode)
            x += len(option) + 2

    def navigate(self, direction: str) -> None:
        """Navigate through options.

        Args:
            direction (str): The direction of navigation ('left' or 'right').
        """
        if direction == "left" and self.selected_option > 0:
            self.selected_option -= 1
        elif direction == "right" and self.selected_option < len(self.options) - 1:
            self.selected_option += 1
        self._draw_options()

    def execute_scancel(self) -> bool:
        """Execute the scancel command for the selected job."""
        PopupPrint(self.stdscr, "Job canceled").show()
        try:
            subprocess.run(["scancel", self.jobid], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error cancelling job {self.jobid}: {e}")
            return False

    def show(self) -> None:
        """Show the dialog and handle user input."""
        self.win.keypad(True)
        self.add_content()
        while True:
            key = self.win.getch()

            if key == curses.KEY_LEFT:
                self.navigate("left")
                self.win.clear()
                self.add_content()
            elif key == curses.KEY_RIGHT:
                self.navigate("right")
                self.win.clear()
                self.add_content()
            elif key in [
                10,
                13,
                curses.KEY_ENTER,
            ]:  # Enter (some systems use 10 or 13 for Enter)
                if self.selected_option == 0:  # If "Yes" is selected
                    self.execute_scancel()
                # return self.selected_option == 0

            self.win.box()
            self.win.refresh()
