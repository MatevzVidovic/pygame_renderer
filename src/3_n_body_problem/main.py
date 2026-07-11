from __future__ import annotations

import numpy as np

from core.renderer import Elipse, ObjectTree, Rect, Splat, VisualProgram, main


SCREEN_SIZE = 800
BALL_RADIUS_FACTOR = 0.03
FPS = 120
# NUM_OF_BALLS = 5


class NBodyProblem(VisualProgram):
    def __init__(self) -> None:
        self.masses = np.array(
            [
                100,
                1,
            ]
        )
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
        # We are doing a 2d version of gravity for planets that are in 2d plane intially and therefore never leave it.
        # Since the planets are 3d, their volume grows with 3rd power of the radius.
        # We presume all planets to have the same density.
        # Therefore we use the 3rd root of the mass to get their radius (which we then scale with constant).
        self.unit_coordinate_radiuses = [BALL_RADIUS_FACTOR * np.cbrt(m) for m in self.masses]
        self.balls = [Elipse(SCREEN_SIZE * 2 * r, (79, 209, 197)) for r in self.unit_coordinate_radiuses]

    def step(self) -> None:
        time_step = 1 / FPS
        self.positions += self.velocities * time_step

        for point, velocity, radius in zip(self.positions, self.velocities, self.unit_coordinate_radiuses):
            if point[0] - radius < 0 or point[0] + radius > 1:
                velocity[0] *= -1
            if point[1] - radius < 0 or point[1] + radius > 1:
                velocity[1] *= -1

    def get_object_tree(self) -> ObjectTree:
        screen_positions = self.positions * SCREEN_SIZE
        return [[Splat(self.balls[i], screen_positions[i]) for i in range(np.size(screen_positions, 0))]]


def run() -> None:
    visual: VisualProgram = NBodyProblem()
    main(visual, size=(SCREEN_SIZE, SCREEN_SIZE), fps=FPS, title="N-Body Problem")


if __name__ == "__main__":
    run()
