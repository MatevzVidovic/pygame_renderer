from __future__ import annotations

import numpy as np

from core.renderer import (
    CoordinatePlacing,
    Elipse,
    ObjectTree,
    RGB,
    Rect,
    Splat,
    VisualProgram,
    main as render_main,
)
from problem_driver import CatchingMiceProblem, GRID_DIM
from state import State


SCREEN_SIZE = (720, 720)
GRID_SIZE = 640
GRID_TOP = 40
GRID_LEFT = 40
CELL_SIZE = GRID_SIZE / GRID_DIM
GRID_LINE_THICKNESS = 2
ROBOT_ID = "robot"
MOUSE_ID = "mouse"


def sticky_stop(t: float | np.ndarray) -> float | np.ndarray:
    t = np.asarray(t)
    return t * t * (3 - 2 * t)


class CatchingMice(VisualProgram):
    def __init__(self, driver: CatchingMiceProblem) -> None:
        self.driver = driver
        self.state: State = driver.init()
        self.background = Rect(SCREEN_SIZE[0], RGB(21, 24, 31), SCREEN_SIZE[1], CoordinatePlacing.TOP_LEFT)
        self.grid_lines = self._make_grid_lines()
        self.robot = Elipse(CELL_SIZE * 0.68, RGB(242, 116, 87))
        self.mouse = Elipse(CELL_SIZE * 0.28, RGB(24, 16, 187))

    def step(self) -> None:
        # This blocks until solution.py submits its next task.  StopIteration is
        # understood by core.renderer as a clean request to end the loop.
        self.state = self.driver.step(self.state)

    def get_object_tree(self) -> ObjectTree:
        return [
            Splat(self.background, (0, 0)),
            self.grid_lines,
            Splat(self.robot, self._cell_center(self.state.robot_pos), ROBOT_ID, sticky_stop),
            Splat(self.mouse, self._cell_center(self.state.mouse_pos), MOUSE_ID, sticky_stop),
        ]

    def _cell_center(self, cell: np.ndarray) -> np.ndarray:
        row, col = cell
        return np.array(
            [
                GRID_TOP + row * CELL_SIZE + CELL_SIZE / 2,
                GRID_LEFT + col * CELL_SIZE + CELL_SIZE / 2,
            ]
        )

    def _make_grid_lines(self) -> list[Splat]:
        line_color = RGB(219, 225, 235)
        lines: list[Splat] = []
        for i in range(GRID_DIM + 1):
            offset = i * CELL_SIZE
            lines.append(
                Splat(
                    Rect(GRID_SIZE + GRID_LINE_THICKNESS, line_color, GRID_LINE_THICKNESS, CoordinatePlacing.TOP_LEFT),
                    (GRID_TOP + offset, GRID_LEFT),
                )
            )
            lines.append(
                Splat(
                    Rect(GRID_LINE_THICKNESS, line_color, GRID_SIZE + GRID_LINE_THICKNESS, CoordinatePlacing.TOP_LEFT),
                    (GRID_TOP, GRID_LEFT + offset),
                )
            )
        return lines


def run(driver: CatchingMiceProblem) -> None:
    render_main(
        CatchingMice(driver),
        size=SCREEN_SIZE,
        fps=2,
        title="Grid robot catching mice",
        background_color=RGB(21, 24, 31),
        interpolating_factor=70,
    )
