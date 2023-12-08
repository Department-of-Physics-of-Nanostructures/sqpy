import curses
import subprocess
import re


class DialogWindow:
    """Base class for dialog windows in curses."""

    def __init__(self, stdscr, height, width, start_y, start_x):
        """Initialize a new dialog window."""
        self.stdscr = stdscr
        self.height = height
        self.width = width
        self.start_y = start_y
        self.start_x = start_x
        self.win = curses.newwin(height, width, start_y, start_x)
        self.win.box()

    def add_content(self):
        """Add content to the window. This method should be overridden."""
        raise NotImplementedError(
            "Method 'add_content' must be implemented in a subclass."
        )

    def show(self):
        """Display the window and wait for user input."""
        self.add_content()
        self.win.refresh()
        self.win.getch()  # Oczekiwanie na dowolny klawisz
        del self.win  # Usunięcie okna


class PopupPrint(DialogWindow):
    """Class for displaying simple popup messages."""

    def __init__(self, stdscr, message):
        """Initialize a popup print window with a message."""
        height, width = stdscr.getmaxyx()
        msg_width = min(60, width - 4)
        msg_height = 5
        start_y = (height - msg_height) // 2
        start_x = (width - msg_width) // 2
        super().__init__(stdscr, msg_height, msg_width, start_y, start_x)
        self.message = message

    def add_content(self):
        """Display the message in the window."""
        self.win.addstr(2, 2, self.message[: self.width - 4])


class ScancelDialog(DialogWindow):
    """Class for displaying a confirmation dialog to cancel a job."""

    def __init__(self, stdscr, jobid, jobname):
        """Initialize a scancel dialog window."""
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
        self.selected_option = 0  # Indeks wybranej opcji

    def add_content(self):
        """Add confirmation question to the window."""
        question = f"Are you sure to cancel {self.jobid} - {self.jobname}?"
        self.win.addstr(2, 2, question[: self.width - 4])  # Dodajemy pytanie do okna
        self._draw_options()

    def _draw_options(self):
        """Draw options inside the window."""
        y, x = 3, 2
        for i, option in enumerate(self.options):
            mode = curses.A_REVERSE if i == self.selected_option else 0
            self.win.addstr(y, x, option, mode)
            x += len(option) + 2

    def navigate(self, direction):
        """Navigate through options."""
        if direction == "left" and self.selected_option > 0:
            self.selected_option -= 1
        elif direction == "right" and self.selected_option < len(self.options) - 1:
            self.selected_option += 1
        self._draw_options()

    def execute_scancel(self):
        """Execute the scancel command for the selected job."""
        PopupPrint(self.stdscr, "Job canceled").show()
        try:
            subprocess.run(["scancel", self.jobid], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error cancelling job {self.jobid}: {e}")
            return False

    def show(self):
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
                return self.selected_option == 0

            self.win.box()
            self.win.refresh()


class SlurmViewer:
    def __init__(self):
        self.data = []
        self.top_row = 0

    def fetch_data(self):
        command = [
            "squeue",
            "-o",
            "%.18i %.9P %.20j %.12u %.8T %.10M %.9l %.6D %R",
            "--me",
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE)
        output = result.stdout.decode("utf-8")
        lines = output.strip().split("\n")
        headers = re.split(r"\s+", lines[0].strip())

        parsed_data = []
        for line in lines[1:]:
            values = re.split(r"\s+", line.strip())
            if len(values) == len(headers):
                row_data = dict(zip(headers, values))
                parsed_data.append(row_data)

        self.data = parsed_data

    def draw_instructions_bar(self, stdscr):
        instructions = "Ctrl+K: Kill Job  |  Ctrl+R: Refresh |  Q: Quit"
        height, width = stdscr.getmaxyx()
        stdscr.addstr(height - 1, 0, instructions[:width], curses.A_REVERSE)

    def calculate_column_widths(self):
        column_widths = {}
        headers = self.data[0].keys()
        for header in headers:
            max_width = max(len(header), max(len(row[header]) for row in self.data))
            column_widths[header] = max_width
        return column_widths

    def calculate_column_widths(self, headers, total_width):
        min_widths = {
            header: max(len(header), max(len(str(row[header])) for row in self.data))
            for header in headers
        }
        used_space = sum(min_widths.values())
        extra_space = max(
            0, total_width - used_space - len(headers) - 1
        )  # Dodatkowe miejsce na spacje między kolumnami
        total_min_width = sum(min_widths.values())
        for header in headers:
            proportion = min_widths[header] / total_min_width
            min_widths[header] += int(extra_space * proportion)

        return min_widths

    def draw_table(self, stdscr, current_row):
        if not self.data:
            return

        height, width = stdscr.getmaxyx()
        headers = self.data[0].keys()

        column_widths = self.calculate_column_widths(headers, width)

        x_pos = 0

        for header in headers:
            stdscr.addstr(0, x_pos, header.ljust(column_widths[header]))
            x_pos += column_widths[header] + 1

        for i, row in enumerate(self.data[self.top_row : self.top_row + height - 2]):
            x_pos = 0
            row_text = "".join(
                row[header].ljust(column_widths[header]) for header in headers
            )
            if i + self.top_row == current_row:
                stdscr.addstr(i + 1, 0, row_text[: width - 1], curses.color_pair(3))
            else:
                stdscr.addstr(i + 1, 0, row_text[: width - 1])

    def show_message(self, stdscr, message):
        height, width = stdscr.getmaxyx()
        msg_width = min(60, width - 4)
        msg_height = 5
        start_y = (height - msg_height) // 2
        start_x = (width - msg_width) // 2

        win = curses.newwin(msg_height, msg_width, start_y, start_x)
        win.box()

        win.addstr(2, 2, message[: msg_width - 4])
        win.refresh()
        win.getch()

        del win

    def run(self, stdscr):
        curses.start_color()
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(3, 1, 0)

        current_row = 0
        curses.curs_set(0)  # Hide cursor

        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()

            self.fetch_data()
            self.draw_table(stdscr, current_row)
            self.draw_instructions_bar(stdscr)

            stdscr.refresh()

            key = stdscr.getch()

            if key == curses.KEY_UP and current_row > 0:
                current_row -= 1
                if current_row < self.top_row:
                    self.top_row = max(0, self.top_row - 1)
            elif key == curses.KEY_DOWN and current_row < len(self.data) - 1:
                current_row += 1
                if current_row >= self.top_row + height - 2:
                    self.top_row = min(len(self.data) - (height - 2), self.top_row + 1)
            elif key == ord("q"):
                break

            elif key == 12:
                if self.data:
                    jobid = self.data[current_row].get("JOBID", None)
                    jobname = self.data[current_row].get("NAME", None)
                    if jobid:
                        PopupPrint(stdscr, "Ctrl+L Detected").show()

            elif key == 11:  #  Ctrl+K
                if self.data:
                    jobid = self.data[current_row].get("JOBID", None)
                    jobname = self.data[current_row].get("NAME", None)
                    if jobid:
                        confirm_dialog = ScancelDialog(stdscr, jobid, jobname)
                        confirm_dialog.add_content()
                        confirmed = confirm_dialog.show()


if __name__ == "__main__":
    viewer = SlurmViewer()
    curses.wrapper(viewer.run)
