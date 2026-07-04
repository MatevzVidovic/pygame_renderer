from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Protocol, TypeAlias

import pygame

Color: TypeAlias = tuple[int, int, int] | tuple[int, int, int, int]
Position: TypeAlias = Iterable[float]


class CoordinatePlacing(Enum):
    CENTER = auto()
    TOP_LEFT = auto()


class Rect:
    def __init__(
        self,
        width: float,
        color: Color,
        height: float | None = None,
        coordinate_placing: CoordinatePlacing = CoordinatePlacing.CENTER,
    ) -> None:
        self.width = width
        self.height = width if height is None else height
        self.color = color
        self.coordinate_placing = coordinate_placing

    def scale(self, scaling_factor: float) -> Rect:
        _validate_scaling_factor(scaling_factor)
        return Rect(
            self.width * scaling_factor,
            self.color,
            self.height * scaling_factor,
            self.coordinate_placing,
        )


class Elipse:
    def __init__(
        self,
        width: float,
        color: Color,
        height: float | None = None,
        coordinate_placing: CoordinatePlacing = CoordinatePlacing.CENTER,
    ) -> None:
        self.width = width
        self.height = width if height is None else height
        self.color = color
        self.coordinate_placing = coordinate_placing

    def scale(self, scaling_factor: float) -> Elipse:
        _validate_scaling_factor(scaling_factor)
        return Elipse(
            self.width * scaling_factor,
            self.color,
            self.height * scaling_factor,
            self.coordinate_placing,
        )


class ImgRect:
    def __init__(
        self,
        path: str | Path,
        width: float,
        height: float | None = None,
        coordinate_placing: CoordinatePlacing = CoordinatePlacing.CENTER,
    ) -> None:
        loaded_image = pygame.image.load(str(path))
        original_width, original_height = loaded_image.get_size()

        self.width = width
        self.height = (
            width * original_height / original_width if height is None else height
        )
        self.coordinate_placing = coordinate_placing
        self.image = pygame.transform.smoothscale(
            loaded_image,
            (int(self.width), int(self.height)),
        )

    def scale(self, scaling_factor: float) -> ImgRect:
        _validate_scaling_factor(scaling_factor)
        scaled = object.__new__(ImgRect)
        scaled.width = self.width * scaling_factor
        scaled.height = self.height * scaling_factor
        scaled.coordinate_placing = self.coordinate_placing
        scaled.image = pygame.transform.smoothscale(
            self.image,
            (int(scaled.width), int(scaled.height)),
        )
        return scaled


Asset: TypeAlias = Rect | Elipse | ImgRect


@dataclass(frozen=True)
class Splat:
    asset: Asset
    pos: Position


ObjectTree: TypeAlias = Splat | Sequence["ObjectTree"]


class VisualProgram(Protocol):
    def step(self) -> None:
        pass

    def get_object_tree(self) -> ObjectTree:
        pass


def render_object_tree(
    surface: pygame.Surface,
    object_tree: ObjectTree,
    background_color: Color = (20, 20, 24),
) -> None:
    surface.fill(background_color)
    _render_node(surface, object_tree)


def _render_node(surface: pygame.Surface, node: ObjectTree) -> None:
    if isinstance(node, Splat):
        _render_splat(surface, node)
        return

    for child in node:
        _render_node(surface, child)


def _render_splat(surface: pygame.Surface, splat: Splat) -> None:
    y, x = splat.pos
    asset = splat.asset
    draw_x, draw_y = _top_left(asset, x, y)
    rect = pygame.Rect(draw_x, draw_y, asset.width, asset.height)

    if isinstance(asset, Rect):
        pygame.draw.rect(surface, asset.color, rect)
    elif isinstance(asset, Elipse):
        pygame.draw.ellipse(surface, asset.color, rect)
    else:
        surface.blit(asset.image, rect)


def _top_left(asset: Asset, x: float, y: float) -> tuple[float, float]:
    if asset.coordinate_placing is CoordinatePlacing.TOP_LEFT:
        return x, y

    return x - asset.width / 2, y - asset.height / 2


def _validate_scaling_factor(scaling_factor: float) -> None:
    if scaling_factor <= 0:
        raise ValueError("scaling_factor must be greater than 0")


def main(
    program: VisualProgram,
    *,
    size: tuple[int, int] = (800, 600),
    fps: int = 60,
    title: str = "pygame renderer",
    background_color: Color = (20, 20, 24),
) -> None:
    pygame.init()
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption(title)
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        program.step()
        render_object_tree(screen, program.get_object_tree(), background_color)

        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()
