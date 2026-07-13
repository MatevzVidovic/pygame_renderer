from __future__ import annotations

import numpy as np

from core.renderer import (
    CoordinatePlacing,
    ObjectTree,
    PerspectiveWarp,
    RGB,
    Rect,
    Splat,
    VisualProgram,
    main,
)

SCREEN_SIZE = (720, 720)
GRID_DIM = 8
GRID_SIZE = 640
GRID_TOP = 40
GRID_LEFT = 40
CELL_SIZE = GRID_SIZE / GRID_DIM
GRID_LINE_THICKNESS = 2
BLOCK_ID = "moving-block"


def sticky_stop(t: float | np.ndarray) -> float | np.ndarray:
    t = np.asarray(t)
    smooth = t * t * (3 - 2 * t)
    shake = 0.8 * np.sin(5 * np.pi * t) * t * t * (1 - t)
    return smooth + shake


class InterpolationTest(VisualProgram):
    def __init__(self) -> None:
        self.rng = np.random.default_rng()
        self.cell = np.array([3, 3])
        self.position = self._cell_center(self.cell)
        self.background = Rect(
            SCREEN_SIZE[0],
            RGB(21, 24, 31),
            SCREEN_SIZE[1],
            CoordinatePlacing.TOP_LEFT,
        )
        self.block = Rect(CELL_SIZE * 0.68, RGB(242, 116, 87), CELL_SIZE * 0.68)
        self.grid_lines = self._make_grid_lines()

    def step(self) -> None:
        next_cell = self.cell
        while np.array_equal(next_cell, self.cell):
            next_cell = self.rng.integers(0, GRID_DIM, size=2)

        self.cell = next_cell
        self.position = self._cell_center(self.cell)

    def get_object_tree(self) -> ObjectTree:
        return [
            Splat(self.background, (0, 0)),
            Splat(
                self.block,
                self.position,
                id=BLOCK_ID,
                interpolating_fn=sticky_stop,
            ),
            self.grid_lines,
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
        lines = []

        for i in range(GRID_DIM + 1):
            offset = i * CELL_SIZE
            lines.append(
                Splat(
                    Rect(
                        GRID_SIZE + GRID_LINE_THICKNESS,
                        line_color,
                        GRID_LINE_THICKNESS,
                        CoordinatePlacing.TOP_LEFT,
                    ),
                    (GRID_TOP + offset, GRID_LEFT),
                )
            )
            lines.append(
                Splat(
                    Rect(
                        GRID_LINE_THICKNESS,
                        line_color,
                        GRID_SIZE + GRID_LINE_THICKNESS,
                        CoordinatePlacing.TOP_LEFT,
                    ),
                    (GRID_TOP, GRID_LEFT + offset),
                )
            )

        return lines


def run() -> None:
    visual: VisualProgram = InterpolationTest()
    main(
        visual,
        size=SCREEN_SIZE,
        fps=2,
        title="Interpolation Test",
        background_color=RGB(21, 24, 31),
        interpolating_factor=28,
        perspective_params=PerspectiveWarp(
            SCREEN_SIZE,
            horizon=0.0,
            depth=1.00001,
            background=(21, 24, 31),
        ),
    )


if __name__ == "__main__":
    run()
