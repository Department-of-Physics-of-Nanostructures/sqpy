import unittest
from unittest.mock import patch, MagicMock
import curses
from sqpy import SlurmViewer


class TestSlurmViewer(unittest.TestCase):
    def setUp(self):
        self.viewer = SlurmViewer()

    @patch('subprocess.run')
    def test_fetch_data(self, mock_run):
        mock_run.return_value.stdout.decode.return_value = (
            "JOBID NAME\n123 job1\n456 job2"
        )
        self.viewer.fetch_data()
        self.assertEqual(len(self.viewer.data), 2)
        self.assertEqual(self.viewer.data[0]['JOBID'], '123')
        self.assertEqual(self.viewer.data[0]['NAME'], 'job1')
        self.assertEqual(self.viewer.data[1]['JOBID'], '456')
        self.assertEqual(self.viewer.data[1]['NAME'], 'job2')

    def test_calculate_column_widths(self):
        headers = ['JOBID', 'NAME']
        total_width = 20
        self.viewer.data = [{'JOBID': '123', 'NAME': 'job1'},
                            {'JOBID': '456', 'NAME': 'job2'}]
        column_widths = self.viewer.calculate_column_widths(
            headers, total_width
        )
        self.assertEqual(column_widths['JOBID'], 10)
        self.assertEqual(column_widths['NAME'], 10)

    @patch('curses.newwin')
    @patch('curses.init_pair')
    @patch('curses.curs_set')
    def test_run(self, mock_curs_set, mock_init_pair, mock_newwin):
        stdscr = MagicMock()
        stdscr.getmaxyx.return_value = (10, 20)
        stdscr.getch.side_effect = [curses.KEY_DOWN, ord('q')]
        self.viewer.fetch_data = MagicMock()
        self.viewer.draw_table = MagicMock()
        self.viewer.draw_instructions_bar = MagicMock()

        self.viewer.run(stdscr)

        self.assertEqual(self.viewer.fetch_data.call_count, 2)
        self.assertEqual(self.viewer.draw_table.call_count, 2)
        self.assertEqual(self.viewer.draw_instructions_bar.call_count, 2)
        self.assertEqual(stdscr.refresh.call_count, 2)
        self.assertEqual(stdscr.getch.call_count, 2)
        self.assertEqual(mock_curs_set.call_count, 1)
        self.assertEqual(mock_init_pair.call_count, curses.COLORS)


if __name__ == '__main__':
    unittest.main()