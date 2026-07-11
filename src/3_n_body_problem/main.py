from __future__ import annotations

import numpy as np

from core.renderer import Elipse, ObjectTree, Rect, Splat, VisualProgram, main


# NUM_OF_BALLS = 5
BALL_RADIUS_FACTOR = 0.03
# VISUAL_SCALING_AID = lambda m: 1 / np.log(m + 1) # doesnt work - makes large objects smaller than small objects
VISUAL_SCALING_AID = lambda m: 1 - np.e ** (-m)
# VISUAL_SCALING_AID = lambda m: 1
FPS = 12

SCREEN_SIZE = 800
G = 0.001


class NBodyProblem(VisualProgram):
    def __init__(self) -> None:
        self.masses = np.array(
            [
                10000,
                1,
            ]
        )
        self.positions = np.array(
            [
                [0.5, 0.5],
                [0.7, 0.5],
            ]
        )
        self.velocities = np.array(
            [
                [0.0003, 0.0002],
                [0.02, 0.01],
            ]
        )
        # We are doing a 2d version of gravity for planets that are in 2d plane intially and therefore never leave it.
        # Since the planets are 3d, their volume grows with 3rd power of the radius.
        # We presume all planets to have the same density.
        # Therefore we use the 3rd root of the mass to get their radius (which we then scale with constant).
        # But
        # Since we want supermassive objects in the centre (like the sun or black hole),
        # if we want the largest object to fit on screen, we would need to make the constants very small.
        # So we need to add another scaling fn that will make very large objects reasonably smaller.
        # So we add an fn as a parameter that will help with visual scaling.
        # (To make that fn easier to construct, we suggest you follow the rule:
        # the smallest object we have has mass 1).
        self.unit_coordinate_radiuses = [BALL_RADIUS_FACTOR * np.cbrt(m) * VISUAL_SCALING_AID(m) for m in self.masses]
        self.balls = [Elipse(SCREEN_SIZE * 2 * r, (79, 209, 197)) for r in self.unit_coordinate_radiuses]

    def step(self) -> None:

        forces = np.zeros_like(self.velocities)
        # print("start")
        for ix in range(len(self.masses)):
            directions = self.positions - self.positions[ix]
            distances = np.linalg.norm(directions, axis=1).reshape(-1, 1)
            unit_directions = directions / distances
            forces_on_object = (G * self.masses * self.masses[ix] / (distances**2)) * unit_directions
            # print(f"{forces_on_object=}")
            # forces_on_object = np.delete(forces_on_object, ix, axis=0)  # to remove the nan self-force
            forces[ix] = np.nansum(forces_on_object, axis=0)  # skips nan vals, including the bogus self-force
            # print(f"{directions=}")
            # print(f"{distances=}")
            # print(f"{unit_directions=}")
            # print(f"{forces_on_object=}")
        # print(forces)
        accelerations = forces / self.masses
        self.velocities += accelerations

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
