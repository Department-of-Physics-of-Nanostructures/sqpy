# import subprocess
import curses
from typing import Tuple
from unittest.mock import MagicMock, patch

# import pytest
from sqpy.sqpy import Sqpy  # Replace with actual import


def test_check_squeue_installed():
    viewer = Sqpy()

    # Test when squeue is installed
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock()
        assert viewer.check_squeue_installed() is True

    # Test when squeue is not installed
    with patch("subprocess.run", side_effect=FileNotFoundError):
        assert viewer.check_squeue_installed() is False


def test_fetch_data():
    viewer = Sqpy()

    # Mock output of squeue command
    mock_output = (
        "JOBID PARTITION                 NAME         USER    STATE       TIME TIME_LIMI  NODES NODELIST(REASON)\n"
        "30063163      fast calc_varying_amplitu     mathieum  PENDING       0:00   1:00:00      1 (Dependency)\n"
        "30063164     tesla varying_amplitude2/0     mathieum  PENDING       0:00 3-03:00:00      1 (Priority)\n"
    )

    # Mock subprocess.run to return the above output
    mock_result = MagicMock()
    mock_result.stdout = mock_output.encode("utf-8")

    with patch("subprocess.run", return_value=mock_result):
        viewer.fetch_data()

    expected_data = [
        {
            "JOBID": "30063163",
            "PARTITION": "fast",
            "NAME": "calc_varying_amplitu",
            "USER": "mathieum",
            "STATE": "PENDING",
            "TIME": "0:00",
            "TIME_LIMI": "1:00:00",
            "NODES": "1",
            "NODELIST(REASON)": "(Dependency)",
        },
        {
            "JOBID": "30063164",
            "PARTITION": "tesla",
            "NAME": "varying_amplitude2/0",
            "USER": "mathieum",
            "STATE": "PENDING",
            "TIME": "0:00",
            "TIME_LIMI": "3-03:00:00",
            "NODES": "1",
            "NODELIST(REASON)": "(Priority)",
        },
    ]

    # Assert that fetch_data correctly parses the mock output
    assert viewer.data == expected_data


class MockCursesWindow:
    """
    Mock class for a curses window.
    """

    def getmaxyx(self) -> Tuple[int, int]:
        """
        Mock implementation of getmaxyx, returning a tuple of two integers.
        """
        return 24, 80  # Example terminal size

    def addstr(self, y: int, x: int, string: str, attribute: int = 0) -> None:
        """
        Mock implementation of addstr.
        """
        pass


def test_draw_instructions_bar():
    viewer = Sqpy()

    # Use the mock curses window
    mock_window = MockCursesWindow()

    # Convert the mock window to a MagicMock to enable method call tracking
    mock_window = MagicMock(wraps=mock_window)

    # Call the draw_instructions_bar method
    viewer.draw_instructions_bar(mock_window)

    # Define the expected call to the addstr method
    expected_call = (
        23,  # Y position (height - 1)
        0,  # X position
        "Ctrl+K: Kill Job  |  Ctrl+R: Refresh |  Q: Quit"[:80],  # Instructions text
        curses.A_REVERSE,  # Attribute
    )

    # Assert that addstr was called with the expected parameters
    mock_window.addstr.assert_called_with(*expected_call)  # type: ignore


def test_calculate_column_widths():
    viewer = Sqpy()

    # Populate the viewer's data with test data
    viewer.data = [
        {"JOBID": "12345", "USER": "alice", "STATE": "RUNNING"},
        {"JOBID": "67890", "USER": "bob", "STATE": "PENDING"},
        {"JOBID": "54321", "USER": "charlie", "STATE": "COMPLETED"},
    ]

    # Define test cases and expected results
    test_cases = [
        (["JOBID", "USER", "STATE"], 30, {"JOBID": 6, "USER": 8, "STATE": 11}),
        (["JOBID", "STATE"], 20, {"JOBID": 6, "STATE": 10}),
        (["USER"], 10, {"USER": 8}),
    ]

    # Run test cases
    for headers, total_width, expected in test_cases:
        assert viewer.calculate_column_widths(headers, total_width) == expected
