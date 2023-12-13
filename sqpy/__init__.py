from .sqpy import Sqpy
import curses


def entrypoint() -> None:
    viewer = Sqpy()
    curses.wrapper(viewer.run)
