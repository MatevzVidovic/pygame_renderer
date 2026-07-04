from __future__ import annotations

import numpy as np

from core.renderer import Elipse, ObjectTree, RGB, Rect, Splat, VisualProgram, main

SCREEN_SIZE = (800, 600)

class SimpleVisual(VisualProgram):
    def __init__(self) -> None:
        self.positions = np.array(
            [
                [300.0, 400.0],
                [250.0, 360.0],
            ]
        )
        self.velocities = np.array(
            [
                [2.5, 3.0],
                [1.7, -2.3],
            ]
        )

        self.background = Rect(800, RGB(28, 30, 36), 600)
        self.frame = Rect(620, RGB(55, 62, 76), 390)
        self.ball = Elipse(72, RGB(79, 209, 197))
        self.highlight = Elipse(18, RGB(230, 250, 255))

    def step(self) -> None:
        self.positions += self.velocities

        for point, velocity in zip(self.positions, self.velocities):
            radius = 36
            if point[0] - radius < 0 or point[0] + radius > SCREEN_SIZE[1]:
                velocity[0] *= -1
            if point[1] - radius < 0 or point[1] + radius > SCREEN_SIZE[0]:
                velocity[1] *= -1

    def get_object_tree(self) -> ObjectTree:
        return [
            Splat(self.frame, (SCREEN_SIZE[1] / 2, SCREEN_SIZE[0] / 2)),
            [
                Splat(self.ball, self.positions[0]),
                Splat(self.highlight, self.positions[1]),
            ],
        ]


def run() -> None:
    visual: VisualProgram = SimpleVisual()
    main(
        visual,
        size=SCREEN_SIZE,
        background_color=RGB(20, 20, 24),
        title="simple renderer test",
    )


if __name__ == "__main__":
    run()
