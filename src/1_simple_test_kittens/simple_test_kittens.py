from __future__ import annotations

from math import ceil
from pathlib import Path
from typing import Literal

import numpy as np
import pygame

from core.renderer import (
    CoordinatePlacing,
    Elipse,
    ImgRect,
    ObjectTree,
    RGB,
    Rect,
    Splat,
    VisualProgram,
    main,
)


SCREEN_SIZE = (800, 600)
KITTEN_PATH = Path("src/1_simple_test_kittens/assets/kitten.png")


def image_tiling(
    image_path: str | Path,
    screen_size: tuple[int, int],
    *,
    fit: Literal["x", "y"],
    num: int,
) -> ObjectTree:
    if num <= 0:
        raise ValueError("num must be greater than 0")

    screen_width, screen_height = screen_size
    image_width, image_height = pygame.image.load(str(image_path)).get_size()

    if fit == "x":
        tile_width = screen_width / num
        tile_height = tile_width * image_height / image_width
    elif fit == "y":
        tile_height = screen_height / num
        tile_width = tile_height * image_width / image_height
    else:
        raise ValueError('fit must be "x" or "y"')

    tile = ImgRect(
        image_path,
        tile_width,
        tile_height,
        CoordinatePlacing.TOP_LEFT,
    )
    rows = ceil(screen_height / tile_height)
    cols = ceil(screen_width / tile_width)

    return [
        Splat(tile, (row * tile_height, col * tile_width))
        for row in range(rows)
        for col in range(cols)
    ]


class SimpleVisual(VisualProgram):
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

        self.background = image_tiling(KITTEN_PATH, SCREEN_SIZE, fit="x", num=8)
        self.ball = Elipse(72, RGB(79, 209, 197))
        self.highlight = Elipse(18, RGB(230, 250, 255))

    def step(self) -> None:
        self.positions += self.velocities

        for point, velocity in zip(self.positions, self.velocities):
            radius = 36
            if point[0] - radius < 0 or point[0] + radius > self.height:
                velocity[0] *= -1
            if point[1] - radius < 0 or point[1] + radius > self.width:
                velocity[1] *= -1

    def get_object_tree(self) -> ObjectTree:
        return [
            self.background,
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
