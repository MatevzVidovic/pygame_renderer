from __future__ import annotations

import numpy as np

from core.renderer import Elipse, ObjectTree, Rect, Splat, VisualProgram, main

SCREEN_SIZE = (800, 600)
BALL_RADIUS = 4
NUM_OF_BALLS = 5


class FarmingRobot(VisualProgram):
    def __init__(self) -> None:
        self.width, self.height = SCREEN_SIZE
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

        self.ball = Elipse(2 * BALL_RADIUS, (79, 209, 197))

    def step(self) -> None:
        self.positions += self.velocities

        for point, velocity in zip(self.positions, self.velocities):
            if point[0] - BALL_RADIUS < 0 or point[0] + BALL_RADIUS > self.height:
                velocity[0] *= -1
            if point[1] - BALL_RADIUS < 0 or point[1] + BALL_RADIUS > self.width:
                velocity[1] *= -1

    def get_object_tree(self) -> ObjectTree:
        self.positions
        return [[Splat(self.ball, self.positions[i]) for i in range(np.size(self.positions, 0))]]


def run() -> None:
    visual: VisualProgram = FarmingRobot()
    main(visual, size=SCREEN_SIZE, title="Farming Robot")


if __name__ == "__main__":
    run()
