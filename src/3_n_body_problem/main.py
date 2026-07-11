from __future__ import annotations

import numpy as np

from core.renderer import Elipse, ObjectTree, Rect, Splat, VisualProgram, main


SCREEN_SIZE = 800
BALL_RADIUS = 0.03
# NUM_OF_BALLS = 5


class NBodyProblem(VisualProgram):
    def __init__(self) -> None:
        self.positions = np.array(
            [
                [0.5, 0.7],
                [0.7, 0.5],
            ]
        )
        self.velocities = np.array(
            [
                [0.03, 0.02],
                [0.02, 0.01],
            ]
        )

        self.ball = Elipse(2 * BALL_RADIUS * SCREEN_SIZE, (79, 209, 197))

    def step(self) -> None:
        self.positions += self.velocities

        for point, velocity in zip(self.positions, self.velocities):
            if point[0] - BALL_RADIUS < 0 or point[0] + BALL_RADIUS > 1:
                velocity[0] *= -1
            if point[1] - BALL_RADIUS < 0 or point[1] + BALL_RADIUS > 1:
                velocity[1] *= -1

    def get_object_tree(self) -> ObjectTree:
        screen_positions = self.positions * SCREEN_SIZE
        print(screen_positions)
        return [[Splat(self.ball, screen_positions[i]) for i in range(np.size(screen_positions, 0))]]


def run() -> None:
    visual: VisualProgram = NBodyProblem()
    main(visual, size=(SCREEN_SIZE, SCREEN_SIZE), title="N-Body Problem")


if __name__ == "__main__":
    run()
